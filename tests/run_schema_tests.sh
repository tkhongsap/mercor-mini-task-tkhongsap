#!/bin/bash
#
# Test runner script for Airtable schema validation tests
#
# This script:
# 1. Activates the virtual environment
# 2. Verifies Airtable credentials
# 3. Runs the schema integration tests
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Airtable Schema Setup Test Runner"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}ERROR: .env file not found${NC}"
    echo "Please create a .env file with your Airtable credentials"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}Installing pytest...${NC}"
    pip install pytest>=7.4.0
fi

# Run auth test first
echo ""
echo -e "${YELLOW}Step 1: Verifying Airtable credentials...${NC}"
python tests/test_auth.py

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}ERROR: Authentication failed${NC}"
    echo "Please check your .env file and Airtable credentials"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Authentication successful${NC}"
echo ""

# Run the schema tests
echo "=========================================="
echo -e "${YELLOW}Step 2: Running Schema Integration Tests${NC}"
echo "=========================================="
echo ""
echo "Note: These tests will create temporary tables"
echo "in your Airtable base and clean them up after."
echo ""

# Run pytest with verbose output
pytest tests/test_setup_airtable_schema.py -v --tb=short

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo "=========================================="
    echo ""
    echo "Your schema setup script is working correctly."
    echo "All tables are created with proper field types,"
    echo "relationships, and configurations."
else
    echo ""
    echo "=========================================="
    echo -e "${RED}✗ Some tests failed${NC}"
    echo "=========================================="
    echo ""
    echo "Please review the test output above to see"
    echo "which schema validations failed."
    exit 1
fi


