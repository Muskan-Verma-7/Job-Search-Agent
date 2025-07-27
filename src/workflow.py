from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .models import JobSearchState, JobSearchParameters, JobListing, CompanyInformation
from .firecrawl import FirecrawlService
from .prompts import JobSearchPrompts
import re
from datetime import datetime, timedelta

class JobSearchWorkflow:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        self.prompts = JobSearchPrompts()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for job search"""
        graph = StateGraph(JobSearchState)
        
        # Define workflow nodes
        graph.add_node("search_portals", self.search_portals_step)
        graph.add_node("process_listings", self.process_listings_step)
        graph.add_node("filter_ai_jobs", self.filter_ai_jobs_step)
        graph.add_node("enrich_jobs", self.enrich_jobs_step)
        graph.add_node("enrich_companies", self.enrich_companies_step)
        graph.add_node("generate_insights", self.generate_insights_step)
        
        # Define workflow edges
        graph.set_entry_point("search_portals")
        graph.add_edge("search_portals", "process_listings")
        graph.add_edge("process_listings", "filter_ai_jobs")
        graph.add_edge("filter_ai_jobs", "enrich_jobs")
        graph.add_edge("enrich_jobs", "enrich_companies")
        graph.add_edge("enrich_companies", "generate_insights")
        graph.add_edge("generate_insights", END)
        
        return graph.compile()
    
    def search_portals_step(self, state: JobSearchState) -> Dict[str, Any]:
        """Search job portals using Firecrawl"""
        print(f"🔍 Searching {len(state.parameters.preferred_platforms)} platforms...")
        raw_listings = self.firecrawl.search_jobs(state.parameters)
        
        # Update metrics
        metrics = state.metrics
        metrics["total_found"] = len(raw_listings)
        metrics["platform_counts"] = {
            platform: sum(1 for job in raw_listings if job.get("platform") == platform)
            for platform in state.parameters.preferred_platforms
        }
        
        print(f"📊 Found {len(raw_listings)} raw listings")
        return {"raw_listings": raw_listings, "metrics": metrics}
    
    def process_listings_step(self, state: JobSearchState) -> Dict[str, Any]:
        """Convert raw listings to structured data"""
        print(f"🛠️ Processing {len(state.raw_listings)} listings...")
        processed = []
        seen_ids = set()
        
        for raw in state.raw_listings:
            try:
                # Generate unique ID from platform + source ID
                job_id = f"{raw.get('platform', 'unknown')}_{raw.get('id', '')}"
                if job_id in seen_ids:
                    continue
                
                # Basic job listing structure
                listing = JobListing(
                    id=job_id,
                    title=raw.get("title", "No Title"),
                    company=CompanyInformation(name=raw.get("company", "Unknown Company")),
                    location=raw.get("location", ""),
                    job_type=raw.get("type", "Full-time"),
                    salary_range=raw.get("salary", ""),
                    experience_level=self._map_experience(raw.get("level", "")),
                    posted_date=self._parse_date(raw.get("postedDate", "")),
                    description=raw.get("markdown", "")[:2000],  # Truncate
                    application_url=raw.get("url", ""),
                    source=raw.get("platform", "Unknown"),
                    visa_sponsorship=False,  # Temporary default
                    remote_policy=self._detect_remote_policy(raw)
                )
                
                processed.append(listing)
                seen_ids.add(job_id)
            except Exception as e:
                print(f"Error processing listing: {e}")
        
        print(f"✅ Processed {len(processed)} listings")
        return {"processed_listings": processed}
    
    def filter_ai_jobs_step(self, state: JobSearchState) -> Dict[str, Any]:
        """Filter non-AI jobs using LLM classification"""
        print(f"🤖 Filtering AI jobs from {len(state.processed_listings)} listings...")
        ai_jobs = []
        
        for job in state.processed_listings:
            # Skip if basic AI keywords already in title
            if any(kw in job.title for kw in ["AI", "ML", "Machine Learning", "Data Science"]):
                ai_jobs.append(job)
                continue
                
            # Use LLM for ambiguous cases
            if self._is_ai_job(job):
                ai_jobs.append(job)
        
        # Update metrics
        metrics = state.metrics
        metrics["ai_relevant"] = len(ai_jobs)
        
        return {"processed_listings": ai_jobs, "metrics": metrics}
    
    def enrich_jobs_step(self, state: JobSearchState) -> Dict[str, Any]:
        """Enrich job listings with detailed information"""
        print(f"✨ Enriching {len(state.processed_listings)} jobs...")
        enriched_listings = []
        
        for job in state.processed_listings:
            try:
                # Skip scraping for mock data URLs to avoid API issues
                if job.application_url and not job.application_url.startswith("https://example.com"):
                    try:
                        scraped = self.firecrawl.scrape_job_page(job.application_url)
                        if scraped:
                            job.description = scraped.get("markdown", job.description)[:4000]
                    except Exception as scrape_error:
                        print(f"Warning: Could not scrape {job.application_url}: {scrape_error}")
                        # Continue with original description
                
                # Extract skills and AI focus areas
                job.required_skills = self._extract_skills(job.description)
                job.ai_focus_areas = self._extract_ai_focus(job.description)
                
                # Detect visa sponsorship
                job.visa_sponsorship = self._detect_visa_sponsorship(
                    job.description,
                    job.company.recent_funding or "Unknown"
                )
                
                enriched_listings.append(job)
            except Exception as e:
                print(f"Error enriching job {job.id}: {e}")
                enriched_listings.append(job)  # Keep even if enrichment fails
        
        return {"processed_listings": enriched_listings}
    
    def enrich_companies_step(self, state: JobSearchState) -> Dict[str, Any]:
        """Enrich company information using cached data or new lookup"""
        print(f"🏢 Enriching company profiles...")
        companies = state.company_profiles
        updated_companies = {}
        
        for job in state.processed_listings:
            company_name = job.company.name
            if company_name in companies:
                # Use cached company profile
                job.company = companies[company_name]
            else:
                # Basic enrichment from job data
                job.company.description = f"{company_name} - AI company"
                job.company.tech_focus = job.ai_focus_areas
                
                # Add to cache
                companies[company_name] = job.company
                updated_companies[company_name] = job.company
        
        return {"company_profiles": {**companies, **updated_companies}}
    
    def generate_insights_step(self, state: JobSearchState) -> Dict[str, Any]:
        """Generate market insights from collected data"""
        print("📊 Generating market insights...")
        
        # Prepare sample data for LLM
        sample_jobs = [job.dict() for job in state.processed_listings[:5]]
        
        # Generate insights using LLM
        messages = [
            SystemMessage(content=self.prompts.MARKET_INSIGHTS_SYSTEM),
            HumanMessage(content=self.prompts.market_insights_user(sample_jobs))
        ]
        
        try:
            response = self.llm.invoke(messages)
            insights = response.content
        except Exception as e:
            print(f"Error generating insights: {e}")
            insights = "Market analysis unavailable"
        
        return {"analysis": insights}
    
    def run(self, parameters: JobSearchParameters) -> JobSearchState:
        """Execute the workflow"""
        initial_state = JobSearchState(parameters=parameters)
        
        # Fix: Properly handle the workflow execution
        try:
            final_state = self.workflow.invoke(initial_state)
            
            # Ensure we have a proper JobSearchState object
            if isinstance(final_state, dict):
                # Convert dict back to JobSearchState
                return JobSearchState(**final_state)
            else:
                return final_state
                
        except Exception as e:
            print(f"Workflow error: {e}")
            print("Falling back to direct execution...")
            return self._run_direct(parameters)
    
    def _run_direct(self, parameters: JobSearchParameters) -> JobSearchState:
        """Direct execution without LangGraph workflow"""
        state = JobSearchState(parameters=parameters)
        
        # Execute steps directly
        try:
            # Step 1: Search portals
            search_result = self.search_portals_step(state)
            state.raw_listings = search_result.get("raw_listings", [])
            state.metrics.update(search_result.get("metrics", {}))
            
            # Step 2: Process listings
            process_result = self.process_listings_step(state)
            state.processed_listings = process_result.get("processed_listings", [])
            
            # Step 3: Filter AI jobs
            filter_result = self.filter_ai_jobs_step(state)
            state.processed_listings = filter_result.get("processed_listings", [])
            state.metrics.update(filter_result.get("metrics", {}))
            
            # Step 4: Enrich jobs
            enrich_result = self.enrich_jobs_step(state)
            state.processed_listings = enrich_result.get("processed_listings", [])
            
            # Step 5: Enrich companies
            company_result = self.enrich_companies_step(state)
            state.company_profiles.update(company_result.get("company_profiles", {}))
            
            # Step 6: Generate insights
            insights_result = self.generate_insights_step(state)
            state.analysis = insights_result.get("analysis", "")
            
        except Exception as e:
            print(f"Direct execution error: {e}")
            state.analysis = f"Execution failed: {str(e)}"
        
        return state
    
    # Helper methods ----------------------------------------------------------
    
    def _is_ai_job(self, job: JobListing) -> bool:
        """LLM-powered AI job classification"""
        messages = [
            SystemMessage(content=self.prompts.RELEVANCE_SYSTEM),
            HumanMessage(content=self.prompts.relevance_user(
                job.title,
                job.company.tech_focus,
                job.description
            ))
        ]
        response = self.llm.invoke(messages).content.strip()
        return response.lower() == "true"
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description"""
        try:
            messages = [
                SystemMessage(content=self.prompts.SKILL_EXTRACTION_SYSTEM),
                HumanMessage(content=self.prompts.skill_extraction_user(description))
            ]
            response = self.llm.invoke(messages).content
            
            # Extract skills from JSON-like response more safely
            if "required_skills" in response:
                # Try to extract JSON-like structure
                import re
                import json
                
                # Look for JSON pattern
                json_match = re.search(r'\{[^}]*"required_skills"[^}]*\}', response)
                if json_match:
                    try:
                        skills_data = json.loads(json_match.group())
                        return skills_data.get("required_skills", [])
                    except json.JSONDecodeError:
                        pass
                
                # Fallback: extract skills from text
                skills = []
                skill_keywords = ["Python", "TensorFlow", "PyTorch", "Machine Learning", "AI", "NLP", "Computer Vision"]
                for skill in skill_keywords:
                    if skill.lower() in description.lower():
                        skills.append(skill)
                return skills
        except Exception as e:
            print(f"Error extracting skills: {e}")
            # Fallback: simple keyword extraction
            skills = []
            skill_keywords = ["Python", "TensorFlow", "PyTorch", "Machine Learning", "AI", "NLP", "Computer Vision"]
            for skill in skill_keywords:
                if skill.lower() in description.lower():
                    skills.append(skill)
            return skills
        return []
    
    def _extract_ai_focus(self, description: str) -> List[str]:
        """Identify AI specialization areas"""
        messages = [
            SystemMessage(content=self.prompts.FOCUS_AREA_SYSTEM),
            HumanMessage(content=self.prompts.focus_area_user(description))
        ]
        try:
            response = self.llm.invoke(messages).content
            return [area.strip() for area in response.split(",") if area.strip()]
        except:
            return []
    
    def _detect_visa_sponsorship(self, description: str, funding: str) -> bool:
        """Detect visa sponsorship availability"""
        messages = [
            SystemMessage(content=self.prompts.VISA_DETECTOR_SYSTEM),
            HumanMessage(content=self.prompts.visa_detector_user(description, funding))
        ]
        response = self.llm.invoke(messages).content.strip().lower()
        return response == "true"
    
    def _map_experience(self, level: str) -> str:
        """Normalize experience levels"""
        level = level.lower()
        if "senior" in level: return "Senior"
        if "mid" in level or "experienced" in level: return "Mid"
        if "junior" in level or "entry" in level: return "Junior"
        return "Not Specified"
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats"""
        try:
            # Handle relative dates ("2 days ago")
            if "ago" in date_str:
                days = int(re.search(r'\d+', date_str).group())
                return datetime.now() - timedelta(days=days)
            
            # Handle absolute dates
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return datetime.now() - timedelta(days=30)  # Default to 30 days ago
    
    def _detect_remote_policy(self, raw: dict) -> str:
        """Detect remote work policy"""
        location = raw.get("location", "").lower()
        if "remote" in location: return "Remote"
        if "hybrid" in location: return "Hybrid"
        return "On-site"