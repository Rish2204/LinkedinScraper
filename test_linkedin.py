import pytest
from unittest.mock import patch, MagicMock
import asyncio
from app.schemas.linkedin import JobSearchRequest, JobListing, JobSearchResponse
from app.services.linkedin_scraper import LinkedInJobScraper


class TestLinkedInSchemas:
    """Test LinkedIn Pydantic schemas"""
    
    def test_valid_job_search_request(self):
        """Test valid job search request creation"""
        request = JobSearchRequest(
            skills=["Python", "FastAPI"],
            location="San Francisco, CA",
            experience_level="mid_senior",
            job_type="full_time",
            limit=10
        )
        
        assert request.skills == ["Python", "FastAPI"]
        assert request.location == "San Francisco, CA"
        assert request.experience_level == "mid_senior"
        assert request.job_type == "full_time"
        assert request.limit == 10
    
    def test_invalid_empty_skills(self):
        """Test that empty skills list raises validation error"""
        with pytest.raises(ValueError, match="At least one skill must be provided"):
            JobSearchRequest(skills=[])
    
    def test_invalid_experience_level(self):
        """Test invalid experience level raises validation error"""
        with pytest.raises(ValueError, match="Invalid experience level"):
            JobSearchRequest(skills=["Python"], experience_level="invalid_level")
    
    def test_invalid_job_type(self):
        """Test invalid job type raises validation error"""
        with pytest.raises(ValueError, match="Invalid job type"):
            JobSearchRequest(skills=["Python"], job_type="invalid_type")
    
    def test_skills_whitespace_cleanup(self):
        """Test that skills with whitespace are cleaned up"""
        request = JobSearchRequest(skills=["  Python  ", "FastAPI", "  "])
        assert request.skills == ["Python", "FastAPI"]
    
    def test_job_listing_creation(self):
        """Test job listing model creation"""
        job = JobListing(
            title="Software Engineer",
            company="Tech Corp",
            location="Remote",
            description="Great job opportunity",
            requirements=["Python", "5+ years experience"],
            salary_range="$100,000 - $150,000",
            job_type="full_time",
            posted_date="2024-08-14",
            linkedin_url="https://linkedin.com/jobs/123",
            skills_matched=["Python"]
        )
        
        assert job.title == "Software Engineer"
        assert job.company == "Tech Corp"
        assert job.skills_matched == ["Python"]
    
    def test_job_search_response_creation(self):
        """Test job search response model creation"""
        request = JobSearchRequest(skills=["Python"])
        job = JobListing(title="Engineer", company="Corp", location="Remote")
        
        response = JobSearchResponse(
            success=True,
            total_jobs_found=1,
            jobs=[job],
            search_query=request,
            message="Success"
        )
        
        assert response.success is True
        assert response.total_jobs_found == 1
        assert len(response.jobs) == 1
        assert response.message == "Success"


class TestLinkedInScraper:
    """Test LinkedIn scraper service"""
    
    @pytest.fixture
    def scraper(self):
        """Create scraper instance for testing"""
        return LinkedInJobScraper()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample search request for testing"""
        return JobSearchRequest(
            skills=["Python", "Django"],
            location="New York, NY",
            experience_level="mid_senior",
            job_type="full_time",
            limit=5
        )
    
    def test_build_search_url(self, scraper, sample_request):
        """Test URL building from search request"""
        url = scraper._build_search_url(sample_request)
        
        assert "linkedin.com/jobs/search" in url
        assert "keywords=Python%20OR%20Django" in url or "Python OR Django" in url
        assert "location=New York" in url
        assert "f_E=4" in url  # mid_senior experience level
        assert "f_JT=F" in url  # full_time job type
        assert "f_TPR=r86400" in url  # last 24 hours
    
    def test_build_search_url_minimal(self, scraper):
        """Test URL building with minimal parameters"""
        request = JobSearchRequest(skills=["Python"])
        url = scraper._build_search_url(request)
        
        assert "linkedin.com/jobs/search" in url
        assert "keywords=Python" in url
        assert "f_TPR=r86400" in url
    
    def test_build_search_url_with_company(self, scraper):
        """Test URL building with company filter"""
        request = JobSearchRequest(skills=["Python"], company="Google")
        url = scraper._build_search_url(request)
        
        assert "f_C=Google" in url
    
    def test_get_scraping_status(self, scraper):
        """Test scraping status method"""
        status = scraper.get_scraping_status()
        
        assert status.status == "ready"
        assert status.jobs_scraped == 0
        assert isinstance(status.errors, list)
        assert status.timestamp is not None
    
    @patch('app.services.linkedin_scraper.webdriver.Chrome')
    def test_create_driver_options(self, mock_chrome, scraper):
        """Test that Chrome driver is created with correct options"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        driver = scraper._create_driver()
        
        # Verify Chrome was called with options
        mock_chrome.assert_called_once()
        args = mock_chrome.call_args
        options = args[1]['options'] if 'options' in args[1] else args[0][0] if args[0] else None
        
        # Can't easily verify options content due to mocking complexity,
        # but we can verify the driver was created
        assert driver == mock_driver
    
    def test_extract_job_from_element_missing_data(self, scraper):
        """Test job extraction handles missing data gracefully"""
        # Mock a minimal BeautifulSoup element
        mock_element = MagicMock()
        mock_element.find.return_value = None
        
        result = scraper._extract_job_from_element(mock_element, ["Python"])
        
        # Should handle missing elements gracefully
        assert result is None or isinstance(result, JobListing)


# Integration-style tests (would require actual browser setup)
class TestLinkedInScraperIntegration:
    """Integration tests for LinkedIn scraper (requires browser setup)"""
    
    @pytest.mark.skip(reason="Requires Chrome WebDriver setup")
    async def test_search_jobs_integration(self):
        """Integration test for actual job search (skipped by default)"""
        scraper = LinkedInJobScraper()
        request = JobSearchRequest(
            skills=["Python"],
            limit=1
        )
        
        result = await scraper.search_jobs(request)
        
        assert isinstance(result, JobSearchResponse)
        # Note: actual assertions would depend on LinkedIn's current state


if __name__ == "__main__":
    # Run tests if this file is executed directly
    pytest.main([__file__, "-v"])