#!/usr/bin/env python3
"""
LinkedIn Profile Scraper - Final Production Version
Scrapes LinkedIn profiles based on user input for skills, location, and experience
"""

import json
import csv
import time
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup

@dataclass
class ProfileData:
    """Store LinkedIn profile data"""
    name: str
    headline: str = ""
    location: str = ""
    profile_url: str = ""
    current_company: str = ""
    experience: str = ""
    skills: List[str] = None
    skill_match_score: float = 0.0
    required_skills_matched: List[str] = None
    total_skills_count: int = 0
    about: str = ""
    education: str = ""
    connections: str = ""
    raw_text: str = ""
    scraped_at: str = ""
    profile_summary: str = ""
    detailed_skills: str = ""
    
    def to_dict(self):
        return {
            'Name': self.name,
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
            'Connections': self.connections,
            'Raw Text': self.raw_text,
            'Scraped At': self.scraped_at,
            'Profile Summary': self.profile_summary,
            'Detailed Skills': self.detailed_skills
        }

class LinkedInScraper:
    """LinkedIn profile scraper"""
    
    def __init__(self, email: str = None, password: str = None, headless: bool = False):
        self.email = email or os.getenv('LINKEDIN_EMAIL')
        self.password = password or os.getenv('LINKEDIN_PASSWORD')
        self.headless = headless
        self.driver = None
        self.wait_time = 3
        self.timeout = 10
        self.delay_between_requests = 2
        
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        try:
            # Try Safari first (macOS native)
            self.driver = webdriver.Safari()
            print("✅ Using Safari WebDriver")
        except Exception as e:
            print(f"⚠️  Safari failed: {e}")
            print("🔄 Falling back to Chrome...")
            
            # Fallback to Chrome
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
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Using Chrome WebDriver")
        
        # Set window size and bring to front
        self.driver.set_window_size(1920, 1080)
        self.driver.maximize_window()
        
        # Bring browser to front
        try:
            self.driver.execute_script("window.focus();")
        except:
            pass
            
        return self.driver
    
    def login_to_linkedin(self):
        """Login to LinkedIn"""
        if not self.email or not self.password:
            print("❌ LinkedIn credentials not provided. Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables.")
            return False
            
        try:
            print("🔑 Logging into LinkedIn...")
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
                print("✅ Successfully logged into LinkedIn")
                return True
            else:
                print("❌ Login failed - please check credentials")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def calculate_skill_match(self, profile_skills: List[str], target_skills: List[str]) -> tuple:
        """Calculate skill match score between profile and target skills"""
        if not target_skills or not profile_skills:
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
    
    def search_profiles(self, skills: List[str], location: str = "", experience: str = "", limit: int = 20):
        """Search for LinkedIn profiles based on criteria"""
        try:
            # Build search URL
            search_query = " OR ".join(skills)
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query.replace(' ', '%20')}"
            
            if location:
                search_url += f"&location={location.replace(' ', '%20')}"
            
            print(f"🔍 Searching for profiles with skills: {', '.join(skills)}")
            if location:
                print(f"📍 Location: {location}")
            if experience:
                print(f"💼 Experience: {experience}")
            print(f"🌐 Search URL: {search_url}")
            
            # Navigate to search page
            self.driver.get(search_url)
            time.sleep(5)
            
            # Wait for search results to load
            try:
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results-container"))
                )
                print("✅ Search results loaded")
                
                # Add delay so user can see the page
                print("⏳ Waiting 3 seconds so you can see the search results...")
                time.sleep(3)
                
            except TimeoutException:
                print("⚠️  Timeout waiting for search results")
                return []
            
            # Extract profile data
            profiles = self._extract_profiles_from_search_results(skills, limit)
            
            return profiles
            
        except Exception as e:
            print(f"❌ Error during profile search: {e}")
            return []
    
    def _extract_profiles_from_search_results(self, target_skills: List[str], limit: int) -> List[ProfileData]:
        """Extract profile data from search results page"""
        profiles = []
        
        try:
            # Find profile cards using multiple selectors
            profile_cards = []
            possible_selectors = [
                "li.search-result",
                ".search-result",
                ".search-result__card",
                "[data-test-search-result]",
                ".search-results__item"
            ]
            
            for selector in possible_selectors:
                try:
                    profile_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if profile_cards:
                        print(f"📊 Found {len(profile_cards)} profile cards with selector: {selector}")
                        break
                except:
                    continue
            
            if not profile_cards:
                # Fallback: look for any clickable profile links
                profile_cards = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/in/']")
                print(f"🔗 Found {len(profile_cards)} potential profile links")
            
            print(f"📊 Processing up to {min(limit, len(profile_cards))} profiles...")
            
            for i, card in enumerate(profile_cards[:limit]):
                try:
                    profile_data = self._extract_single_profile(card, target_skills, i + 1)
                    if profile_data:
                        # Extract detailed profile information
                        if profile_data.profile_url and profile_data.profile_url != "N/A":
                            print(f"   🔍 Extracting detailed profile for: {profile_data.name}")
                            detailed_info = self.extract_detailed_profile(profile_data.profile_url)
                            
                            # Update profile data with detailed information
                            profile_data.headline = detailed_info.get('headline', 'N/A')
                            profile_data.about = detailed_info['about']
                            profile_data.experience = detailed_info['experience']
                            profile_data.education = detailed_info['education']
                            profile_data.connections = detailed_info['connections']
                            profile_data.profile_summary = detailed_info['profile_summary']
                            profile_data.detailed_skills = detailed_info['skills']
                            
                            # Update skill match score with detailed skills
                            if detailed_info['skills'] != "Not available":
                                skills_list = [skill.strip() for skill in detailed_info['skills'].split(',')]
                                match_score, matched_skills = self.calculate_skill_match(skills_list, target_skills)
                                profile_data.skill_match_score = match_score
                                profile_data.required_skills_matched = matched_skills
                                profile_data.total_skills_count = len(skills_list)
                        
                        profiles.append(profile_data)
                        print(f"   ✅ Profile {i+1}: {profile_data.name}")
                    
                    # Add delay between extractions
                    time.sleep(1)  # Increased delay for detailed scraping
                    
                except Exception as e:
                    print(f"   ❌ Error extracting profile {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error extracting profiles: {e}")
        
        return profiles
    
    def _extract_single_profile(self, card, target_skills: List[str], index: int) -> Optional[ProfileData]:
        """Extract data from a single profile card"""
        try:
            # Get raw text for debugging
            raw_text = card.text if hasattr(card, 'text') else ""
            
            # Extract name
            name = self._extract_text_from_card(card, [
                "span.name-and-icon",
                ".search-result__title",
                "h3",
                ".search-result__name",
                "[data-test-search-result-name]"
            ])
            
            if not name:
                # Try to extract from raw text
                lines = raw_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('View') and not line.startswith('Connect'):
                        line = line.replace('View profile', '').strip()
                        if line and len(line) > 2:
                            name = line
                            break
            
            if not name:
                return None
            
            # Extract headline
            headline = self._extract_text_from_card(card, [
                "p.search-result__info",
                ".search-result__headline",
                ".search-result__subtitle",
                "p",
                ".search-result__description"
            ])
            
            # Extract location
            location = self._extract_text_from_card(card, [
                "p.search-result__location",
                ".search-result__location",
                ".search-result__subtitle",
                "[data-test-search-result-location]"
            ])
            
            # Extract profile URL
            profile_url = self._extract_profile_url(card)
            
            # Extract company
            company = self._extract_text_from_card(card, [
                "p.search-result__company",
                ".search-result__company",
                ".search-result__subtitle",
                "[data-test-search-result-company]"
            ])
            
            # Calculate skill match
            # For now, we'll use a simple approach - you can enhance this later
            match_score, matched_skills = self.calculate_skill_match([name, headline, company], target_skills)
            
            return ProfileData(
                name=name,
                headline=headline or "N/A",
                location=location or "N/A",
                profile_url=profile_url or "N/A",
                current_company=company or "N/A",
                skills=[],
                skill_match_score=match_score,
                required_skills_matched=matched_skills,
                raw_text=raw_text,
                scraped_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"   ❌ Error in profile extraction: {e}")
            return None
    
    def _extract_text_from_card(self, card, selectors: List[str]) -> str:
        """Extract text using multiple selectors"""
        for selector in selectors:
            try:
                element = card.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    return text
            except:
                continue
        return ""
    
    def _extract_profile_url(self, card) -> str:
        """Extract profile URL from card"""
        try:
            # Try to get href from the card itself
            profile_url = card.get_attribute('href')
            if profile_url and '/in/' in profile_url:
                # Clean the URL by removing miniProfileUrn parameter
                clean_url = profile_url.split('?')[0] if '?' in profile_url else profile_url
                return clean_url
            
            # Try to find a link within the card
            link_elem = card.find_element(By.CSS_SELECTOR, "a")
            profile_url = link_elem.get_attribute('href')
            if profile_url and '/in/' in profile_url:
                # Clean the URL by removing miniProfileUrn parameter
                clean_url = profile_url.split('?')[0] if '?' in profile_url else profile_url
                return clean_url
                
        except:
            pass
        
        return ""
    
    def extract_detailed_profile(self, profile_url: str) -> Dict[str, str]:
        """Extract detailed information from a profile page"""
        detailed_info = {
            'about': '',
            'experience': '',
            'education': '',
            'skills': '',
            'connections': '',
            'profile_summary': ''
        }
        
        try:
            print(f"      🔍 Opening profile: {profile_url}")
            
            # Navigate to profile page
            self.driver.get(profile_url)
            time.sleep(5)  # Increased wait time for page to load
            
            # Wait for profile content to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-heading-xlarge"))
                )
                print(f"      ✅ Profile page loaded successfully")
            except TimeoutException:
                print(f"      ⚠️  Profile page load timeout, continuing anyway...")
            
            # Extract about section with multiple strategies
            try:
                about_selectors = [
                    # Modern LinkedIn selectors
                    "section[aria-label='About'] div.display-flex.ph5.pv3",
                    "section[aria-label='About'] div.pv-shared-text-with-see-more",
                    "section[aria-label='About'] span.break-words",
                    "section[aria-label='About'] div.text-body-medium",
                    # Alternative selectors
                    "section[aria-label='About'] div.pv-shared-text",
                    "section[aria-label='About'] div.text-body-medium.break-words",
                    "section[aria-label='About'] div.break-words",
                    # Generic text selectors
                    "section[aria-label='About'] div",
                    "section[aria-label='About'] p",
                    "section[aria-label='About'] span"
                ]
                
                about_found = False
                for selector in about_selectors:
                    try:
                        about_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        about_text = about_elem.text.strip()
                        if about_text and len(about_text) > 10 and not about_text.startswith('About'):
                            detailed_info['about'] = about_text
                            about_found = True
                            break
                    except:
                        continue
                
                # Fallback: Look for any text that might be "about" content
                if not about_found:
                    try:
                        page_text = self.driver.page_source
                        if "About" in page_text:
                            # Try to find text near "About" keyword
                            about_sections = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'About')]")
                            for section in about_sections:
                                try:
                                    parent = section.find_element(By.XPATH, "./..")
                                    text = parent.text.strip()
                                    if len(text) > 20 and "About" in text:
                                        about_text = text.replace("About", "").strip()
                                        if about_text:
                                            detailed_info['about'] = about_text
                                            about_found = True
                                            break
                                except:
                                    continue
                    except:
                        pass
                
                if not about_found:
                    detailed_info['about'] = "Not available"
                    
            except:
                detailed_info['about'] = "Not available"
            
            # Extract experience section with multiple strategies
            try:
                exp_selectors = [
                    "section[aria-label='Experience']",
                    "section[data-section='experience']",
                    "section.experience-section"
                ]
                
                exp_found = False
                for selector in exp_selectors:
                    try:
                        exp_section = self.driver.find_element(By.CSS_SELECTOR, selector)
                        exp_items = exp_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")[:3]
                        
                        if not exp_items:
                            # Try alternative selectors for experience items
                            exp_items = exp_section.find_elements(By.CSS_SELECTOR, "li")[:3]
                        
                        experience_list = []
                        for item in exp_items:
                            try:
                                # Multiple selectors for job title
                                title_selectors = [
                                    "span[aria-hidden='true']",
                                    "h3",
                                    ".t-bold",
                                    ".experience__title",
                                    "span.t-16.t-black.t-bold"
                                ]
                                
                                title = ""
                                for title_sel in title_selectors:
                                    try:
                                        title_elem = item.find_element(By.CSS_SELECTOR, title_sel)
                                        title = title_elem.text.strip()
                                        if title:
                                            break
                                    except:
                                        continue
                                
                                # Multiple selectors for company
                                company_selectors = [
                                    "span.t-14.t-normal",
                                    ".experience__company",
                                    ".t-14.t-black--light",
                                    "span.t-14"
                                ]
                                
                                company = ""
                                for company_sel in company_selectors:
                                    try:
                                        company_elem = item.find_element(By.CSS_SELECTOR, company_sel)
                                        company = company_elem.text.strip()
                                        if company and company != title:
                                            break
                                    except:
                                        continue
                                
                                if title and company:
                                    experience_list.append(f"{title} at {company}")
                                elif title:
                                    experience_list.append(title)
                                    
                            except Exception as e:
                                continue
                        
                        if experience_list:
                            detailed_info['experience'] = "; ".join(experience_list)
                            exp_found = True
                            break
                            
                    except:
                        continue
                
                if not exp_found:
                    detailed_info['experience'] = "Not available"
                    
            except:
                detailed_info['experience'] = "Not available"
            
            # Extract education section with multiple strategies
            try:
                edu_selectors = [
                    "section[aria-label='Education']",
                    "section[data-section='education']",
                    "section.education-section"
                ]
                
                edu_found = False
                for selector in edu_selectors:
                    try:
                        edu_section = self.driver.find_element(By.CSS_SELECTOR, selector)
                        edu_items = edu_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")[:2]
                        
                        if not edu_items:
                            # Try alternative selectors for education items
                            edu_items = edu_section.find_elements(By.CSS_SELECTOR, "li")[:2]
                        
                        education_list = []
                        for item in edu_items:
                            try:
                                # Multiple selectors for school name
                                school_selectors = [
                                    "span[aria-hidden='true']",
                                    "h3",
                                    ".t-bold",
                                    ".education__school",
                                    "span.t-16.t-black.t-bold"
                                ]
                                
                                school = ""
                                for school_sel in school_selectors:
                                    try:
                                        school_elem = item.find_element(By.CSS_SELECTOR, school_sel)
                                        school = school_elem.text.strip()
                                        if school:
                                            break
                                    except:
                                        continue
                                
                                # Multiple selectors for degree
                                degree_selectors = [
                                    "span.t-14.t-normal",
                                    ".education__degree",
                                    ".t-14.t-black--light",
                                    "span.t-14"
                                ]
                                
                                degree = ""
                                for degree_sel in degree_selectors:
                                    try:
                                        degree_elem = item.find_element(By.CSS_SELECTOR, degree_sel)
                                        degree = degree_elem.text.strip()
                                        if degree and degree != school:
                                            break
                                    except:
                                        continue
                                
                                if school and degree:
                                    education_list.append(f"{degree} from {school}")
                                elif school:
                                    education_list.append(school)
                                    
                            except Exception as e:
                                continue
                        
                        if education_list:
                            detailed_info['education'] = "; ".join(education_list)
                            edu_found = True
                            break
                            
                    except:
                        continue
                
                if not edu_found:
                    detailed_info['education'] = "Not available"
                    
            except:
                detailed_info['education'] = "Not available"
            
            # Extract skills section with multiple strategies
            try:
                skills_selectors = [
                    "a[href*='/details/skills/']",
                    "a[href*='skills']",
                    "a[data-control-name='skill_details']",
                    "a[aria-label*='skill']"
                ]
                
                skills_found = False
                for selector in skills_selectors:
                    try:
                        skills_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                        skills_link.click()
                        time.sleep(3)  # Wait for skills page to load
                        
                        # Multiple selectors for skill elements
                        skill_selectors = [
                            "span[aria-hidden='true']",
                            ".skill-category-entity__name-text",
                            ".skill-category-entity__name",
                            ".skill-category-entity__skill-name",
                            "span.t-bold",
                            ".t-16.t-black.t-bold"
                        ]
                        
                        skills = []
                        for skill_sel in skill_selectors:
                            try:
                                skill_elements = self.driver.find_elements(By.CSS_SELECTOR, skill_sel)
                                for elem in skill_elements:
                                    skill_text = elem.text.strip()
                                    if skill_text and len(skill_text) > 1 and skill_text not in skills:
                                        skills.append(skill_text)
                                if skills:
                                    break
                            except:
                                continue
                        
                        if skills:
                            detailed_info['skills'] = ", ".join(skills[:15])  # Limit to first 15 skills
                            skills_found = True
                        
                        # Go back to main profile
                        self.driver.back()
                        time.sleep(2)  # Wait for profile to reload
                        break
                        
                    except:
                        continue
                
                # Fallback: Try to extract skills from the main profile page
                if not skills_found:
                    try:
                        # Look for skills mentioned in the profile text
                        page_text = self.driver.page_source.lower()
                        common_skills = [
                            'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular', 'vue',
                            'node.js', 'django', 'flask', 'spring', 'oracle', 'mysql', 'postgresql', 'mongodb',
                            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'agile', 'scrum'
                        ]
                        
                        found_skills = []
                        for skill in common_skills:
                            if skill in page_text:
                                found_skills.append(skill.title())
                        
                        if found_skills:
                            detailed_info['skills'] = ", ".join(found_skills[:10])
                            skills_found = True
                    except:
                        pass
                
                if not skills_found:
                    detailed_info['skills'] = "Not available"
                    
            except:
                detailed_info['skills'] = "Not available"
            
            # Extract connections
            try:
                connections_elem = self.driver.find_element(By.CSS_SELECTOR, "span.t-bold span")
                detailed_info['connections'] = connections_elem.text.strip()
            except:
                detailed_info['connections'] = "Not available"
            
            # Extract headline from profile page
            try:
                headline_selectors = [
                    "div.text-body-medium.break-words",
                    "div.text-body-medium",
                    "div.break-words",
                    "span.text-body-medium",
                    "div[data-section='headline']",
                    "h2.text-body-medium"
                ]
                
                for selector in headline_selectors:
                    try:
                        headline_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        headline_text = headline_elem.text.strip()
                        if headline_text and len(headline_text) > 5:
                            detailed_info['headline'] = headline_text
                            break
                    except:
                        continue
                        
            except:
                detailed_info['headline'] = "Not available"
            
            # Create profile summary
            summary_parts = []
            if detailed_info['headline'] != "Not available":
                summary_parts.append(f"Headline: {detailed_info['headline']}")
            if detailed_info['about'] != "Not available":
                summary_parts.append(f"About: {detailed_info['about'][:200]}...")
            if detailed_info['experience'] != "Not available":
                summary_parts.append(f"Experience: {detailed_info['experience']}")
            if detailed_info['education'] != "Not available":
                summary_parts.append(f"Education: {detailed_info['education']}")
            if detailed_info['skills'] != "Not available":
                summary_parts.append(f"Skills: {detailed_info['skills']}")
            
            detailed_info['profile_summary'] = " | ".join(summary_parts)
            
            # Debug: Print what was extracted
            print(f"      📊 Extracted data:")
            print(f"         About: {detailed_info['about'][:50]}...")
            print(f"         Experience: {detailed_info['experience'][:50]}...")
            print(f"         Education: {detailed_info['education'][:50]}...")
            print(f"         Skills: {detailed_info['skills'][:50]}...")
            print(f"         Connections: {detailed_info['connections']}")
            
            print(f"      ✅ Profile details extracted successfully")
            
            # Go back to search results
            self.driver.back()
            time.sleep(2)  # Wait for search results to reload
            
        except Exception as e:
            print(f"      ⚠️  Warning: Could not extract full profile details: {e}")
            detailed_info['profile_summary'] = "Profile details extraction failed"
            
            # Try to go back to search results even if extraction failed
            try:
                self.driver.back()
                time.sleep(2)
            except:
                pass
        
        return detailed_info
    
    def save_results(self, profiles: List[ProfileData], skills: List[str], location: str, experience: str):
        """Save scraped profiles to files"""
        if not profiles:
            print("❌ No profiles to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename based on search criteria
        skills_str = "_".join([skill.replace(" ", "").replace("/", "") for skill in skills[:3]])
        location_str = location.replace(" ", "").replace(",", "") if location else "any"
        experience_str = experience.replace(" ", "") if experience else "any"
        
        filename_base = f"linkedin_profiles_{skills_str}_{location_str}_{experience_str}_{timestamp}"
        
        # Save to JSON
        json_filename = f"{filename_base}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump([profile.to_dict() for profile in profiles], f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(profiles)} profiles to: {json_filename}")
        
        # Save to CSV
        csv_filename = f"{filename_base}.csv"
        if profiles:
            fieldnames = profiles[0].to_dict().keys()
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows([profile.to_dict() for profile in profiles])
            print(f"💾 Saved {len(profiles)} profiles to: {csv_filename}")
        
        return json_filename, csv_filename
    
    def close(self):
        """Close the web driver"""
        if self.driver:
            try:
                self.driver.quit()
                print("🔒 Browser closed")
            except Exception as e:
                print(f"⚠️  Warning: Error closing browser: {e}")

