#!/usr/bin/env python3
"""
Test script for LinkedIn job scraping functionality
"""
import asyncio
import json
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.schemas.linkedin import JobSearchRequest
from app.services.linkedin_scraper import LinkedInJobScraper


async def test_job_search():
    """Test the LinkedIn job search functionality"""
    print("=== LinkedIn Job Scraper Test ===")
    
    # Create a test search request
    search_request = JobSearchRequest(
        skills=["Python", "FastAPI"],
        location="Remote",
        experience_level="mid_senior",
        job_type="full_time",
        limit=5
    )
    
    print(f"Testing job search with request:")
    print(f"  Skills: {search_request.skills}")
    print(f"  Location: {search_request.location}")
    print(f"  Experience Level: {search_request.experience_level}")
    print(f"  Job Type: {search_request.job_type}")
    print(f"  Limit: {search_request.limit}")
    print()
    
    # Create scraper instance
    scraper = LinkedInJobScraper()
    
    try:
        # Test URL building
        test_url = scraper._build_search_url(search_request)
        print(f"Generated search URL: {test_url}")
        print()
        
        # Test status check
        status = scraper.get_scraping_status()
        print(f"Scraper status: {status.status}")
        print()
        
        # Note: We're not running the full search in tests due to WebDriver requirements
        print("✅ Basic functionality tests passed!")
        print("ℹ️  Full scraping test requires Chrome WebDriver installation")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def test_schema_validation():
    """Test Pydantic schema validation"""
    print("=== Schema Validation Test ===")
    
    try:
        # Test valid request
        valid_request = JobSearchRequest(
            skills=["Python", "Machine Learning"],
            location="San Francisco, CA",
            limit=10
        )
        print("✅ Valid request schema validation passed")
        
        # Test invalid skills (empty list)
        try:
            invalid_request = JobSearchRequest(skills=[], limit=10)
            print("❌ Empty skills validation should have failed")
            return False
        except ValueError:
            print("✅ Empty skills validation correctly failed")
        
        # Test invalid experience level
        try:
            invalid_request = JobSearchRequest(
                skills=["Python"],
                experience_level="invalid_level"
            )
            print("❌ Invalid experience level validation should have failed")
            return False
        except ValueError:
            print("✅ Invalid experience level validation correctly failed")
        
        print("✅ All schema validation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema validation test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("Starting LinkedIn Job Scraper Tests...\n")
    
    # Run schema validation tests
    schema_test_passed = test_schema_validation()
    print()
    
    # Run job search tests
    search_test_passed = await test_job_search()
    print()
    
    # Summary
    if schema_test_passed and search_test_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)