#!/usr/bin/env python3
"""
LinkedIn Scraper - Comprehensive LinkedIn scraping toolkit
Combines profile scraping, job search, skill matching, and Excel export capabilities
"""

import logging
import time
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from dataclasses import dataclass, asdict
from urllib.parse import urlencode, quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProfileData:
    """Store LinkedIn profile data"""
    name: str
    headline: str = ""
    location: str = ""
    profile_url: str = ""
    email: str = ""
    current_company: str = ""
    experience: str = ""
    skills: List[str] = None
    skill_match_score: float = 0.0
    required_skills_matched: List[str] = None
    total_skills_count: int = 0
    about: str = ""
    education: str = ""
    connections: str = ""
    
    def to_dict(self):
        return {
            'Name': self.name,
            'Email': self.email if self.email else 'Not Available',
            'Headline': self.headline,
            'Current Company': self.current_company,
            'Location': self.location,
            'Experience Summary': self.experience,
            'Education': self.education,
            'Skills Matched': ', '.join(self.required_skills_matched) if self.required_skills_matched else '',
            'Match Score (%)': round(self.skill_match_score, 1),
            'Total Skills': self.total_skills_count,
            'All Skills': ', '.join(self.skills) if self.skills else '',
            'About': self.about[:200] + '...' if self.about and len(self.about) > 200 else self.about,
            'Profile URL': self.profile_url,
            'Connections': self.connections
        }


@dataclass
class JobListing:
    """Store LinkedIn job listing data"""
    title: str
    company: str
    location: str
    description: str = ""
    requirements: List[str] = None
    salary_range: str = ""
    job_type: str = ""
    posted_date: str = ""
    linkedin_url: str = ""
    skills_matched: List[str] = None
    match_score: float = 0.0
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
        if self.skills_matched is None:
            self.skills_matched = []


@dataclass
class JobSearchRequest:
    """Job search request parameters"""
    skills: List[str]
    location: str = ""
    experience_level: str = ""
    job_type: str = ""
    company: str = ""
    limit: int = 10
    
    def __post_init__(self):
        if not self.skills:
            raise ValueError("At least one skill must be provided")
        # Clean up skills (remove whitespace)
        self.skills = [skill.strip() for skill in self.skills if skill.strip()]


@dataclass
class JobSearchResponse:
    """Job search response"""
    success: bool
    total_jobs_found: int
    jobs: List[JobListing]
    search_query: JobSearchRequest
    message: str = ""