def get_user_inputs():
    """Get user inputs for the scraper"""
    print("\n" + "="*60)
    print("🔍 LinkedIn Profile Scraper")
    print("="*60)
    
    # Get skills
    print("\n1️⃣  SKILLS")
    print("Enter the skills you want to search for (separate multiple skills with commas)")
    print("Examples: Oracle PL/SQL, Python Developer, Data Scientist")
    skills_input = input("\nEnter skills: ").strip()
    
    if not skills_input:
        print("❌ Skills are required!")
        return None, None, None
    
    skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
    
    # Get location
    print("\n2️⃣  LOCATION")
    print("Enter the location (optional - press Enter to skip)")
    print("Examples: San Francisco, CA, United States, Remote")
    location = input("Enter location: ").strip()
    
    # Get experience level
    print("\n3️⃣  EXPERIENCE LEVEL")
    print("Choose experience level (optional - press Enter to skip):")
    print("1. Internship")
    print("2. Entry Level")
    print("3. Associate")
    print("4. Mid-Senior")
    print("5. Director")
    print("6. Executive")
    
    experience_choice = input("\nEnter choice (1-6) or press Enter to skip: ").strip()
    
    experience_mapping = {
        "1": "Internship",
        "2": "Entry Level", 
        "3": "Associate",
        "4": "Mid-Senior",
        "5": "Director",
        "6": "Executive"
    }
    
    experience = experience_mapping.get(experience_choice, "") if experience_choice else ""
    
    # Get number of profiles to scrape
    print("\n4️⃣  NUMBER OF PROFILES")
    print("How many profiles would you like to scrape? (default: 20)")
    limit_input = input("Enter number: ").strip()
    
    try:
        limit = int(limit_input) if limit_input else 20
        if limit <= 0:
            limit = 20
    except ValueError:
        limit = 20
    
    return skills, location, experience, limit

