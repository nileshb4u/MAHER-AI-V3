@echo off
REM ============================================================================
REM MAHER AI v3 - One-Click Application Startup
REM ============================================================================
REM Starts both backend (Flask/Waitress) and frontend (Vite dev server)
REM Opens the browser automatically when both servers are ready.
REM
REM Usage:
REM   Double-click this file  OR  run from command prompt: start.bat
REM
REM Prerequisites (run setup.bat first if not done):
REM   - Python 3.10+ with venv in backend\venv
REM   - Node.js 18+ with node_modules present
REM   - backend\.env configured with at least one AI provider key
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   MAHER AI v3 - Virtual Maintenance Assistant
echo   Developed by Saudi Aramco Corporate Maintenance Services
echo ============================================================
echo.

REM ------------------------------------------------------------
REM Guard: must be run from the MAHER-AI-V3 root directory
REM ------------------------------------------------------------
if not exist "backend\app.py" (
    echo [ERROR] backend\app.py not found.
    echo         Run this script from the MAHER-AI-V3 root folder.
    pause
    exit /b 1
)
if not exist "package.json" (
    echo [ERROR] package.json not found.
    echo         Run this script from the MAHER-AI-V3 root folder.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM Step 1: Backend virtual environment
REM ------------------------------------------------------------
echo [1/5] Checking Python virtual environment...
if not exist "backend\venv\" (
    echo [ERROR] Virtual environment not found at backend\venv
    echo         Please run setup.bat first.
    pause
    exit /b 1
)
echo        OK - backend\venv found

REM ------------------------------------------------------------
REM Step 2: Frontend node_modules
REM ------------------------------------------------------------
echo [2/5] Checking frontend dependencies...
if not exist "node_modules\" (
    echo        node_modules not found - installing now...
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed. Check your Node.js installation.
        pause
        exit /b 1
    )
)
echo        OK - node_modules found

REM ------------------------------------------------------------
REM Step 3: Environment file
REM ------------------------------------------------------------
echo [3/5] Checking environment configuration...
if not exist "backend\.env" (
    echo [WARNING] backend\.env not found - creating from template...
    (
        echo # ============================================================
        echo # MAHER AI v3 - Environment Configuration
        echo # ============================================================
        echo.
        echo # --- AI Provider (choose one or more; fallback order: gpt-oss -^> metabrain -^> gemini) ---
        echo MODEL_PROVIDER=gpt-oss
        echo.
        echo # GPT-OSS / vLLM (self-hosted, primary)
        echo VLLM_SERVER_URL=
        echo VLLM_MODEL_PATH=/home/cdsw/gpt-oss
        echo.
        echo # MetaBrain (Aramco enterprise AI, secondary)
        echo METABRAIN_CLIENT_ID=
        echo METABRAIN_CLIENT_SECRET=
        echo METABRAIN_BASE_URL=
        echo.
        echo # Gemini (Google AI, last resort)
        echo GEMINI_API_KEY=
        echo.
        echo # --- Server ---
        echo HOST=0.0.0.0
        echo PORT=8080
        echo THREADS=4
        echo.
        echo # --- Security ---
        echo SECRET_KEY=
        echo ALLOWED_ORIGINS=*
        echo ADMIN_PASSWORD=maher_admin_2026
        echo.
        echo # --- Optional: Redis for distributed rate limiting ---
        echo REDIS_URL=
    ) > backend\.env
    echo [WARNING] Created backend\.env template.
    echo           Configure at least one AI provider key before continuing.
    echo.
    echo  Press any key to open backend\.env for editing, then re-run start.bat.
    pause
    start notepad backend\.env
    exit /b 0
)
echo        OK - backend\.env found

REM ------------------------------------------------------------
REM Step 4: Start backend server
REM ------------------------------------------------------------
echo [4/5] Starting backend server (Flask on port 8080)...
start "MAHER AI - Backend" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate.bat && echo. && echo [MAHER AI Backend] Starting on http://localhost:8080 && echo. && python app.py"

echo        Waiting for backend to initialise (8 seconds)...
timeout /t 8 /nobreak >nul

REM ------------------------------------------------------------
REM Step 5: Start frontend dev server
REM ------------------------------------------------------------
echo [5/5] Starting frontend dev server (Vite on port 3000)...
start "MAHER AI - Frontend" cmd /k "cd /d "%~dp0" && echo. && echo [MAHER AI Frontend] Starting on http://localhost:3000 && echo. && npm run dev"

echo        Waiting for frontend to initialise (6 seconds)...
timeout /t 6 /nobreak >nul

REM ------------------------------------------------------------
REM Done
REM ------------------------------------------------------------
echo.
echo ============================================================
echo   MAHER AI v3 - Both servers are starting up!
echo ============================================================
echo.
echo   Backend  (Flask)  -^>  http://localhost:8080
echo   Frontend (Vite)   -^>  http://localhost:3000
echo.
echo   Admin Password    -^>  maher_admin_2026
echo                         (set ADMIN_PASSWORD in backend\.env to change)
echo.
echo   AI Provider chain -^>  GPT-OSS -^> MetaBrain -^> Gemini
echo                         (set MODEL_PROVIDER in backend\.env to change)
echo.
echo   Two terminal windows have been opened.
echo   Press Ctrl+C in each to stop the servers.
echo.
echo   Opening browser to http://localhost:3000 ...
timeout /t 2 /nobreak >nul
start http://localhost:3000
echo.
echo   You can close this window now.
echo.
pause
