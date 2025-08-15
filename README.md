# LinkedIn Scraper

A comprehensive, standalone LinkedIn scraping toolkit with profile extraction, job search, skill matching, and Excel export capabilities.

## Features

### Profile Scraping
- LinkedIn profile scraping with anti-detection measures
- Skill matching and scoring
- Excel export with detailed profile information
- Automated profile data extraction

### Job Search
- LinkedIn job listing scraping
- Advanced search filters (skills, location, experience level, job type)
- Job details extraction
- Interactive command-line interface

### Data Processing
- Skill matching algorithms
- Excel export functionality
- Data validation and cleaning
- Batch processing capabilities

## Project Structure

```
LinkedinScraper/
├── linkedin_scraper.py            # Main scraper (consolidated functionality)
├── test_job_search.py             # Job search test script
├── requirements.txt               # Dependencies
├── setup.sh                       # Setup script
├── README.md                      # This file
├── README_linkedin.md             # Detailed documentation
├── .env.example                   # Environment template
└── .gitignore                     # Git ignore rules
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd LinkedinScraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your LinkedIn credentials
```

## Usage

### Interactive Mode
Run the main scraper for an interactive experience:
```bash
python3 linkedin_scraper.py
```

Choose from:
- **Option 1**: Search for jobs
- **Option 2**: Scrape profiles

### Programmatic Usage

#### Job Search
```python
from linkedin_scraper import LinkedInScraper, JobSearchRequest

# Create scraper instance
scraper = LinkedInScraper(headless=True)

# Create search request
request = JobSearchRequest(
    skills=["Python", "JavaScript"],
    location="San Francisco, CA",
    limit=10
)

# Search for jobs
result = scraper.search_jobs(request)

if result.success:
    for job in result.jobs:
        print(f"{job.title} at {job.company}")
```

#### Profile Scraping
```python
from linkedin_scraper import LinkedInScraper

# Create scraper instance
scraper = LinkedInScraper(headless=True)

# Scrape a profile
profile_url = "https://linkedin.com/in/username"
profile = scraper.scrape_profile(profile_url)

if profile:
    print(f"Name: {profile.name}")
    print(f"Skills: {profile.skills}")
    print(f"Match Score: {profile.skill_match_score}%")
```

### Test Scripts
Run the job search test:
```bash
python3 test_job_search.py
```

## Configuration

### Environment Variables
Create a `.env` file with the following variables (optional):
```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

### Customizing Target Skills
Modify the `target_skills` list in the `LinkedInScraper` class:
```python
scraper = LinkedInScraper()
scraper.target_skills = [
    'Python', 'JavaScript', 'React', 'Node.js',
    'AWS', 'Docker', 'Kubernetes', 'Machine Learning'
]
```

## Features

### Job Search
- **Skills-based filtering**: Search by specific skills
- **Location filtering**: Filter by city, state, or country
- **Experience level**: Entry-level, mid-senior, director, etc.
- **Job type**: Full-time, part-time, contract, etc.
- **Company filtering**: Search within specific companies
- **Result limiting**: Control number of results returned

### Profile Scraping
- **Comprehensive data extraction**: Name, headline, location, experience
- **Skill matching**: Automatic skill comparison and scoring
- **Education extraction**: Academic background
- **Contact information**: Email and profile URLs
- **Excel export**: Export data to spreadsheet format

### Anti-Detection Measures
- **Headless browser support**: Run without GUI
- **User agent spoofing**: Mimic real browser behavior
- **Request delays**: Prevent rate limiting
- **Session management**: Handle login and cookies

## Dependencies

### Core Dependencies
- `selenium>=4.15.0` - Web automation
- `beautifulsoup4>=4.12.0` - HTML parsing
- `pandas>=2.0.0` - Data processing and Excel export
- `openpyxl>=3.1.0` - Excel file handling

### Optional Dependencies
- `openai>=1.3.0` - AI-powered analysis (future feature)
- `anthropic>=0.7.0` - Alternative AI provider (future feature)

## Testing

The project includes comprehensive test scripts:
- `test_job_search.py` - Tests job search functionality
- Built-in validation for data models

## Development

### Code Quality
- Type hints throughout
- Comprehensive error handling
- Logging for debugging
- Clean, maintainable code structure

### Extending the Scraper
The modular design makes it easy to add new features:
- Add new data extraction methods
- Implement additional search filters
- Create new export formats
- Add AI-powered analysis

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - Install Chrome browser
   - Download ChromeDriver from https://chromedriver.chromium.org/

2. **LinkedIn blocking requests**
   - Use headless mode: `scraper = LinkedInScraper(headless=True)`
   - Add delays between requests
   - Use valid LinkedIn credentials

3. **Import errors**
   - Install all dependencies: `pip install -r requirements.txt`
   - Check Python version (3.9+ recommended)

### Performance Tips
- Use headless mode for faster execution
- Limit result counts to reduce processing time
- Add appropriate delays between requests
- Use specific skill filters to narrow results

## License

This project is independent and open source. Use responsibly and in accordance with LinkedIn's terms of service.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Disclaimer

This tool is for educational and research purposes. Please respect LinkedIn's terms of service and robots.txt file. Use responsibly and ethically.
