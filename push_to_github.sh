#!/bin/bash

echo "Pushing LinkedIn Scraper to GitHub..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all files
echo "Adding files to git..."
git add .

# Commit changes
echo "Committing changes..."
git commit -m "Complete LinkedIn scraper migration from Pravis Boutique

- Profile scraping functionality
- Job search API endpoints
- FastAPI standalone server
- CLI interface
- Comprehensive test suite
- Documentation and setup scripts"

# Add remote if not exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "Adding remote origin..."
    git remote add origin https://github.com/Rish2204/LinkedinScraper.git
fi

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo "LinkedIn Scraper successfully pushed to GitHub!"
echo "Repository: https://github.com/Rish2204/LinkedinScraper.git"
