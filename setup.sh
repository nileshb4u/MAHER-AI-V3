#!/bin/bash

# MAHER AI - Complete Setup Script
# This script sets up the entire application in one go

set -e  # Exit on any error

echo "=========================================="
echo "  MAHER AI - Automated Setup"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_step() {
    echo ""
    echo -e "${GREEN}==>${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi
print_success "Node.js found: $(node --version)"

if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi
print_success "npm found: $(npm --version)"

# Step 1: Create Python virtual environment
print_step "Step 1: Setting up Python virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists, skipping creation"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

# Step 2: Install Python dependencies
print_step "Step 2: Installing Python backend dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r backend/requirements.txt
print_success "Backend dependencies installed"

# Step 3: Initialize database
print_step "Step 3: Initializing SQLite database..."
cd backend
python seed_db.py
cd ..
print_success "Database initialized and seeded with system agents"

# Step 4: Check for .env file
print_step "Step 4: Checking environment configuration..."

if [ ! -f "backend/.env" ]; then
    print_warning ".env file not found. Creating template..."
    cat > backend/.env << 'EOF'
# MAHER AI Environment Configuration

# Required: Your Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8080
THREADS=4

# Optional: Security
SECRET_KEY=
ALLOWED_ORIGINS=*

# Optional: HTTPS (if using reverse proxy)
USE_HTTPS=false
EOF
    print_warning "Created backend/.env template. PLEASE ADD YOUR GEMINI_API_KEY!"
    echo ""
    echo "Edit backend/.env and add your Gemini API key before running the server."
    echo ""
else
    print_success ".env file exists"

    # Check if API key is set
    if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" backend/.env || grep -q "GEMINI_API_KEY=$" backend/.env; then
        print_warning "GEMINI_API_KEY not configured in backend/.env"
        echo "Please add your Gemini API key to backend/.env before running the server."
    else
        print_success "GEMINI_API_KEY appears to be configured"
    fi
fi

# Step 5: Install frontend dependencies
print_step "Step 5: Installing frontend dependencies..."
npm install
print_success "Frontend dependencies installed"

# Step 6: Build frontend
print_step "Step 6: Building frontend for production..."
npm run build
print_success "Frontend built successfully"

# Step 7: Create data directory
print_step "Step 7: Ensuring directories exist..."
mkdir -p backend/data
mkdir -p backend/knowledge_storage
print_success "Directories created"

# Final summary
echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
print_success "Database: backend/data/maher_ai.db"
print_success "System agents: 6 agents loaded"
print_success "Frontend: Built and ready in dist/"
echo ""
echo "Next steps:"
echo "  1. Ensure your Gemini API key is set in backend/.env"
echo "  2. Start the server:"
echo ""
echo "     For Linux/Mac:"
echo "     ./start_server.sh"
echo ""
echo "     For Windows:"
echo "     start_server.bat"
echo ""
echo "     Or manually:"
echo "     source venv/bin/activate"
echo "     cd backend"
echo "     python run_production.py"
echo ""
echo "  3. Open http://localhost:8080 in your browser"
echo ""
echo "=========================================="
