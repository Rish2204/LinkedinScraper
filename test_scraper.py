#!/usr/bin/env python3
"""
Simple test script to run LinkedIn scraper
Run this to test if the scraper works with your credentials
"""

import os
import sys
from linkedin_profile_scraper import LinkedInProfileScraper

def test_scraper():
    """Test the LinkedIn scraper with minimal setup"""
    print("=== LinkedIn Scraper Test ===")
    print()
    
    # Check if credentials are available
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ Please set your LinkedIn credentials in environment variables:")
        print("   export LINKEDIN_EMAIL='your_email@example.com'")
        print("   export LINKEDIN_PASSWORD='your_password'")
        print()
        print("Or enter them manually when prompted.")
        print()
        
        # Ask for credentials
        email = input("Enter LinkedIn email: ").strip()
        password = input("Enter LinkedIn password: ").strip()
        
        if not email or not password:
            print("❌ Credentials required to continue!")
            return
    
    print(f"✅ Using email: {email}")
    print()
    
    # Test with a simple search
    search_url = "https://www.linkedin.com/search/results/people/?keywords=python%20developer"
    max_profiles = 3  # Just test with 3 profiles
    
    print(f"🔍 Testing with search: {search_url}")
    print(f"📊 Will scrape up to {max_profiles} profiles")
    print()
    
    try:
        # Initialize scraper (non-headless so you can see what's happening)
        print("🚀 Initializing scraper...")
        scraper = LinkedInProfileScraper(email=email, password=password, headless=False)
        
        print("🌐 Opening browser...")
        scraper.setup_driver()
        
        print("🔐 Logging into LinkedIn...")
        if scraper.login():
            print("✅ Login successful!")
            
            print("🔍 Starting profile scraping...")
            profiles = scraper.scrape_profiles(search_url, max_profiles)
            
            if profiles:
                print(f"✅ Successfully scraped {len(profiles)} profiles!")
                
                # Show results
                print("\n📋 Scraped Profiles:")
                for i, profile in enumerate(profiles, 1):
                    print(f"\n{i}. {profile.name}")
                    print(f"   Company: {profile.current_company}")
                    print(f"   Location: {profile.location}")
                    print(f"   Skills: {', '.join(profile.skills[:5]) if profile.skills else 'None'}")
                    print(f"   Match Score: {profile.skill_match_score:.1f}%")
                
                # Export to Excel
                print("\n💾 Exporting to Excel...")
                filename = scraper.export_to_excel(profiles)
                print(f"✅ Data exported to: {filename}")
                
            else:
                print("❌ No profiles were scraped")
                
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nThis might be due to:")
        print("- Invalid credentials")
        print("- LinkedIn blocking automated access")
        print("- Missing Chrome driver")
        print("- Network issues")
    
    finally:
        # Clean up
        if hasattr(scraper, 'driver') and scraper.driver:
            print("\n🧹 Closing browser...")
            scraper.driver.quit()

if __name__ == "__main__":
    test_scraper()
