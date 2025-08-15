#!/usr/bin/env python3
"""
Test script for LinkedIn job search functionality
"""

from linkedin_scraper import LinkedInScraper, JobSearchRequest

def test_job_search():
    """Test the job search functionality"""
    print("🔍 Testing LinkedIn Job Search...")
    
    # Create a job search request
    request = JobSearchRequest(
        skills=["Python", "JavaScript"],
        location="San Francisco, CA",
        limit=5
    )
    
    print(f"Searching for jobs with skills: {request.skills}")
    print(f"Location: {request.location}")
    print(f"Limit: {request.limit}")
    print()
    
    # Create scraper instance
    scraper = LinkedInScraper(headless=True)
    
    try:
        # Perform job search
        print("⏳ Searching for jobs...")
        result = scraper.search_jobs(request)
        
        if result.success:
            print(f"✅ Found {len(result.jobs)} jobs!")
            print()
            
            for i, job in enumerate(result.jobs, 1):
                print(f"{i}. {job.title}")
                print(f"   Company: {job.company}")
                print(f"   Location: {job.location}")
                if job.skills_matched:
                    print(f"   Skills matched: {', '.join(job.skills_matched)}")
                print()
        else:
            print(f"❌ Job search failed: {result.message}")
            
    except Exception as e:
        print(f"❌ Error during job search: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_job_search()
