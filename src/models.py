from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel
from datetime import datetime

class JobSearchParameters(BaseModel):
    keywords: List[str] = ["AI", "Machine Learning", "Prompt", "LLM", "Generative AI"]
    locations: List[str] = ["Europe"]  # Default to Europe-wide search
    experience_level: List[str] = ["Entry", "Mid", "Senior"]  
    employment_type: List[str] = ["Full-time", "Contract"]
    remote_policy: List[str] = ["Remote", "Hybrid"]
    required_skills: List[str] = ["Python", "TensorFlow"]
    preferred_platforms: List[str] = ["LinkedIn", "StepStone"]


class CompanyInformation(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[str] = None
    tech_focus: List[str] = []  # e.g., ["AI", "Cloud Computing"]
    company_rating: Optional[float] = None  # From review platforms
    hiring_trends: List[str] = []  # e.g., ["Growing", "Stable"]
    glassdoor_rating: Optional[float] = None
    recent_funding: Optional[str] = None  # e.g., "Series B - €20M"


class JobListing(BaseModel):
    id: str  # Unique identifier
    title: str
    company: CompanyInformation  # Embedded company info
    location: str
    job_type: str
    experience_level: str
    posted_date: datetime
    application_deadline: Optional[datetime] = None
    description: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    ai_focus_areas: List[str] = []  # NLP, Computer Vision, etc.
    visa_sponsorship: bool
    remote_policy: str
    application_url: str
    source: str  # LinkedIn, StepStone, etc.
    recruiter_contact: Optional[str] = None  # For direct applications


class JobSearchState(BaseModel):
    parameters: JobSearchParameters
    raw_listings: List[Dict] = []  # Raw data from platforms
    processed_listings: List[JobListing] = []
    company_profiles: Dict[str, CompanyInformation] = {}  # Company cache
    analysis: Optional[str] = None
    metrics: Dict[str, Any] = {
        "total_found": 0,
        "ai_relevant": 0,
        "platform_counts": {}
    }

