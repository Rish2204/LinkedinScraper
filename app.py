#!/usr/bin/env python3
"""
LinkedIn Scraper FastAPI Application
Standalone FastAPI server for LinkedIn job scraping functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

# Import the moved LinkedIn components
from linkedin_scraper import LinkedInJobScraper
from linkedin import JobSearchRequest, JobSearchResponse, ScrapingStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LinkedIn Scraper API",
    description="API for scraping LinkedIn job listings and profiles",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scraper
linkedin_scraper = LinkedInJobScraper()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LinkedIn Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "job_search": "/linkedin/search",
            "status": "/linkedin/status",
            "help": "/linkedin/help"
        }
    }

@app.post("/linkedin/search", response_model=JobSearchResponse)
async def search_linkedin_jobs(search_request: JobSearchRequest) -> JobSearchResponse:
    """
    Search for jobs on LinkedIn based on skillset and other criteria.
    
    This endpoint allows you to search for job opportunities on LinkedIn
    by providing skills, location, experience level, and other filters.
    """
    try:
        logger.info(f"Starting LinkedIn job search for skills: {search_request.skills}")
        
        # Validate request
        if not search_request.skills:
            raise HTTPException(status_code=400, detail="At least one skill is required")
        
        # Perform job search
        result = await linkedin_scraper.search_jobs(search_request)
        
        logger.info(f"LinkedIn job search completed. Found {len(result.jobs)} jobs")
        return result
        
    except Exception as e:
        logger.error(f"LinkedIn job search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")

@app.get("/linkedin/status")
async def get_linkedin_status():
    """
    Get the current status of the LinkedIn scraping service.
    
    Returns information about the scraper's health and configuration.
    """
    try:
        status_info = linkedin_scraper.get_scraping_status()
        return JSONResponse(content=status_info)
    except Exception as e:
        logger.error(f"Failed to get LinkedIn status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.get("/linkedin/help")
async def get_linkedin_help():
    """
    Get help information for using the LinkedIn job scraping endpoints.
    
    Returns detailed information about how to use the LinkedIn job search functionality.
    """
    return {
        "description": "LinkedIn Job Scraping API",
        "endpoints": {
            "POST /linkedin/search": {
                "description": "Search for jobs on LinkedIn",
                "request_body": {
                    "skills": ["Python", "JavaScript"],
                    "location": "San Francisco, CA",
                    "experience_level": "mid_senior",
                    "job_type": "full_time",
                    "company": "Google",
                    "limit": 10
                },
                "response": {
                    "success": True,
                    "total_jobs_found": 5,
                    "jobs": [
                        {
                            "title": "Senior Python Developer",
                            "company": "Tech Corp",
                            "location": "San Francisco, CA",
                            "description": "Job description...",
                            "requirements": ["Python", "Django"],
                            "salary_range": "$120k - $180k",
                            "job_type": "full_time",
                            "posted_date": "2024-01-15",
                            "linkedin_url": "https://linkedin.com/jobs/123",
                            "skills_matched": ["Python"]
                        }
                    ]
                }
            },
            "GET /linkedin/status": {
                "description": "Get scraper status and health information"
            },
            "GET /linkedin/help": {
                "description": "Get this help information"
            }
        },
        "notes": [
            "LinkedIn may implement anti-bot measures that could affect scraping",
            "Use reasonable delays between requests to avoid being blocked",
            "Some job details may require authentication to access"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
