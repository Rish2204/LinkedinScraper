#!/bin/bash

echo "=== LinkedIn Scraper Quick Test ==="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed!"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo

# Install essential dependencies only
echo "📦 Installing essential dependencies..."
pip3 install selenium beautifulsoup4 pandas openpyxl python-dotenv

# Check if Chrome is installed
if command -v google-chrome &> /dev/null; then
    echo "✅ Chrome found"
elif command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium found"
elif command -v /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome &> /dev/null; then
    echo "✅ Chrome found (macOS)"
else
    echo "⚠️  Chrome not found. You may need to install it manually."
fi

echo
echo "🚀 Ready to test! Run one of these commands:"
echo
echo "1. Quick test (3 profiles):"
echo "   python3 test_scraper.py"
echo
echo "2. Full test (interactive):"
echo "   python3 linkedin_profile_scraper.py"
echo
echo "3. Demo (no browser):"
echo "   python3 linkedin_demo.py"
echo
echo "📝 Note: Make sure to set your LinkedIn credentials:"
echo "   export LINKEDIN_EMAIL='your_email@example.com'"
echo "   export LINKEDIN_PASSWORD='your_password'"
echo
