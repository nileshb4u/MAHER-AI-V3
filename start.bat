@echo off
REM ============================================================================
REM MAHER AI - Complete Application Startup Script
REM ============================================================================
REM This script starts both the backend Flask server and frontend Vite dev server
REM ============================================================================

echo.
echo ========================================
echo   MAHER AI - Application Startup
echo ========================================
echo.

REM Check if we're in the correct directory
if not exist "backend\app.py" (
    echo ERROR: backend\app.py not found!
    echo Please run this script from the MAHER_NEW_UI root directory.
    pause
    exit /b 1
)

if not exist "package.json" (
    echo ERROR: package.json not found!
    echo Please run this script from the MAHER_NEW_UI root directory.
    pause
    exit /b 1
)

REM ============================================================================
REM Step 1: Check Backend Dependencies
REM ============================================================================
echo [1/5] Checking backend dependencies...
echo.

if not exist "backend\venv" (
    echo WARNING: Virtual environment not found!
    echo Please run setup.bat first to install dependencies.
    pause
    exit /b 1
)

REM ============================================================================
REM Step 2: Check Frontend Dependencies
REM ============================================================================
echo [2/5] Checking frontend dependencies...
echo.

if not exist "node_modules" (
    echo WARNING: Node modules not found!
    echo Installing frontend dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies!
        pause
        exit /b 1
    )
)

REM ============================================================================
REM Step 3: Check Environment Variables
REM ============================================================================
echo [3/5] Checking environment configuration...
echo.

if not exist "backend\.env" (
    echo WARNING: Backend .env file not found!
    echo Creating from .env.example...
    if exist "backend\.env.example" (
        copy "backend\.env.example" "backend\.env"
        echo Please configure backend\.env with your API keys.
    ) else (
        echo ERROR: backend\.env.example not found!
        pause
        exit /b 1
    )
)

if not exist ".env" (
    echo WARNING: Frontend .env file not found!
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo Created .env from .env.example
    )
)

REM ============================================================================
REM Step 4: Start Backend Server
REM ============================================================================
echo [4/5] Starting backend server...
echo.

REM Start backend in a new window with virtual environment activated
start "MAHER AI - Backend Server" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate.bat && set PORT=8080 && python app.py"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM ============================================================================
REM Step 5: Start Frontend Dev Server
REM ============================================================================
echo [5/5] Starting frontend dev server...
echo.

REM Start frontend in a new window
# Use 'npm run dev -- --host' to ensure it binds to network if needed, though vite config handles it
start "MAHER AI - Frontend Dev Server" cmd /k "cd /d "%~dp0" && npm run dev"

REM Wait for frontend to start
echo Waiting for frontend to initialize...
timeout /t 5 /nobreak >nul

REM ============================================================================
REM Startup Complete
REM ============================================================================
echo.
echo ========================================
echo   MAHER AI - Startup Complete!
echo ========================================
echo.
echo Backend Server:  http://localhost:8080
echo Frontend App:    http://localhost:3000
echo.
echo Admin Password:  maher_admin_2026
echo.
echo Two windows have been opened:
echo   1. Backend Server (Flask) - Port 8080
echo   2. Frontend Dev Server (Vite) - Port 3000
echo.
echo Press Ctrl+C in each window to stop the servers.
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul

REM Open browser
start http://localhost:3000

echo.
echo You can close this window now.
echo The servers will continue running in their own windows.
echo.
pause
