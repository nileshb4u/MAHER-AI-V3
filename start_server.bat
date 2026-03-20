@echo off
REM MAHER AI - Production Server Startup Script (Windows)
REM This script starts the production server using Waitress

echo =========================================
echo   MAHER AI - Starting Production Server
echo =========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found!
    echo    Please run the following commands first:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r backend\requirements.txt
    exit /b 1
)

REM Activate virtual environment
echo ✓ Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist "backend\.env" (
    echo ⚠️  WARNING: backend\.env file not found!
    echo    Please create it with your GEMINI_API_KEY
    echo.
    pause
)

REM Check if frontend is built
if not exist "dist\" (
    echo ⚠️  Frontend not built. Building now...
    call npm install
    call npm run build
    echo ✓ Frontend built successfully
)

REM Change to backend directory
cd backend

REM Start the production server
echo.
echo ✓ Starting production server...
echo   Host: %HOST% (default: 0.0.0.0)
echo   Port: %PORT% (default: 8080)
echo   Threads: %THREADS% (default: 4)
echo.
echo 🚀 Server will be available at:
echo    http://localhost:8080
echo.
echo Press CTRL+C to stop the server
echo.

REM Run the production server
python run_production.py
