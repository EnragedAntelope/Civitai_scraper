#!/bin/bash
# Launcher for Civitai Scraper CLI (Linux/macOS)

# Check if virtual environment exists
if [ ! -f "venv/bin/python" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run ./install.sh first to set up the environment."
    echo ""
    exit 1
fi

# Activate virtual environment and run CLI with all arguments
source venv/bin/activate
python civitai_scraper.py "$@"
