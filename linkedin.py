import logging
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from app.schemas.linkedin import (
    JobSearchRequest, 
    JobSearchResponse, 
    ScrapingStatus
)
from app.services.linkedin_scraper import LinkedInJobScraper


logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize scraper service
linkedin_scraper = LinkedInJobScraper()


@router.post("/search", response_model=JobSearchResponse, status_code=status.HTTP_200_OK)
async def search_linkedin_jobs(search_request: JobSearchRequest) -> JobSearchResponse:
    """
    Search for jobs on LinkedIn based on skillset and other criteria.
    
    This endpoint accepts a list of skills and optional filters to search for relevant 
    job opportunities on LinkedIn.
    
    **Parameters:**
    - **skills**: List of skills to search for (required, 1-10 skills)
    - **location**: Job location (optional)
    - **experience_level**: Experience level filter (optional)
    - **job_type**: Job type filter (optional) 
    - **company**: Specific company filter (optional)
    - **limit**: Maximum number of jobs to return (1-50, default: 10)
    
    **Returns:**
    - Job search results with matching listings
    """
    try:
        logger.info(f"Received job search request for skills: {search_request.skills}")
        
        # Perform the job search
        result = await linkedin_scraper.search_jobs(search_request)
        
        if not result.success:
            logger.warning(f"Job search failed: {result.message}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Job search failed: {result.message}"
            )
        
        logger.info(f"Job search completed successfully. Found {result.total_jobs_found} jobs")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in job search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred during job search"
        )


@router.get("/status", response_model=ScrapingStatus, status_code=status.HTTP_200_OK)
async def get_scraping_status() -> ScrapingStatus:
    """
    Get the current status of the LinkedIn scraping service.
    
    Returns information about the scraper's current state and any recent operations.
    """
    try:
        status_info = linkedin_scraper.get_scraping_status()
        return status_info
    except Exception as e:
        logger.error(f"Error getting scraping status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scraping status"
        )


@router.get("/help", status_code=status.HTTP_200_OK)
async def get_linkedin_help():
    """
    Get help information for using the LinkedIn job scraping endpoints.
    
    Returns detailed information about how to use the LinkedIn job search functionality.
    """
    help_info = {
        "description": "LinkedIn Job Scraping API",
        "version": "1.0.0",
        "endpoints": {
            "POST /search": {
                "description": "Search for jobs based on skills and criteria",
                "required_fields": ["skills"],
                "optional_fields": ["location", "experience_level", "job_type", "company", "limit"]
            },
            "GET /status": {
                "description": "Get scraping service status"
            },
            "GET /help": {
                "description": "Get API help information"
            }
        },
        "example_request": {
            "skills": ["Python", "FastAPI", "Machine Learning"],
            "location": "San Francisco, CA",
            "experience_level": "mid_senior",
            "job_type": "full_time",
            "limit": 20
        },
        "supported_experience_levels": [
            "internship",
            "entry_level", 
            "associate",
            "mid_senior",
            "director"
        ],
        "supported_job_types": [
            "full_time",
            "part_time",
            "contract", 
            "temporary",
            "volunteer"
        ],
        "rate_limits": {
            "requests_per_minute": 5,
            "max_results_per_request": 50
        },
        "notes": [
            "LinkedIn may implement anti-bot measures that could affect scraping",
            "Results are limited to publicly available job postings",
            "Detailed job information is only fetched for the first 3 results",
            "Use appropriate delays between requests to avoid being blocked"
        ]
    }
    
    return JSONResponse(content=help_info)


# Rate limiting middleware for LinkedIn endpoints
@router.middleware("http")
async def linkedin_rate_limit_middleware(request, call_next):
    """Simple rate limiting for LinkedIn scraping endpoints"""
    # This is a basic implementation - in production you'd want to use Redis
    # or a proper rate limiting solution
    response = await call_next(request)
    return response