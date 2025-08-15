# LinkedIn Scraper

A comprehensive LinkedIn scraping toolkit with profile extraction, job search, skill matching, and Excel export capabilities.

## Features

### Profile Scraping
- LinkedIn profile scraping with anti-detection measures
- Skill matching and scoring
- Excel export with detailed profile information
- AI-powered profile analysis

### Job Search
- LinkedIn job listing scraping
- Advanced search filters (skills, location, experience level, job type)
- Job details extraction
- REST API endpoints for job search

### Command Line Interface
- CLI for job searching
- Profile scraping automation
- Batch processing capabilities

## Project Structure

```
linkedin-scraper/
├── linkedin_profile_scraper.py    # Main profile scraping functionality
├── linkedin_cli.py                # Command-line interface
├── linkedin_demo.py               # Demo script
├── linkedin_scraper.py            # Job scraping service (from backend)
├── linkedin.py                    # Pydantic schemas (from backend)
├── endpoints/linkedin.py          # FastAPI endpoints (from backend)
├── test_linkedin_scraper.py       # Profile scraper tests
├── test_linkedin_agent.py         # AI agent tests
├── test_linkedin.py               # Job scraper tests (from backend)
├── requirements.txt               # Dependencies
├── setup.sh                       # Setup script
├── README.md                      # This file
├── README_linkedin.md             # Detailed documentation
├── .env.example                   # Environment template
└── .gitignore                     # Git ignore rules
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your LinkedIn credentials and API keys
```

## Usage

### Profile Scraping
```bash
python linkedin_profile_scraper.py
```

### Job Search (CLI)
```bash
python linkedin_cli.py -s "Python,JavaScript" -l "San Francisco"
```

### Job Search (API)
```bash
# Start the FastAPI server
uvicorn linkedin_scraper:app --reload

# Use the API endpoints
curl -X POST "http://localhost:8000/linkedin/search" \
  -H "Content-Type: application/json" \
  -d '{"skills": ["Python", "JavaScript"], "location": "San Francisco"}'
```

### Demo
```bash
python linkedin_demo.py
```

## Configuration

Create a `.env` file with the following variables:
```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## API Endpoints

### Job Search
- `POST /linkedin/search` - Search for jobs
- `GET /linkedin/status` - Get scraping status
- `GET /linkedin/help` - Get API documentation

### Profile Scraping
- Use the `linkedin_profile_scraper.py` script directly
- Supports batch processing and Excel export

## Testing

Run all tests:
```bash
pytest
```

Run specific test files:
```bash
pytest test_linkedin_scraper.py
pytest test_linkedin_agent.py
pytest test_linkedin.py
```

## Development

### Code Formatting
```bash
black .
isort .
flake8 .
```

### Running Tests
```bash
pytest --cov=. --cov-report=html
```

## Migration from Pravis Boutique

This project was extracted from the main Pravis Boutique backend and includes:

- **Profile Scraper**: Original LinkedIn profile scraping functionality
- **Job Scraper**: FastAPI service for job search (moved from backend)
- **API Endpoints**: REST API for job search (moved from backend)
- **Schemas**: Pydantic models for data validation (moved from backend)
- **Tests**: Comprehensive test suite for all functionality

## License

This project is part of the Pravis Boutique ecosystem.