@dataclass
class ScrapingStatus:
    """Scraping operation status"""
    status: str
    jobs_scraped: int = 0
    profiles_scraped: int = 0
    errors: List[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class LinkedInScraper:
    """Comprehensive LinkedIn scraper for both profiles and jobs"""
    
    def __init__(self, email: str = None, password: str = None, headless: bool = True):
        self.email = email or os.getenv('LINKEDIN_EMAIL')
        self.password = password or os.getenv('LINKEDIN_PASSWORD')
        self.headless = headless
        self.driver = None
        self.wait_time = 3
        self.base_url = "https://www.linkedin.com/jobs/search"
        self.timeout = 10
        self.delay_between_requests = 2
        
        # Default target skills (can be customized)
        self.target_skills = [
            'Oracle', 'PL/SQL', 'SQL', 'Database', 'Oracle Database',
            'Stored Procedures', 'Triggers', 'Functions', 'Packages',
            'Performance Tuning', 'Query Optimization', 'Data Modeling',
            'ETL', 'Data Warehouse', 'Oracle Forms', 'Oracle Reports',
            'APEX', 'SQL*Plus', 'TOAD', 'SQL Developer', 'Unix',
            'Shell Scripting', 'Python', 'Java', 'JavaScript'
        ]
    
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        options = Options()
        
        if self.headless:
            options.add_argument("--headless")
            
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return self.driver
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            raise WebDriverException(f"Failed to initialize web driver: {e}")
    
    def login_to_linkedin(self):
        """Login to LinkedIn"""
        if not self.email or not self.password:
            logger.warning("LinkedIn credentials not provided. Some features may be limited.")
            return False
            
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            # Enter email
            email_field = self.driver.find_element(By.ID, "username")
            email_field.send_keys(self.email)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(5)
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                logger.info("Successfully logged into LinkedIn")
                return True
            else:
                logger.error("Login failed - please check credentials")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def calculate_skill_match(self, profile_skills: List[str], target_skills: List[str] = None) -> tuple:
        """Calculate skill match score between profile and target skills"""
        if not target_skills:
            target_skills = self.target_skills
            
        if not profile_skills:
            return 0.0, []
            
        # Normalize skills for comparison
        profile_skills_lower = [skill.lower().strip() for skill in profile_skills]
        target_skills_lower = [skill.lower().strip() for skill in target_skills]
        
        # Find matching skills
        matched_skills = []
        for target_skill in target_skills_lower:
            for profile_skill in profile_skills_lower:
                if target_skill in profile_skill or profile_skill in target_skill:
                    matched_skills.append(target_skill)
                    break
        
        # Calculate match percentage
        match_score = (len(matched_skills) / len(target_skills)) * 100 if target_skills else 0
        
        return match_score, matched_skills
    
    def scrape_profile(self, profile_url: str) -> Optional[ProfileData]:
        """Scrape a single LinkedIn profile"""
        try:
            self.driver.get(profile_url)
            time.sleep(self.wait_time)
            
            # Extract basic info
            name = self._extract_text("h1.text-heading-xlarge")
            headline = self._extract_text("div.text-body-medium.break-words")
            location = self._extract_text("span.text-body-small.inline.t-black--light.break-words")
            
            # Extract current company
            current_company = self._extract_text("div[aria-label='Current company'] span")
            
            # Extract about section
            about = self._extract_text("section[aria-label='About'] div.display-flex.ph5.pv3")
            
            # Extract experience
            experience = self._extract_experience()
            
            # Extract education
            education = self._extract_education()
            
            # Extract skills
            skills = self._extract_skills()
            
            # Calculate skill match
            match_score, matched_skills = self.calculate_skill_match(skills)
            
            # Extract connections
            connections = self._extract_text("span.t-bold span")
            
            return ProfileData(
                name=name or "N/A",
                headline=headline or "",
                location=location or "",
                profile_url=profile_url,
                current_company=current_company or "",
                experience=experience or "",
                skills=skills,
                skill_match_score=match_score,
                required_skills_matched=matched_skills,
                total_skills_count=len(skills),
                about=about or "",
                education=education or "",
                connections=connections or ""
            )
            
        except Exception as e:
            logger.error(f"Error scraping profile {profile_url}: {e}")
            return None
    
    def _extract_text(self, selector: str) -> str:
        """Extract text from element using CSS selector"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            return ""
    
    def _extract_experience(self) -> str:
        """Extract experience information"""
        try:
            exp_section = self.driver.find_element(By.CSS_SELECTOR, "section[aria-label='Experience']")
            exp_items = exp_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")[:3]
            
            experience_list = []
            for item in exp_items:
                try:
                    title = item.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']").text.strip()
                    company = item.find_element(By.CSS_SELECTOR, "span.t-14.t-normal").text.strip()
                    experience_list.append(f"{title} at {company}")
                except:
                    continue
            
            return "; ".join(experience_list)
        except:
            return ""
    
    def _extract_education(self) -> str:
        """Extract education information"""
        try:
            edu_section = self.driver.find_element(By.CSS_SELECTOR, "section[aria-label='Education']")
            edu_items = edu_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")[:2]
            
            education_list = []
            for item in edu_items:
                try:
                    school = item.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']").text.strip()
                    degree = item.find_element(By.CSS_SELECTOR, "span.t-14.t-normal").text.strip()
                    education_list.append(f"{degree} from {school}")
                except:
                    continue
            
            return "; ".join(education_list)
        except:
            return ""
    
    def _extract_skills(self) -> List[str]:
        """Extract skills from profile"""
        try:
            # Navigate to skills section
            skills_link = self.driver.find_element(By.CSS_SELECTOR, "a[href*='/details/skills/']")
            skills_link.click()
            time.sleep(2)
            
            # Extract skills
            skill_elements = self.driver.find_elements(By.CSS_SELECTOR, "span[aria-hidden='true']")
            skills = [elem.text.strip() for elem in skill_elements if elem.text.strip()]
            
            # Go back to main profile
            self.driver.back()
            time.sleep(1)
            
            return skills
        except:
            return []
    
    def search_jobs(self, search_request: JobSearchRequest) -> JobSearchResponse:
        """Search for jobs on LinkedIn"""
        driver = None
        try:
            driver = self.setup_driver()
            
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
            job_link = job_element.find('a', class_='base-card__full-link')
            job_url = job_link.get('href') if job_link else ""
            
            # Calculate skill match
            match_score, matched_skills = self.calculate_skill_match(search_skills, search_skills)
            
            return JobListing(
                title=title,
                company=company,
                location=location,
                linkedin_url=job_url,
                skills_matched=matched_skills,
                match_score=match_score
            )
            
        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            return None
    
    def get_scraping_status(self) -> ScrapingStatus:
        """Get current status of scraping operations"""
        return ScrapingStatus(
            status="ready",
            jobs_scraped=0,
            profiles_scraped=0,
            errors=[],
            timestamp=datetime.now().isoformat()
        )
    
    def export_to_excel(self, data: List[ProfileData], filename: str = None) -> str:
        """Export profile data to Excel file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_profiles_{timestamp}.xlsx"
        
        try:
            # Convert to DataFrame
            df_data = [profile.to_dict() for profile in data]
            df = pd.DataFrame(df_data)
            
            # Export to Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            logger.info(f"Data exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise
    
    def close(self):
        """Close the web driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")


# Example usage functions
def scrape_profiles(search_query: str, max_profiles: int = 10, target_skills: List[str] = None):
    """Scrape LinkedIn profiles based on search query"""
    scraper = LinkedInScraper(headless=True)
    
    try:
        scraper.setup_driver()
        
        if target_skills:
            scraper.target_skills = target_skills
        
        # This would need to be implemented based on LinkedIn search
        # For now, this is a placeholder
        logger.info(f"Would scrape {max_profiles} profiles for: {search_query}")
        
    finally:
        scraper.close()


def search_jobs(skills: List[str], location: str = "", limit: int = 10):
    """Search for jobs on LinkedIn"""
    scraper = LinkedInScraper(headless=True)
    
    try:
        request = JobSearchRequest(
            skills=skills,
            location=location,
            limit=limit
        )
        
        result = scraper.search_jobs(request)
        
        if result.success:
            logger.info(f"Found {len(result.jobs)} jobs")
            for job in result.jobs:
                print(f"- {job.title} at {job.company} ({job.location})")
        else:
            logger.error(f"Job search failed: {result.message}")
            
    finally:
        scraper.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 LinkedIn Scraper - Professional Tool")
    print("=" * 60)
    print()
    
    # Check if credentials are available
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if email and password:
        print(f"✅ LinkedIn credentials found for: {email}")
    else:
        print("⚠️  LinkedIn credentials not found in .env file")
        print("   Some features may be limited without login")
    
    print()
    print("Choose an option:")
    print("1. 🔍 Search for jobs")
    print("2. 👤 Scrape profiles")
    print("3. 🚪 Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1, 2, or 3): ").strip()
            
            if choice == "1":
                print("\n" + "=" * 40)
                print("🔍 JOB SEARCH")
                print("=" * 40)
                
                # Get keywords/skills
                print("\nEnter the skills or keywords you want to search for.")
                print("Examples: 'Oracle PL/SQL', 'Python Developer', 'Data Scientist'")
                keywords_input = input("\nEnter keywords: ").strip()
                
                if not keywords_input:
                    print("❌ No keywords provided. Please try again.")
                    continue
                
                # Parse keywords
                skills = [skill.strip() for skill in keywords_input.split(',') if skill.strip()]
                
                # Get location
                location = input("Enter location (optional, e.g., 'San Francisco, CA'): ").strip()
                
                # Get limit
                try:
                    limit_input = input("Number of jobs to find (default 10): ").strip()
                    limit = int(limit_input) if limit_input else 10
                except ValueError:
                    limit = 10
                
                print(f"\n🔍 Searching for: {', '.join(skills)}")
                if location:
                    print(f"📍 Location: {location}")
                print(f"📊 Limit: {limit} jobs")
                print("\n⏳ Please wait...")
                
                # Perform search
                search_jobs(skills, location, limit)
                
            elif choice == "2":
                print("\n" + "=" * 40)
                print("👤 PROFILE SCRAPING")
                print("=" * 40)
                
                print("\nEnter the search query for profiles.")
                print("Examples: 'Oracle PL/SQL developers', 'Python developers in San Francisco'")
                query = input("\nEnter search query: ").strip()
                
                if not query:
                    print("❌ No search query provided. Please try again.")
                    continue
                
                try:
                    max_profiles = int(input("Number of profiles to scrape (default 10): ").strip() or "10")
                except ValueError:
                    max_profiles = 10
                
                print(f"\n👤 Searching for profiles: {query}")
                print(f"📊 Max profiles: {max_profiles}")
                print("\n⏳ Please wait...")
                
                # Perform profile scraping
                scrape_profiles(query, max_profiles)
                
            elif choice == "3":
                print("\n👋 Thank you for using LinkedIn Scraper!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again.")
        
        print("\n" + "=" * 60)
        print("Choose an option:")
        print("1. 🔍 Search for jobs")
        print("2. 👤 Scrape profiles")
        print("3. 🚪 Exit")
        print()