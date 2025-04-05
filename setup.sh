#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to print step information
print_step() {
    echo -e "${GREEN}[SETUP] $1${NC}"
}

# Function to print errors
print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed. Please install Python3 and try again."
    exit 1
fi

# Check and install python3-venv if needed
if ! dpkg -l | grep -q python3-venv; then
    print_step "Installing python3-venv..."
    sudo apt-get update && sudo apt-get install -y python3-venv
    if [ $? -ne 0 ]; then
        print_error "Failed to install python3-venv. Please install it manually with: sudo apt-get install python3-venv"
        exit 1
    fi
fi

# Remove existing venv if it exists
if [ -d "venv" ]; then
    print_step "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
print_step "Creating virtual environment..."
python3 -m venv venv --clear
if [ $? -ne 0 ]; then
    print_error "Failed to create virtual environment. Please try again with: sudo apt-get install --reinstall python3-venv"
    exit 1
fi

# Ensure correct permissions
chmod -R u+w venv

# Activate virtual environment
print_step "Activating virtual environment..."
. ./venv/bin/activate
if [ ! "$VIRTUAL_ENV" ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
print_step "Upgrading pip..."
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    print_error "Failed to upgrade pip"
    exit 1
fi

# Install requirements
print_step "Installing requirements from requirements.txt..."
pip install fastapi uvicorn streamlit python-dotenv requests httpx pydantic fitz
if [ $? -ne 0 ]; then
    print_error "Failed to install requirements"
    exit 1
fi

print_step "Setup completed successfully!"
echo -e "\nTo run the project:"
echo -e "1. Activate the virtual environment (if not already activated):"
echo -e "   ${GREEN}source venv/bin/activate${NC}"
echo -e "\n2. Start the backend server (in a new terminal):"
echo -e "   ${GREEN}python main_back.py${NC}"
echo -e "\n3. Start the frontend (in another terminal):"
echo -e "   ${GREEN}python main_front.py${NC}"
