class JobSearchPrompts:
    """Prompts for job research agent focused on European AI roles"""
    
    # 1. Job Relevance Classifier
    RELEVANCE_SYSTEM = """
    You are an AI job classifier for European tech roles. Determine if a job is primarily focused on 
    AI, Machine Learning, Data Science, or related fields. Consider:
    - Job title
    - Required skills
    - Company's tech focus
    - 50% of job description content
    
    Return only: true|false
    """
    
    @staticmethod
    def relevance_user(title: str, company_tech_focus: list, description: str) -> str:
        return f"""
        Job Title: {title}
        Company Tech Focus: {', '.join(company_tech_focus)}
        Description Excerpt: {description[:1000]}
        
        Is this primarily an AI/ML role? Respond ONLY with true or false.
        """
    
    # 2. Skill Extractor
    SKILL_EXTRACTION_SYSTEM = """
    Extract technical skills from job descriptions with global context. Focus on:
    - AI/ML specific skills (LLMs, Generative AI, Prompt Engineering, etc.)
    - Programming languages
    - Cloud platforms (AWS, GCP, Azure)
    - EU-specific tools (GDPR-compliant systems)
    - Language requirements (English, German, French etc.)
    
    Categorize as REQUIRED or PREFERRED based on job description language.
    """
    
    @staticmethod
    def skill_extraction_user(description: str) -> str:
        return f"""
        Job Description:
        {description[:2000]}
        
        Extract skills in JSON format: 
        {
          "required_skills": [],
          "preferred_skills": []
        }
        """

    # 3. Visa Sponsor Detector (EU Focus)
    VISA_DETECTOR_SYSTEM = """
    Determine if job offers visa sponsorship for European countries. Key indicators:
    - "visa sponsorship" or "work permit"
    - "relocation package"
    - "support for international candidates"
    - EU Blue Card mentions
    - Company funding status (funded companies more likely)
    
    Return: true|false|null (if ambiguous)
    """
    
    @staticmethod
    def visa_detector_user(description: str, company_funding: str) -> str:
        return f"""
        Company Funding Status: {company_funding}
        Job Description Excerpt:
        {description[:1000]}
        
        Does this offer visa sponsorship? Respond ONLY with true, false, or null.
        """
    
    # 4. AI Focus Area Extractor
    FOCUS_AREA_SYSTEM = """
    Identify specific AI subfields from job descriptions. European focus areas include:
    - NLP (Multilingual focus)
    - Computer Vision
    - LLMs and Generative AI
    - EU Regulations (GDPR-compliant AI)
    - Industrial AI (Manufacturing, Automotive)
    - Healthcare AI
    - Climate/Green AI
    
    Return list of focus areas.
    """
    
    @staticmethod
    def focus_area_user(description: str) -> str:
        return f"""
        Job Description:
        {description[:1500]}
        
        Extract AI focus areas as comma-separated list.
        """
    
    # 5. Company Intel Enricher
    COMPANY_INTEL_SYSTEM = """
    Generate company insights for job seekers based on:
    - Company description
    - Tech focus
    - Employee count
    - Funding status
    - Hiring trends
    
    Focus on European tech company characteristics.
    """
    
    @staticmethod
    def company_intel_user(company: dict) -> str:
        return f"""
        Company Data:
        {company}
        
        Generate insights in 3 bullet points:
        1. Core tech focus
        2. Growth indicators
        3. EU market position
        """
    
    # 6. Salary Normalizer (EU Focus)
    SALARY_NORMALIZER_SYSTEM = """
    Normalize European salary ranges to annual EUR equivalents:
    - Handle formats: "€70,000", "70k", "£85,000", "100K CHF"
    - Convert currencies to EUR
    - Annualize monthly salaries
    - Adjust for country cost of living
    
    Return JSON: {"min": int, "max": int, "currency": "EUR"}
    """
    
    @staticmethod
    def salary_normalizer_user(raw_salary: str, country: str) -> str:
        return f"""
        Job Location Country: {country}
        Raw Salary String: "{raw_salary}"
        
        Normalize to EUR annual equivalent.
        """
    
    # 7. Market Insights Generator
    MARKET_INSIGHTS_SYSTEM = """
    Analyze European AI job market trends. Focus on:
    - In-demand skills in EU market
    - Salary benchmarks by country
    - Visa sponsorship availability
    - Remote work trends
    - Company funding vs hiring correlation
    - Emerging AI specializations
    
    Provide concise insights (max 1 paragraph).
    """
    
    @staticmethod
    def market_insights_user(jobs_data: list) -> str:
        return f"""
        Analyzed Job Data (Sample):
        {jobs_data[:5]}
        
        Generate European AI job market insights.
        """
    
    # 8. Job Ranker
    RANKING_SYSTEM = """
    Rank jobs based on candidate fit for European market. Consider:
    - Skill match (40%)
    - Salary competitiveness (25%)
    - Visa support (20% if needed)
    - Company growth potential (15%)
    
    Return relevance score (0.0-1.0) with brief justification.
    """
    
    @staticmethod
    def ranking_user(job: dict, params: dict) -> str:
        return f"""
        Candidate Requirements:
        - Skills: {params['required_skills']}
        - Visa Needed: {params['visa_sponsorship']}
        
        Job Details:
        {job}
        
        Calculate relevance score and 1-sentence justification.
        Return JSON: {"score": float, "reason": str}
        """