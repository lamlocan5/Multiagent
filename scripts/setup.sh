#!/bin/bash
# Setup script for the multiagent system

# Set script to exit on error
set -e

echo "Setting up Multiagent System..."

# Create necessary directories
mkdir -p logs
mkdir -p data/chroma
mkdir -p data/uploads/audio
mkdir -p data/uploads/images
mkdir -p data/uploads/documents

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d "." -f 1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d "." -f 2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "Python 3.9 or higher is required. Found Python $PYTHON_VERSION."
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -e .

# Check for required system dependencies
if ! command -v tesseract &> /dev/null; then
    echo "Warning: Tesseract OCR is not installed. Vietnamese OCR functionality may be limited."
    echo "Please install Tesseract with Vietnamese language support for full functionality."
fi

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit the .env file with your API keys and settings."
fi

# Check for UI dependencies
if [ -d "ui" ]; then
    echo "Setting up UI components..."
    if ! command -v node &> /dev/null; then
        echo "Warning: Node.js is not installed. UI development will not be available."
        echo "Please install Node.js to develop the UI components."
    else
        cd ui
        npm install
        cd ..
    fi
fi

echo "Setup complete!"
echo "------------------------------------"
echo "Next steps:"
echo "1. Edit the .env file with your API keys"
echo "2. Run the system with: source venv/bin/activate && python -m src.main"
echo "3. Access the API documentation at: http://localhost:8000/docs"
echo "------------------------------------" 