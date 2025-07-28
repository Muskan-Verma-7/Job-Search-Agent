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
                    scrape_options={"formats": ["markdown"]}
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
        
        # If no results found, return an empty list or handle as needed
        if not all_results:
            print("No results found from API.")
            # Optionally: raise an error, return [], or handle as you wish
            # For example:
            # raise RuntimeError("No job results found from API.")
        
        return all_results

    def scrape_job_page(self, url: str) -> Optional[Dict]:
        """
        Scrape detailed job description from a specific URL
        """
        try:
            result = self.app.scrape_url(
                url,
                scrape_options={"formats": ["markdown"]}
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

    