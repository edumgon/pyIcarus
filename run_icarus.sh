#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Checking environment for pyIcarus...${NC}"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to check if a Python package is installed
python_package_installed() {
  python3 -c "import $1" >/dev/null 2>&1
}

# Store all command line arguments to pass to the Python script
ARGS="$@"

# Check if Python is installed
if ! command_exists python3; then
  echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
  exit 1
fi

# Check for GTK environment first
if python_package_installed gi; then
  echo -e "${GREEN}GTK environment detected.${NC}"
  
  # Check GTK requirements
  MISSING_PACKAGES=0
  
  # Check for PyGObject
  if ! python3 -c "import gi" 2>/dev/null; then
    echo -e "${RED}PyGObject is not installed.${NC}"
    MISSING_PACKAGES=1
  fi
  
  # Check for requests
  if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${RED}requests module is not installed.${NC}"
    MISSING_PACKAGES=1
  fi
  
  if [ $MISSING_PACKAGES -eq 0 ]; then
    echo -e "${GREEN}All GTK requirements are satisfied. Starting GTK application...${NC}"
    python3 ponto_app_gtk.py $ARGS
    exit 0
  else
    echo -e "${YELLOW}Installing missing requirements...${NC}"
    pip3 install -r requirements.txt
    
    # Check if installation was successful
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}Requirements installed successfully. Starting GTK application...${NC}"
      python3 ponto_app_gtk.py $ARGS
      exit 0
    else
      echo -e "${RED}Failed to install requirements. Please install them manually.${NC}"
      exit 1
    fi
  fi
# Check for PyQt environment
elif python_package_installed PyQt6; then
  echo -e "${GREEN}PyQt environment detected.${NC}"
  
  # Check PyQt requirements
  MISSING_PACKAGES=0
  
  # Check for PyQt6
  if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo -e "${RED}PyQt6 is not installed.${NC}"
    MISSING_PACKAGES=1
  fi
  
  # Check for requests
  if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${RED}requests module is not installed.${NC}"
    MISSING_PACKAGES=1
  fi
  
  # Check for cryptography
  if ! python3 -c "import cryptography" 2>/dev/null; then
    echo -e "${RED}cryptography module is not installed.${NC}"
    MISSING_PACKAGES=1
  fi
  
  if [ $MISSING_PACKAGES -eq 0 ]; then
    echo -e "${GREEN}All PyQt requirements are satisfied. Starting PyQt application...${NC}"
    python3 ponto_app_pyqt.py $ARGS
    exit 0
  else
    echo -e "${YELLOW}Installing missing requirements...${NC}"
    pip3 install -r requirements_pyqt.txt
    
    # Check if installation was successful
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}Requirements installed successfully. Starting PyQt application...${NC}"
      python3 ponto_app_pyqt.py $ARGS
      exit 0
    else
      echo -e "${RED}Failed to install requirements. Please install them manually.${NC}"
      exit 1
    fi
  fi
else
  echo -e "${YELLOW}No GUI environment detected. Installing PyQt by default...${NC}"
  pip3 install -r requirements_pyqt.txt
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}PyQt requirements installed successfully. Starting PyQt application...${NC}"
    python3 ponto_app_pyqt.py $ARGS
    exit 0
  else
    echo -e "${RED}Failed to install PyQt requirements. Please install them manually.${NC}"
    exit 1
  fi
fi
