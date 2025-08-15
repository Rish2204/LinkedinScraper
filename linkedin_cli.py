#!/usr/bin/env python3
"""
LinkedIn Job Search CLI
Command-line interface for searching LinkedIn jobs based on skills
"""
import argparse
import asyncio
import json
import sys
from typing import List, Optional

# Note: In a real deployment, you'd need to install the dependencies
# For this demo, we'll create a mock version that shows the functionality

class MockLinkedInJobSearcher:
    """Mock LinkedIn job searcher for demonstration"""
    
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search"
    
    async def search_jobs(self, skills: List[str], location: Optional[str] = None,
                         experience_level: Optional[str] = None, 
                         job_type: Optional[str] = None,
                         limit: int = 10) -> dict:
        """Mock job search that returns sample data"""
        
        # Simulate search delay
        print(f"🔍 Searching LinkedIn for jobs with skills: {', '.join(skills)}")
        if location:
            print(f"📍 Location: {location}")
        if experience_level:
            print(f"👔 Experience Level: {experience_level}")
        if job_type:
            print(f"💼 Job Type: {job_type}")
        print(f"📊 Limit: {limit}")
        print()
        
        # Mock job results
        mock_jobs = [
            {
                "title": f"Senior {skills[0]} Developer",
                "company": "Tech Corporation",
                "location": location or "San Francisco, CA",
                "description": f"Looking for an experienced {skills[0]} developer to join our team...",
                "requirements": [
                    f"5+ years of {skills[0]} experience",
                    "Strong problem-solving skills",
                    "Experience with modern frameworks"
                ],
                "salary_range": "$120,000 - $180,000",
                "job_type": job_type or "full_time",
                "posted_date": "2024-08-14",
                "linkedin_url": "https://www.linkedin.com/jobs/view/123456789",
                "skills_matched": skills[:2]  # First 2 skills
            },
            {
                "title": f"{skills[0]} Engineer",
                "company": "Innovation Labs",
                "location": location or "Remote",
                "description": f"Join our team to build amazing {skills[0]} applications...",
                "requirements": [
                    f"3+ years of {skills[0]} experience",
                    "Bachelor's degree in Computer Science",
                    "Experience with agile methodologies"
                ],
                "salary_range": "$90,000 - $140,000",
                "job_type": job_type or "full_time",
                "posted_date": "2024-08-13",
                "linkedin_url": "https://www.linkedin.com/jobs/view/987654321",
                "skills_matched": [skills[0]]
            }
        ]
        
        # Limit results
        jobs = mock_jobs[:limit]
        
        return {
            "success": True,
            "total_jobs_found": len(jobs),
            "jobs": jobs,
            "search_query": {
                "skills": skills,
                "location": location,
                "experience_level": experience_level,
                "job_type": job_type,
                "limit": limit
            },
            "message": f"Successfully found {len(jobs)} job listings"
        }


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Search LinkedIn for jobs based on skillset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for Python jobs
  python linkedin_cli.py -s Python

  # Search for multiple skills in specific location
  python linkedin_cli.py -s Python FastAPI Django -l "San Francisco, CA"

  # Search with experience level and job type
  python linkedin_cli.py -s JavaScript React -l Remote -e mid_senior -j full_time

  # Limit results and output as JSON
  python linkedin_cli.py -s "Machine Learning" Python -l "New York, NY" --limit 5 --json
        """
    )
    
    parser.add_argument(
        '-s', '--skills',
        nargs='+',
        required=True,
        help='Skills to search for (e.g., Python FastAPI Django)'
    )
    
    parser.add_argument(
        '-l', '--location',
        help='Job location (e.g., "San Francisco, CA", "Remote")'
    )
    
    parser.add_argument(
        '-e', '--experience-level',
        choices=['internship', 'entry_level', 'associate', 'mid_senior', 'director'],
        help='Experience level filter'
    )
    
    parser.add_argument(
        '-j', '--job-type',
        choices=['full_time', 'part_time', 'contract', 'temporary', 'volunteer'],
        help='Job type filter'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum number of jobs to return (default: 10)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    return parser.parse_args()


def format_job_output(job: dict, verbose: bool = False) -> str:
    """Format a single job for console output"""
    output = []
    output.append(f"📋 {job['title']}")
    output.append(f"🏢 {job['company']}")
    output.append(f"📍 {job['location']}")
    
    if job.get('salary_range'):
        output.append(f"💰 {job['salary_range']}")
    
    if job.get('posted_date'):
        output.append(f"📅 Posted: {job['posted_date']}")
    
    if job.get('skills_matched'):
        output.append(f"🎯 Matched Skills: {', '.join(job['skills_matched'])}")
    
    if verbose and job.get('description'):
        desc = job['description'][:200] + "..." if len(job['description']) > 200 else job['description']
        output.append(f"📝 {desc}")
    
    if verbose and job.get('requirements'):
        output.append("📋 Requirements:")
        for req in job['requirements'][:3]:  # Show first 3 requirements
            output.append(f"   • {req}")
    
    if job.get('linkedin_url'):
        output.append(f"🔗 {job['linkedin_url']}")
    
    return "\n".join(output)


async def main():
    """Main CLI function"""
    args = parse_arguments()
    
    # Create searcher instance
    searcher = MockLinkedInJobSearcher()
    
    try:
        # Perform job search
        results = await searcher.search_jobs(
            skills=args.skills,
            location=args.location,
            experience_level=args.experience_level,
            job_type=args.job_type,
            limit=args.limit
        )
        
        if args.json:
            # Output as JSON
            print(json.dumps(results, indent=2))
        else:
            # Format for console output
            if results['success']:
                print(f"✅ {results['message']}")
                print(f"📊 Found {results['total_jobs_found']} jobs")
                print("=" * 60)
                
                for i, job in enumerate(results['jobs'], 1):
                    print(f"\n[{i}] {format_job_output(job, args.verbose)}")
                    print("-" * 60)
                
                # Summary
                print(f"\n📈 Search Summary:")
                print(f"   Skills: {', '.join(args.skills)}")
                if args.location:
                    print(f"   Location: {args.location}")
                if args.experience_level:
                    print(f"   Experience: {args.experience_level}")
                if args.job_type:
                    print(f"   Job Type: {args.job_type}")
                print(f"   Results: {len(results['jobs'])}/{args.limit}")
            else:
                print(f"❌ Search failed: {results['message']}")
                return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Search interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error during job search: {e}")
        return 1


if __name__ == "__main__":
    # Run the CLI
    exit_code = asyncio.run(main())
    sys.exit(exit_code)