#!/bin/bash
# Civitai Scraper Installer for Linux/macOS
# This script creates a virtual environment and installs dependencies

echo "========================================"
echo "Civitai Image Prompt Scraper Installer"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    echo ""
    echo "On Ubuntu/Debian: sudo apt-get install python3 python3-venv python3-pip"
    echo "On macOS: brew install python3"
    exit 1
fi

echo "Checking Python version..."
python3 --version

# Check if venv already exists
if [ -d "venv" ]; then
    echo ""
    read -p "Virtual environment already exists. Do you want to recreate it? (y/N): " RECREATE
    if [ "$RECREATE" = "y" ] || [ "$RECREATE" = "Y" ]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Keeping existing virtual environment."
        # Skip to dependency installation
        source venv/bin/activate
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        echo ""
        echo "========================================"
        echo "Installation completed successfully!"
        echo "========================================"
        echo ""
        echo "To run the scraper:"
        echo "  - GUI version: ./run_gui.sh"
        echo "  - CLI version: ./run_cli.sh --base-model \"Flux.1 D\" --max-models 10"
        echo ""
        echo "Or manually activate the virtual environment:"
        echo "  source venv/bin/activate"
        echo ""
        exit 0
    fi
fi

echo ""
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Upgrading pip..."
python -m pip install --upgrade pip

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Making run scripts executable..."
chmod +x run_gui.sh run_cli.sh 2>/dev/null || true

echo ""
echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo ""
echo "To run the scraper:"
echo "  - GUI version: ./run_gui.sh"
echo "  - CLI version: ./run_cli.sh --base-model \"Flux.1 D\" --max-models 10"
echo ""
echo "Or manually activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
