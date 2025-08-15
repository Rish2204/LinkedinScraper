# LinkedIn Job Scraping Module

A comprehensive LinkedIn job scraping solution integrated into the Pravis Boutique backend API. This module allows users to search for jobs on LinkedIn based on skillsets and other criteria.

## 🚀 Quick Start

### API Usage
```bash
# Start the FastAPI server
uvicorn main:app --reload

# Search for jobs via API
curl -X POST "http://localhost:8000/api/v1/linkedin/search" \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "FastAPI", "Machine Learning"],
    "location": "San Francisco, CA",
    "experience_level": "mid_senior",
    "job_type": "full_time",
    "limit": 10
  }'
```

### CLI Usage
```bash
# Search for Python jobs
python linkedin_cli.py -s Python FastAPI -l "Remote" -e mid_senior

# Get JSON output
python linkedin_cli.py -s "Machine Learning" --json

# Verbose output with job details
python linkedin_cli.py -s JavaScript React -l "New York, NY" --verbose
```

### Demo
```bash
# Run the demo to see example functionality
python linkedin_demo.py
```

## 📁 Files Structure

```
backend/
├── app/
│   ├── schemas/
│   │   └── linkedin.py              # Pydantic models for job search
│   ├── services/
│   │   └── linkedin_scraper.py      # Core scraping service
│   └── api/api_v1/endpoints/
│       └── linkedin.py              # FastAPI endpoints
├── tests/
│   └── test_linkedin.py             # Unit tests
├── docs/
│   └── linkedin_scraping.md         # Detailed documentation
├── linkedin_cli.py                  # Command-line interface
├── linkedin_demo.py                 # Demo script
└── README_linkedin.md               # This file
```

## 🛠️ Features

### Core Functionality
- **Skills-based Search**: Search for jobs using specific programming languages, frameworks, or technologies
- **Location Filtering**: Filter jobs by geographic location or remote work
- **Experience Level**: Filter by internship, entry-level, mid-senior, or director positions
- **Job Type**: Filter by full-time, part-time, contract, temporary, or volunteer positions
- **Company Filtering**: Search for jobs at specific companies
- **Detailed Job Information**: Extract job descriptions, requirements, salary ranges, and posting dates

### API Features
- **RESTful API**: Clean, documented API endpoints
- **Input Validation**: Robust Pydantic schema validation
- **Error Handling**: Comprehensive error handling and status reporting
- **Rate Limiting**: Built-in rate limiting to respect LinkedIn's servers
- **Interactive Documentation**: Swagger/OpenAPI documentation at `/docs`

### CLI Features
- **Easy-to-use Interface**: Simple command-line tool for quick searches
- **Multiple Output Formats**: Console-friendly output or JSON format
- **Verbose Mode**: Detailed job information including descriptions and requirements
- **Flexible Filtering**: Support for all API filtering options

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/linkedin/search` | Search for jobs based on criteria |
| `GET` | `/api/v1/linkedin/status` | Get scraping service status |
| `GET` | `/api/v1/linkedin/help` | Get API help information |

## 📋 Request/Response Examples

### Job Search Request
```json
{
  "skills": ["Python", "Django", "PostgreSQL"],
  "location": "Remote",
  "experience_level": "mid_senior",
  "job_type": "full_time",
  "company": "Google",
  "limit": 15
}
```

### Job Search Response
```json
{
  "success": true,
  "total_jobs_found": 12,
  "jobs": [
    {
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "description": "We are looking for a senior Python developer...",
      "requirements": ["5+ years Python", "Django experience"],
      "salary_range": "$120,000 - $180,000",
      "job_type": "full_time",
      "posted_date": "2024-08-14",
      "linkedin_url": "https://linkedin.com/jobs/view/123456789",
      "skills_matched": ["Python", "Django"]
    }
  ],
  "search_query": {...},
  "message": "Successfully found 12 job listings"
}
```

## 🔧 Configuration

### Environment Variables
```env
# Optional configuration in .env file
LINKEDIN_DELAY_BETWEEN_REQUESTS=2
LINKEDIN_REQUEST_TIMEOUT=10
LINKEDIN_MAX_JOBS_PER_REQUEST=50
LINKEDIN_RATE_LIMIT_PER_MINUTE=5
```

### Dependencies
```txt
# Core dependencies
fastapi>=0.97.0
pydantic>=1.10.0
selenium>=4.15.0
beautifulsoup4>=4.12.0

# Server
uvicorn>=0.22.0
```

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/test_linkedin.py -v

# With coverage
pytest tests/test_linkedin.py --cov=app.services.linkedin_scraper

# Run demo
python linkedin_demo.py
```

### Test CLI
```bash
# Basic search
python linkedin_cli.py -s Python

# Advanced search
python linkedin_cli.py -s Python FastAPI -l "Remote" -e mid_senior --json
```

## 📚 Documentation

- **[Complete Documentation](docs/linkedin_scraping.md)**: Detailed API documentation, setup instructions, and best practices
- **[Interactive API Docs](http://localhost:8000/docs)**: Swagger UI when server is running
- **[API Help Endpoint](http://localhost:8000/api/v1/linkedin/help)**: Programmatic help information

## ⚠️ Important Notes

### Prerequisites
1. **Chrome Browser**: Required for web scraping functionality
2. **ChromeDriver**: Automatically managed by Selenium WebDriver Manager
3. **Network Access**: Internet connection required for LinkedIn access

### Limitations
- **Rate Limiting**: LinkedIn implements anti-bot measures - use responsibly
- **Legal Compliance**: Review LinkedIn's Terms of Service
- **Reliability**: Web scraping can be affected by site changes
- **Geographic Restrictions**: Some content may vary by region

### Best Practices
- Use reasonable delays between requests (built-in)
- Monitor for rate limiting and errors
- Respect LinkedIn's servers and policies
- Cache results when appropriate
- Implement proper error handling

## 🔄 Integration with Pravis Boutique

This LinkedIn scraping module is seamlessly integrated into the existing Pravis Boutique FastAPI backend:

- **Consistent Architecture**: Follows the same patterns as other API modules
- **Shared Dependencies**: Uses existing FastAPI, Pydantic, and other dependencies
- **API Versioning**: Follows the `/api/v1/` versioning scheme
- **Error Handling**: Uses the same error handling middleware
- **Documentation**: Integrated with Swagger/OpenAPI documentation

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**:
   ```bash
   uvicorn main:app --reload
   ```

3. **Test the API**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/linkedin/search" \
     -H "Content-Type: application/json" \
     -d '{"skills": ["Python"], "limit": 5}'
   ```

4. **Try the CLI**:
   ```bash
   python linkedin_cli.py -s Python --limit 3
   ```

5. **View Documentation**:
   - Open http://localhost:8000/docs in your browser
   - Read the detailed docs in `docs/linkedin_scraping.md`

## 📈 Future Enhancements

- **Background Processing**: Async job search for large queries
- **Database Integration**: Store and track job searches
- **Email Notifications**: Alert users to new matching jobs
- **Machine Learning**: Job recommendation engine
- **Additional Sources**: Indeed, Glassdoor integration
- **Export Features**: CSV, PDF export of results

---

For detailed documentation, see [docs/linkedin_scraping.md](docs/linkedin_scraping.md)