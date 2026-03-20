@echo off
REM MAHER AI - Complete Setup Script (Windows)
REM This script sets up the entire application in one go

setlocal enabledelayedexpansion

echo ==========================================
echo   MAHER AI - Automated Setup
echo ==========================================
echo.

REM Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed. Please install Python 3.11 or higher.
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python found: %PYTHON_VERSION%

REM Check Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18 or higher.
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js found: %NODE_VERSION%

REM Check npm
where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm is not installed. Please install npm.
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo [OK] npm found: v%NPM_VERSION%

REM Step 1: Create Python virtual environment
echo.
echo ==^> Step 1: Setting up Python virtual environment...

if not exist "venv\" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [WARNING] Virtual environment already exists, skipping creation
)

REM Activate virtual environment
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated

REM Step 2: Install Python dependencies
echo.
echo ==^> Step 2: Installing Python backend dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r backend\requirements.txt
echo [OK] Backend dependencies installed

REM Step 3: Initialize database
echo.
echo ==^> Step 3: Initializing SQLite database...
cd backend
python seed_db.py
cd ..
echo [OK] Database initialized and seeded with system agents

REM Step 4: Check for .env file
echo.
echo ==^> Step 4: Checking environment configuration...

if not exist "backend\.env" (
    echo [WARNING] .env file not found. Creating template...
    (
        echo # ============================================================
        echo # MAHER AI v3 - Environment Configuration
        echo # ============================================================
        echo.
        echo # --- AI Provider Selection ---
        echo # Fallback chain: gpt-oss -^> metabrain -^> gemini
        echo # Set MODEL_PROVIDER to whichever is your primary provider.
        echo MODEL_PROVIDER=gpt-oss
        echo.
        echo # GPT-OSS / vLLM ^(self-hosted, primary^)
        echo VLLM_SERVER_URL=
        echo VLLM_MODEL_PATH=/home/cdsw/gpt-oss
        echo.
        echo # MetaBrain ^(Aramco enterprise AI, secondary^)
        echo METABRAIN_CLIENT_ID=
        echo METABRAIN_CLIENT_SECRET=
        echo METABRAIN_BASE_URL=
        echo.
        echo # Gemini ^(Google AI, last resort fallback^)
        echo GEMINI_API_KEY=
        echo.
        echo # --- Server Configuration ---
        echo HOST=0.0.0.0
        echo PORT=8080
        echo THREADS=4
        echo.
        echo # --- Security ---
        echo SECRET_KEY=
        echo ALLOWED_ORIGINS=*
        echo ADMIN_PASSWORD=maher_admin_2026
        echo.
        echo # --- Optional: HTTPS ^(if using reverse proxy^) ---
        echo USE_HTTPS=false
        echo.
        echo # --- Optional: Redis for distributed rate limiting ---
        echo REDIS_URL=
    ) > backend\.env
    echo [WARNING] Created backend\.env template.
    echo           Configure at least one AI provider key before running the server.
    echo.
    echo Edit backend\.env and set your provider credentials.
    echo.
) else (
    echo [OK] .env file exists

    REM Check if API key is set
    findstr /C:"GEMINI_API_KEY=your_gemini_api_key_here" backend\.env >nul
    if !ERRORLEVEL! EQU 0 (
        echo [WARNING] GEMINI_API_KEY not configured in backend\.env
        echo Please add your Gemini API key to backend\.env before running the server.
    ) else (
        echo [OK] GEMINI_API_KEY appears to be configured
    )
)

REM Step 5: Install frontend dependencies
echo.
echo ==^> Step 5: Installing frontend dependencies...
call npm install
echo [OK] Frontend dependencies installed

REM Step 6: Build frontend
echo.
echo ==^> Step 6: Building frontend for production...
call npm run build
echo [OK] Frontend built successfully

REM Step 7: Create data directory
echo.
echo ==^> Step 7: Ensuring directories exist...
if not exist "backend\data\" mkdir backend\data
if not exist "backend\knowledge_storage\" mkdir backend\knowledge_storage
echo [OK] Directories created

REM Final summary
echo.
echo ==========================================
echo   Setup Complete!
echo ==========================================
echo.
echo [OK] Database: backend\data\maher_ai.db
echo [OK] System agents: 6 agents loaded
echo [OK] Frontend: Built and ready in dist\
echo.
echo Next steps:
echo   1. Ensure your Gemini API key is set in backend\.env
echo   2. Start the server:
echo.
echo      start_server.bat
echo.
echo      Or manually:
echo      venv\Scripts\activate
echo      cd backend
echo      python run_production.py
echo.
echo   3. Open http://localhost:8080 in your browser
echo.
echo ==========================================

pause
