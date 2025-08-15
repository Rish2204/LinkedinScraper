import logging
import time
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode, quote
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup

from app.schemas.linkedin import JobSearchRequest, JobListing, JobSearchResponse, ScrapingStatus


logger = logging.getLogger(__name__)


class LinkedInJobScraper:
    """Service for scraping LinkedIn job listings"""
    
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search"
        self.timeout = 10
        self.delay_between_requests = 2  # seconds
        
    def _create_driver(self) -> webdriver.Chrome:
        """Create a Chrome WebDriver instance with appropriate options"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            raise WebDriverException(f"Failed to initialize web driver: {e}")
    
    def _build_search_url(self, search_request: JobSearchRequest) -> str:
        """Build LinkedIn job search URL from request parameters"""
        params = {}
        
        # Keywords (skills)
        if search_request.skills:
            keywords = " OR ".join(search_request.skills)
            params['keywords'] = keywords
        
        # Location
        if search_request.location:
            params['location'] = search_request.location
        
        # Experience level mapping
        experience_mapping = {
            'internship': '1',
            'entry_level': '2', 
            'associate': '3',
            'mid_senior': '4',
            'director': '5'
        }
        if search_request.experience_level and search_request.experience_level in experience_mapping:
            params['f_E'] = experience_mapping[search_request.experience_level]
        
        # Job type mapping
        job_type_mapping = {
            'full_time': 'F',
            'part_time': 'P',
            'contract': 'C',
            'temporary': 'T',
            'volunteer': 'V'
        }
        if search_request.job_type and search_request.job_type in job_type_mapping:
            params['f_JT'] = job_type_mapping[search_request.job_type]
        
        # Company
        if search_request.company:
            params['f_C'] = search_request.company
        
        # Time filter (recent jobs)
        params['f_TPR'] = 'r86400'  # Last 24 hours
        params['start'] = '0'
        
        query_string = urlencode(params, quote_via=quote)
        return f"{self.base_url}?{query_string}"
    
    def _extract_job_from_element(self, job_element, search_skills: List[str]) -> Optional[JobListing]:
        """Extract job information from a job listing element"""
        try:
            # Extract basic job information
            title_element = job_element.find('h3', class_='base-search-card__title')
            title = title_element.get_text().strip() if title_element else "N/A"
            
            company_element = job_element.find('h4', class_='base-search-card__subtitle')
            company = company_element.get_text().strip() if company_element else "N/A"
            
            location_element = job_element.find('span', class_='job-search-card__location')
            location = location_element.get_text().strip() if location_element else "N/A"
            
            # Extract job URL
            link_element = job_element.find('a', class_='base-card__full-link')
            linkedin_url = link_element.get('href') if link_element else None
            
            # Extract posting date
            date_element = job_element.find('time')
            posted_date = date_element.get('datetime') if date_element else None
            
            # Match skills in job title and company name
            skills_matched = []
            job_text = f"{title} {company}".lower()
            for skill in search_skills:
                if skill.lower() in job_text:
                    skills_matched.append(skill)
            
            return JobListing(
                title=title,
                company=company,
                location=location,
                linkedin_url=linkedin_url,
                posted_date=posted_date,
                skills_matched=skills_matched
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract job information: {e}")
            return None
    
    def _get_job_details(self, driver: webdriver.Chrome, job_url: str) -> Dict[str, Any]:
        """Get detailed job information from job page"""
        try:
            driver.get(job_url)
            time.sleep(2)
            
            # Wait for page to load
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "show-more-less-html__markup"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract job description
            description_element = soup.find('div', class_='show-more-less-html__markup')
            description = description_element.get_text().strip() if description_element else None
            
            # Extract requirements (look for bullet points or key phrases)
            requirements = []
            if description:
                # Simple regex to find requirement-like statements
                requirement_patterns = [
                    r'(?:required|must have|minimum).*?(?:\n|\.)',
                    r'(?:\d+[\+\-]?\s*years?\s*(?:of\s*)?experience)',
                    r'(?:bachelor|master|phd|degree)',
                    r'(?:proficient|experience|knowledge)\s+(?:in|with|of)\s+[\w\s,]+',
                ]
                
                for pattern in requirement_patterns:
                    matches = re.findall(pattern, description.lower(), re.IGNORECASE)
                    requirements.extend([match.strip() for match in matches[:3]])  # Limit to 3 per pattern
            
            # Extract salary information
            salary_element = soup.find('span', class_='salary-range')
            salary_range = salary_element.get_text().strip() if salary_element else None
            
            return {
                'description': description,
                'requirements': requirements[:10],  # Limit to 10 requirements
                'salary_range': salary_range
            }
            
        except Exception as e:
            logger.warning(f"Failed to get job details from {job_url}: {e}")
            return {}
    
    async def search_jobs(self, search_request: JobSearchRequest) -> JobSearchResponse:
        """Search for jobs on LinkedIn based on the provided criteria"""
        logger.info(f"Starting LinkedIn job search for skills: {search_request.skills}")
        
        driver = None
        try:
            # Create WebDriver
            driver = self._create_driver()
            
            # Build search URL
            search_url = self._build_search_url(search_request)
            logger.info(f"Searching with URL: {search_url}")
            
            # Navigate to search page
            driver.get(search_url)
            time.sleep(self.delay_between_requests)
            
            # Wait for job listings to load
            try:
                WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
                )
            except TimeoutException:
                logger.warning("Timeout waiting for job listings to load")
                return JobSearchResponse(
                    success=False,
                    total_jobs_found=0,
                    jobs=[],
                    search_query=search_request,
                    message="Failed to load job listings - LinkedIn may be blocking requests"
                )
            
            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find job listing containers
            job_containers = soup.find_all('div', class_='base-card')
            logger.info(f"Found {len(job_containers)} job containers")
            
            jobs = []
            processed_count = 0
            
            for container in job_containers:
                if processed_count >= search_request.limit:
                    break
                
                job = self._extract_job_from_element(container, search_request.skills)
                if job:
                    # Optionally get detailed information for first few jobs
                    if processed_count < 3 and job.linkedin_url:
                        try:
                            details = self._get_job_details(driver, job.linkedin_url)
                            if details.get('description'):
                                job.description = details['description'][:500] + "..." if len(details['description']) > 500 else details['description']
                            if details.get('requirements'):
                                job.requirements = details['requirements']
                            if details.get('salary_range'):
                                job.salary_range = details['salary_range']
                        except Exception as e:
                            logger.warning(f"Failed to get details for job: {e}")
                    
                    jobs.append(job)
                    processed_count += 1
                
                # Add delay between processing jobs
                time.sleep(0.5)
            
            logger.info(f"Successfully scraped {len(jobs)} jobs")
            
            return JobSearchResponse(
                success=True,
                total_jobs_found=len(jobs),
                jobs=jobs,
                search_query=search_request,
                message=f"Successfully found {len(jobs)} job listings"
            )
            
        except WebDriverException as e:
            logger.error(f"WebDriver error during job search: {e}")
            return JobSearchResponse(
                success=False,
                total_jobs_found=0,
                jobs=[],
                search_query=search_request,
                message=f"Web scraping error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during job search: {e}")
            return JobSearchResponse(
                success=False,
                total_jobs_found=0,
                jobs=[],
                search_query=search_request,
                message=f"Unexpected error: {str(e)}"
            )
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error closing driver: {e}")
    
    def get_scraping_status(self) -> ScrapingStatus:
        """Get current status of scraping operations"""
        return ScrapingStatus(
            status="ready",
            jobs_scraped=0,
            errors=[],
            timestamp=datetime.now().isoformat()
        )