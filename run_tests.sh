#!/bin/bash
# Script to run tests for Polygon Manager

echo "===================================="
echo "Polygon Manager - Test Runner"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python -m venv venv
fi

# Activate virtual environment
if [ -f "venv/Scripts/activate" ]; then
    # Windows
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    # Linux/Mac
    source venv/bin/activate
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt

echo ""
echo -e "${GREEN}Running API Tests...${NC}"
echo "------------------------------------"
pytest tests/test_api.py -v

echo ""
echo -e "${GREEN}Test Summary${NC}"
echo "------------------------------------"
pytest tests/test_api.py --tb=no -q

echo ""
echo -e "${YELLOW}To run UI tests, ensure the application is running and execute:${NC}"
echo -e "${YELLOW}  pytest tests/test_ui.py${NC}"
echo ""
echo -e "${YELLOW}To run all tests with coverage:${NC}"
echo -e "${YELLOW}  pytest --cov=app --cov-report=html${NC}"