def main():
    """Main function"""
    try:
        # Get user inputs
        inputs = get_user_inputs()
        if not inputs:
            return
        
        skills, location, experience, limit = inputs
        
        # Display search summary
        print(f"\n🔍 SEARCH SUMMARY:")
        print(f"   Skills: {', '.join(skills)}")
        print(f"   Location: {location if location else 'Any'}")
        print(f"   Experience: {experience if experience else 'Any'}")
        print(f"   Profiles to scrape: {limit}")
        
        # Confirm before proceeding
        confirm = input("\nProceed with scraping? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Scraping cancelled")
            return
        
        # Initialize scraper
        print("\n🚀 Initializing LinkedIn Scraper...")
        scraper = LinkedInScraper(headless=False)
        
        # Setup driver
        print("🌐 Setting up browser...")
        driver = scraper.setup_driver()
        
        # Login to LinkedIn
        if not scraper.login_to_linkedin():
            print("❌ Failed to login. Exiting...")
            return
        
        # Search for profiles
        print(f"\n🔍 Searching for profiles...")
        profiles = scraper.search_profiles(skills, location, experience, limit)
        
        if not profiles:
            print("❌ No profiles found")
            return
        
        # Save results
        print(f"\n💾 Saving {len(profiles)} profiles...")
        json_file, csv_file = scraper.save_results(profiles, skills, location, experience)
        
        # Print summary
        print(f"\n🎉 Scraping completed successfully!")
        print(f"📊 Total profiles scraped: {len(profiles)}")
        print(f"📁 Files saved:")
        print(f"   - JSON: {json_file}")
        print(f"   - CSV: {csv_file}")
        
        # Show sample profiles
        print(f"\n📋 Sample profiles:")
        for i, profile in enumerate(profiles[:3]):
            print(f"   {i+1}. {profile.name} - {profile.headline}")
            if profile.location and profile.location != "N/A":
                print(f"      📍 {profile.location}")
            if profile.current_company and profile.current_company != "N/A":
                print(f"      🏢 {profile.current_company}")
            if profile.profile_summary and profile.profile_summary != "Profile details extraction failed":
                print(f"      📝 Summary: {profile.profile_summary[:150]}...")
            if profile.detailed_skills and profile.detailed_skills != "Not available":
                print(f"      🎯 Skills: {profile.detailed_skills[:100]}...")
            print(f"      🔗 {profile.profile_url}")
            print()
        
    except KeyboardInterrupt:
        print("\n\n❌ Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    main()
