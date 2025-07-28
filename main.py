import sys
from datetime import datetime
from src.models import JobSearchParameters
from src.workflow import JobSearchWorkflow

def main():
    print_banner()
    
    while True:
        try:
            # Collect search parameters
            params = collect_parameters()
            
            # Execute search workflow
            workflow = JobSearchWorkflow()
            results = workflow.run(params)
            
            # Display results
            display_results(results)
            
            if not ask_restart():
                break
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            if ask_retry():
                continue
            break

def print_banner():
    print("=" * 60)
    print("🤖 EUROPEAN AI JOB SEARCH AGENT".center(60))
    print("Find AI/ML Roles Across Europe".center(60))
    print("=" * 60)
    print("\n")

def collect_parameters() -> JobSearchParameters:
    """Collect search parameters from user input"""
    print("🔍 Configure Your Search (press Enter for defaults)")
    print("-" * 50)
    
    keywords = input("Keywords (comma separated, e.g., AI,ML,LLM): ").strip()
    locations = input("Locations (comma separated, e.g., Berlin,Remote): ").strip()
    experience = input("Experience (Junior/Mid/Senior, comma separated): ").strip()
    skills = input("Required Skills (comma separated, e.g., Python,PyTorch): ").strip()
    min_salary = input("Minimum Salary (EUR, e.g., 70000): ").strip()
    visa_needed = input("Require Visa Sponsorship? (y/N): ").strip().lower() == 'y'
    
    # Set default values if empty
    keywords = keywords.split(",") if keywords else ["AI", "Machine Learning"]
    locations = locations.split(",") if locations else ["Europe"]
    experience = experience.split(",") if experience else ["Mid", "Senior"]
    skills = skills.split(",") if skills else ["Python", "TensorFlow"]
    
    # Remove all salary_range related code, including parameter, print statements, and logic
    
    return JobSearchParameters(
        keywords=keywords,
        locations=locations,
        experience_level=experience,
        required_skills=skills,
        visa_sponsorship=visa_needed
    )

def display_results(state):
    """Display search results in a user-friendly format"""
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {len(state.processed_listings)} AI Jobs Found")
    print("=" * 60)
    
    if not state.processed_listings:
        print("\n🚫 No matching AI jobs found. Try different parameters.")
        return
    
    # Print metrics summary
    metrics = state.metrics
    print(f"\n🔍 Found {metrics.get('total_found', 0)} jobs, " 
          f"{metrics.get('ai_relevant', 0)} are AI-relevant")
    print(f"🌍 Platforms: {', '.join(state.parameters.preferred_platforms)}")
    
    # Print each job listing
    for i, job in enumerate(state.processed_listings, 1):
        print("\n" + "-" * 60)
        print(f"{i}. 🚀 {job.title}")
        print(f"   🏢 {job.company.name} | 📍 {job.location}")
        
        # Experience and type
        print(f"   🎯 {job.experience_level} | 🕒 {job.job_type}")
        
        # Visa and remote status
        visa_status = "✅ Visa Support" if job.visa_sponsorship else "❌ No Visa"
        remote_status = "🏠 " + job.remote_policy
        print(f"   {visa_status} | {remote_status}")
        
        # Skills and AI focus
        if job.required_skills:
            print(f"   ⚙️  Skills: {', '.join(job.required_skills[:5])}")
        if job.ai_focus_areas:
            print(f"   🤖 AI Focus: {', '.join(job.ai_focus_areas)}")
        
        # Job source and freshness
        days_old = (datetime.now() - job.posted_date).days
        freshness = "🆕 Today" if days_old == 0 else f"📅 {days_old}d ago"
        print(f"   🔗 Apply: {job.application_url}")
        print(f"   {freshness} | 📱 Source: {job.source}")
    
    # Display market insights
    if state.analysis:
        print("\n" + "=" * 60)
        print("📈 EUROPEAN AI JOB MARKET INSIGHTS")
        print("=" * 60)
        print(state.analysis)
    
    # Show additional metrics
    print("\n" + "=" * 60)
    print(f"⏱️  Search completed at {datetime.now().strftime('%H:%M:%S')}")
    print(f"ℹ️  Found {len(state.processed_listings)} relevant AI positions")

def ask_restart() -> bool:
    """Ask user if they want to perform another search"""
    response = input("\n🔍 Perform another search? (y/N): ").strip().lower()
    return response == 'y'

def ask_retry() -> bool:
    """Ask user if they want to retry after an error"""
    response = input("\n🔄 Retry with same parameters? (y/N): ").strip().lower()
    return response == 'y'

if __name__ == "__main__":
    main()