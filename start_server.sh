#!/bin/bash

# MAHER AI - Production Server Startup Script
# This script starts the production server using Waitress

set -e  # Exit on error

echo "========================================="
echo "  MAHER AI - Starting Production Server"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run the following commands first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r backend/requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  WARNING: backend/.env file not found!"
    echo "   Please create it with your GEMINI_API_KEY"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

# Check if frontend is built
if [ ! -d "dist" ]; then
    echo "⚠️  Frontend not built. Building now..."
    npm install
    npm run build
    echo "✓ Frontend built successfully"
fi

# Change to backend directory
cd backend

# Start the production server
echo ""
echo "✓ Starting production server..."
echo "  Host: ${HOST:-0.0.0.0}"
echo "  Port: ${PORT:-8080}"
echo "  Threads: ${THREADS:-4}"
echo ""
echo "🚀 Server will be available at:"
echo "   http://localhost:${PORT:-8080}"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Run the production server
python run_production.py
