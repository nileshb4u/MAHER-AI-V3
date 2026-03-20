#!/bin/bash

###############################################################################
# MAHER AI - Production Deployment Script
# This script builds and deploys the MAHER AI application
###############################################################################

set -e  # Exit on error

echo "======================================"
echo "MAHER AI - Production Deployment"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your settings:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Source environment variables
echo -e "${YELLOW}Loading environment variables...${NC}"
export $(grep -v '^#' .env | xargs)

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}ERROR: GEMINI_API_KEY not set in .env file!${NC}"
    exit 1
fi

echo -e "${GREEN}Environment variables loaded successfully${NC}"
echo ""

# Step 1: Install Node.js dependencies
echo -e "${YELLOW}Step 1/6: Installing frontend dependencies...${NC}"
npm install
echo -e "${GREEN}Frontend dependencies installed${NC}"
echo ""

# Step 2: Build frontend
echo -e "${YELLOW}Step 2/6: Building frontend application...${NC}"
npm run build
echo -e "${GREEN}Frontend built successfully to ./dist${NC}"
echo ""

# Step 3: Set up Python virtual environment
echo -e "${YELLOW}Step 3/6: Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${GREEN}Virtual environment already exists${NC}"
fi
echo ""

# Step 4: Activate virtual environment and install Python dependencies
echo -e "${YELLOW}Step 4/6: Installing backend dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
echo -e "${GREEN}Backend dependencies installed${NC}"
echo ""

# Step 5: Test backend
echo -e "${YELLOW}Step 5/6: Testing backend configuration...${NC}"
cd backend
python3 -c "from app import app; print('Backend configuration is valid')"
cd ..
echo -e "${GREEN}Backend configuration validated${NC}"
echo ""

# Step 6: Display next steps
echo -e "${YELLOW}Step 6/6: Deployment preparation complete!${NC}"
echo ""
echo -e "${GREEN}======================================"
echo "Deployment Ready!"
echo "======================================${NC}"
echo ""
echo "To start the production server:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Start the server:"
echo "     cd backend && python wsgi.py"
echo ""
echo "Or use systemd (recommended for production):"
echo "  sudo cp maher-ai.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable maher-ai"
echo "  sudo systemctl start maher-ai"
echo ""
echo "The application will be available at:"
echo "  http://localhost:${PORT:-8080}"
echo ""
echo -e "${YELLOW}Note: For production, configure a reverse proxy (nginx/apache)${NC}"
echo -e "${YELLOW}      and use HTTPS with a valid SSL certificate.${NC}"
echo ""
