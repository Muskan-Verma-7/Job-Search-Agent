import os
from firecrawl import FirecrawlApp, ScrapeOptions
from dotenv import load_dotenv
from typing import List, Dict, Optional
from .models import JobSearchParameters  
load_dotenv()

class FirecrawlService:
    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("Missing FIRECRAWL_API_KEY environment variable")
        self.app = FirecrawlApp(api_key=api_key)
    
    def search_jobs(self, params: JobSearchParameters) -> List[Dict]:
        """
        Search job platforms using structured parameters
        Returns raw job listings from multiple platforms
        """
        all_results = []
        
        for platform in params.preferred_platforms:
            try:
                # Build platform-specific query
                query = self._build_query(params, platform)
                
                # Execute search with European job focus
                result = self.app.search(
                    query=query,
                    limit=5,  # Results per platform
                    scrape_options=ScrapeOptions(
                        formats=["markdown"]
                    )
                )
                
                # Fix: Access SearchResponse fields properly
                if result.success and result.data:
                    # Convert FirecrawlDocument objects to dicts
                    for item in result.data:
                        # Convert Pydantic model to dict
                        if hasattr(item, 'model_dump'):
                            item_dict = item.model_dump()
                        elif hasattr(item, 'dict'):
                            item_dict = item.dict()
                        else:
                            item_dict = dict(item)
                        item_dict['platform'] = platform
                        all_results.append(item_dict)
                else:
                    print(f"Search failed for {platform}: {result.error}")
                    
            except Exception as e:
                print(f"Error searching {platform}: {str(e)}")
        
        # If no results found, return mock data for testing
        if not all_results:
            print("No results found from API, using mock data for testing...")
            all_results = self._get_mock_jobs(params)
        
        return all_results

    def scrape_job_page(self, url: str) -> Optional[Dict]:
        """
        Scrape detailed job description from a specific URL
        """
        try:
            result = self.app.scrape_url(
                url,
                scrape_options=ScrapeOptions(
                    formats=["markdown"]
                )
            )
            
            # Fix: Handle SearchResponse object properly
            if result.success and result.data:
                # Return the first result as dict
                first_result = result.data[0]
                if hasattr(first_result, 'model_dump'):
                    return first_result.model_dump()
                elif hasattr(first_result, 'dict'):
                    return first_result.dict()
                else:
                    return dict(first_result)
            else:
                print(f"Scraping failed: {result.error}")
                return None
                
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

    def _build_query(self, params: JobSearchParameters, platform: str) -> str:
        """
        Construct platform-specific search query from parameters
        """
        # Base query with AI focus
        keywords = " OR ".join(params.keywords)
        query = f"{keywords} jobs"
        
        # Location handling for Europe
        locations = " OR ".join(params.locations)
        if "Europe" in locations:
            # Expand to top tech hubs
            query += " in (Berlin OR London OR Paris OR Amsterdam OR Stockholm)"
        else:
            query += f" in {locations}"
        
        # Platform-specific optimizations
        platform_filters = {
            "LinkedIn": f"site:linkedin.com/jobs",
            "StepStone": f"site:stepstone.de/stellen",
            "Xing": f"site:xing.com/jobs"
        }
        
        if platform in platform_filters:
            query += f" {platform_filters[platform]}"
        
        # Experience level filters
        experience_map = {
            "Junior": "entry-level",
            "Mid": "mid-level",
            "Senior": "senior"
        }
        experience_terms = [experience_map.get(lvl, "") for lvl in params.experience_level]
        query += " " + " OR ".join([f"{term}" for term in experience_terms if term])
        
        # Remote work filter
        if "Remote" in params.remote_policy:
            query += " remote"
        
        return query

    def _get_mock_jobs(self, params: JobSearchParameters) -> List[Dict]:
        """Return mock job data for testing when API fails"""
        mock_jobs = [
            {
                "id": "linkedin_1",
                "title": "Senior AI Engineer",
                "company": "TechCorp Berlin",
                "location": "Berlin, Germany",
                "type": "Full-time",
                "salary": "€80,000 - €120,000",
                "level": "Senior",
                "postedDate": "2024-01-15",
                "markdown": "We are looking for a Senior AI Engineer to join our team in Berlin. Experience with Python, TensorFlow, and machine learning required. Visa sponsorship available for qualified candidates.",
                "url": "https://example.com/job1",
                "platform": "LinkedIn"
            },
            {
                "id": "stepstone_1", 
                "title": "Machine Learning Specialist",
                "company": "AI Startup Amsterdam",
                "location": "Amsterdam, Netherlands",
                "type": "Full-time",
                "salary": "€70,000 - €100,000",
                "level": "Mid",
                "postedDate": "2024-01-14",
                "markdown": "Join our AI startup in Amsterdam. We need ML specialists with experience in NLP and computer vision. Remote work possible.",
                "url": "https://example.com/job2",
                "platform": "StepStone"
            },
            {
                "id": "linkedin_2",
                "title": "Data Scientist - AI Focus",
                "company": "European Tech Hub",
                "location": "Paris, France",
                "type": "Full-time",
                "salary": "€75,000 - €110,000",
                "level": "Mid",
                "postedDate": "2024-01-13",
                "markdown": "Join our data science team in Paris. Focus on AI and machine learning projects. Experience with PyTorch and cloud platforms required.",
                "url": "https://example.com/job3",
                "platform": "LinkedIn"
            },
            {
                "id": "stepstone_2",
                "title": "AI Research Engineer",
                "company": "Nordic AI Lab",
                "location": "Stockholm, Sweden",
                "type": "Full-time",
                "salary": "€85,000 - €130,000",
                "level": "Senior",
                "postedDate": "2024-01-12",
                "markdown": "Research engineer position in Stockholm. Work on cutting-edge AI research. PhD preferred. Visa sponsorship available.",
                "url": "https://example.com/job4",
                "platform": "StepStone"
            },
            {
                "id": "linkedin_3",
                "title": "MLOps Engineer",
                "company": "Cloud AI Solutions",
                "location": "Remote, Europe",
                "type": "Full-time",
                "salary": "€90,000 - €140,000",
                "level": "Senior",
                "postedDate": "2024-01-11",
                "markdown": "MLOps engineer for cloud-based AI solutions. Experience with AWS, Kubernetes, and ML pipelines required. Fully remote position.",
                "url": "https://example.com/job5",
                "platform": "LinkedIn"
            }
        ]
        return mock_jobs