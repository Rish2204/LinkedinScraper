#!/usr/bin/env python3
"""
Quick test script for LinkedIn Profile Scraper
"""

import os
from linkedin_profile_scraper import LinkedInProfileScraper

def test_scraper():
    """Test the LinkedIn scraper with sample data"""
    
    print("\n=== LinkedIn Profile Scraper Test ===\n")
    
    # Check for environment variables first
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("⚠️  No credentials in environment variables.")
        print("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        print("\nExample:")
        print("export LINKEDIN_EMAIL='your-email@example.com'")
        print("export LINKEDIN_PASSWORD='your-password'")
        return
    
    # Oracle PL/SQL Developer search URL
    search_url = "https://www.linkedin.com/search/results/people/?keywords=oracle%20plsql%20developer"
    
    print(f"📧 Using email: {email[:3]}***{email[-10:]}")
    print(f"🔍 Search URL: {search_url}")
    print(f"📊 Profiles to scrape: 5")
    
    # Create scraper instance
    scraper = LinkedInProfileScraper(email=email, password=password, headless=False)
    
    print("\n🚀 Starting scraper (browser will open)...")
    print("⏳ This may take a few minutes...\n")
    
    # Scrape profiles
    profiles = scraper.scrape_profiles(search_url, max_profiles=5)
    
    if profiles:
        print(f"\n✅ Successfully scraped {len(profiles)} profiles!")
        
        # Export to Excel
        filename = scraper.export_to_excel(profiles, "oracle_plsql_profiles.xlsx")
        print(f"📊 Data exported to: {filename}")
        
        # Display results
        print("\n=== Top Matched Profiles ===\n")
        for i, profile in enumerate(profiles[:3], 1):
            print(f"{i}. {profile.name}")
            print(f"   📍 Location: {profile.location}")
            print(f"   🏢 Company: {profile.current_company}")
            print(f"   📊 Match Score: {profile.skill_match_score:.1f}%")
            print(f"   ✅ Matched Skills: {', '.join(profile.required_skills_matched[:5]) if profile.required_skills_matched else 'None'}")
            print(f"   📧 Email: {profile.email if profile.email else 'Not available'}")
            print(f"   🔗 Profile: {profile.profile_url}")
            print()
        
        print("\n📋 Summary:")
        print(f"   Total profiles scraped: {len(profiles)}")
        print(f"   Profiles with 70%+ match: {sum(1 for p in profiles if p.skill_match_score >= 70)}")
        print(f"   Profiles with 50-70% match: {sum(1 for p in profiles if 50 <= p.skill_match_score < 70)}")
        print(f"   Profiles with <50% match: {sum(1 for p in profiles if p.skill_match_score < 50)}")
        
    else:
        print("❌ No profiles were scraped. Please check your credentials and try again.")

if __name__ == "__main__":
    test_scraper()