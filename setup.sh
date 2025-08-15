#!/bin/bash

echo "Setting up LinkedIn Scraper..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create output directory
echo "Creating output directory..."
mkdir -p output

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your credentials"
else
    echo ".env file already exists"
fi

echo "Setup complete!"
echo "To activate the environment, run: source venv/bin/activate"
echo "To run the profile scraper, run: python linkedin_profile_scraper.py"
echo "To run the FastAPI server, run: python app.py"
echo "To run the CLI, run: python linkedin_cli.py"
