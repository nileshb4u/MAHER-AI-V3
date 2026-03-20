# Build Enterprise Package Script
# Automates the creation of a standalone portable Python package for Windows Server

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# --- CONFIGURATION ---
$PYTHON_VERSION = "3.10.11"
$PYTHON_URL = "https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-embed-amd64.zip"
$BUILD_DIR = Join-Path (Get-Location) "maher_ai_enterprise_build"
$RUNTIME_DIR = Join-Path $BUILD_DIR "runtime"
$SITE_PACKAGES = Join-Path $BUILD_DIR "site-packages"
$APP_DIR = Join-Path $BUILD_DIR "app"
$ZIP_NAME = "MAHER_AI_Enterprise_Package.zip"

Write-Host "=========================================="
Write-Host "MAHER AI - Enterprise Package Builder"
Write-Host "Target Python: $PYTHON_VERSION (Embeddable)"
Write-Host "Build Dir: $BUILD_DIR"
Write-Host "=========================================="

# 1. Clean Build Directory
if (Test-Path $BUILD_DIR) {
    Write-Host "[INFO] Cleaning previous build..."
    Remove-Item -Path $BUILD_DIR -Recurse -Force
}
New-Item -ItemType Directory -Path $BUILD_DIR | Out-Null
New-Item -ItemType Directory -Path $RUNTIME_DIR | Out-Null
New-Item -ItemType Directory -Path $SITE_PACKAGES | Out-Null
New-Item -ItemType Directory -Path $APP_DIR | Out-Null
New-Item -ItemType Directory -Path "$APP_DIR\backend" | Out-Null
New-Item -ItemType Directory -Path "$APP_DIR\dist" | Out-Null
New-Item -ItemType Directory -Path "$BUILD_DIR\logs" | Out-Null
New-Item -ItemType Directory -Path "$BUILD_DIR\config" | Out-Null

# 2. Download and Extract Embeddable Python
$zipFile = Join-Path $BUILD_DIR "python.zip"
Write-Host "[INFO] Downloading Python Embeddable Package..."
Invoke-WebRequest -Uri $PYTHON_URL -OutFile $zipFile


Write-Host "[INFO] Extracting Python Runtime..."
Expand-Archive -Path $zipFile -DestinationPath $RUNTIME_DIR -Force
Remove-Item $zipFile
$PYTHON_EXE = Join-Path $RUNTIME_DIR "python.exe"

# 2a. Ensure pip is installed
Write-Host "[INFO] Downloading get-pip.py..."
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "$BUILD_DIR\get-pip.py"
Write-Host "[INFO] Installing pip..."
& "$PYTHON_EXE" "$BUILD_DIR\get-pip.py" --no-warn-script-location


# 3. Configure python._pth to enable site-packages
$pthFile = Join-Path $RUNTIME_DIR "python310._pth"
Write-Host "[INFO] Configuring $pthFile..."
$content = Get-Content $pthFile
$newContent = @()
foreach ($line in $content) {
    if ($line -match "#import site") {
        $newContent += "import site" # Uncomment
    }
    else {
        $newContent += $line
    }
}
# Add site-packages path if not present (usually implies adding ..\site-packages)
if (-not ($newContent -contains "..\site-packages")) {
    $newContent += "..\site-packages"
}
$newContent | Set-Content $pthFile

# 4. Install Dependencies
Write-Host "[INFO] Installing Dependencies into site-packages..."
# We use the SYSTEM python to install into the TARGET site-packages
Write-Host "[INFO] Installing Python dependencies..."
# Force install specific version of python-dotenv to ensure it's fresh
# Use simple execution
$installDotEnvArgs = "-m pip install python-dotenv==1.0.1 --target `"$SITE_PACKAGES`" --no-cache-dir --upgrade"
Write-Host "[EXEC] $PYTHON_EXE $installDotEnvArgs"
Start-Process -FilePath "$PYTHON_EXE" -ArgumentList "$installDotEnvArgs" -Wait -NoNewWindow

$installReqsArgs = "-m pip install -r `"backend\requirements.txt`" --target `"$SITE_PACKAGES`" --no-compile --only-binary=:all: --platform win_amd64 --python-version 310"
Write-Host "[EXEC] $PYTHON_EXE $installReqsArgs"
Start-Process -FilePath "$PYTHON_EXE" -ArgumentList "$installReqsArgs" -Wait -NoNewWindow

if ($LASTEXITCODE -ne 0) {
    Write-Warning "pip install might have had issues. Please check output above."
}

# 5. Copy Application Code
Write-Host "[INFO] Copying Backend..."
Copy-Item -Path "backend\*" -Destination "$APP_DIR\backend" -Recurse -Exclude "__pycache__", "venv", ".env"

Write-Host "[INFO] Checking Frontend (dist)..."
if (-not (Test-Path "dist")) {
    Write-Warning "[WARN] 'dist' folder not found. Attempting to build frontend..."
    
    if (Get-Command "npm" -ErrorAction SilentlyContinue) {
        Write-Host "[INFO] Running 'npm install'..."
        cmd /c "npm install"
        
        Write-Host "[INFO] Running 'npm run build'..."
        cmd /c "npm run build"
        
        if (-not (Test-Path "dist")) {
            Write-Error "[ERROR] Frontend build failed! 'dist' folder still missing."
        }
    }
    else {
        Write-Error "[ERROR] 'dist' folder missing and 'npm' not found. Cannot build frontend."
    }
}

Write-Host "[INFO] Copying Frontend (dist)..."
Copy-Item -Path "dist\*" -Destination "$APP_DIR\dist" -Recurse

# 6. Create run_local.bat (No Admin Needed - Localhost Only)
Write-Host "[INFO] Creating run_local.bat..."
$batContentLocal = @"
@echo off
setlocal
title MAHER AI - Local Mode (127.0.0.1)

:: --- CONFIGURATION ---
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "APP_DIR=%ROOT%app\backend"
set "PYTHON=%RUNTIME%\python.exe"
set "HOST=127.0.0.1"
set "PORT=8080"

:: --- ENVIRONMENT ---
set "PYTHONPATH=%ROOT%site-packages;%APP_DIR%"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUNBUFFERED=1"

:: --- EXECUTION ---
echo [INFO] Moving to application directory...
cd /d "%APP_DIR%"

echo [INFO] Starting MAHER AI (Local Mode)...
echo [INFO] Accessible at: http://127.0.0.1:8080

:: Open browser after 5 seconds
timeout /t 5 /nobreak >nul
start http://127.0.0.1:8080

"%PYTHON%" "wsgi.py"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Application crashed with exit code %ERRORLEVEL%
    pause
)
"@
$batContentLocal | Set-Content (Join-Path $BUILD_DIR "run_local.bat")

# 6b. Create run_network.bat (Admin/Firewall Needed - Network Accessible)
Write-Host "[INFO] Creating run_network.bat..."
$batContentNetwork = @"
@echo off
setlocal
title MAHER AI - Network Mode (0.0.0.0)

:: --- CONFIGURATION ---
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "APP_DIR=%ROOT%app\backend"
set "PYTHON=%RUNTIME%\python.exe"
set "HOST=0.0.0.0"
set "PORT=8080"

:: --- ENVIRONMENT ---
set "PYTHONPATH=%ROOT%site-packages;%APP_DIR%"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUNBUFFERED=1"

:: --- EXECUTION ---
echo [INFO] Moving to application directory...
cd /d "%APP_DIR%"

echo [INFO] Starting MAHER AI (Network Mode)...
echo [WARN] This mode may trigger Windows Firewall (requires Admin).
"%PYTHON%" "wsgi.py"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Application crashed with exit code %ERRORLEVEL%
    pause
)
"@
$batContentNetwork | Set-Content (Join-Path $BUILD_DIR "run_network.bat")

# 6c. Create run_custom_port.bat (Interactive Port Selection)
Write-Host "[INFO] Creating run_custom_port.bat..."
$batContentCustom = @"
@echo off
setlocal
title MAHER AI - Custom Port

echo ============================================================================
echo MAHER AI - Custom Port Startup
echo ============================================================================
echo.
echo This script allows you to run MAHER AI on a specific port.
echo Useful if the default port (8080) is blocked by a firewall.
echo.

:ASK
set /p PORT_INPUT="Enter desired port (e.g., 8080, 3000, 9090): "
if "%PORT_INPUT%"=="" goto ASK

:: --- CONFIGURATION ---
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "APP_DIR=%ROOT%app\backend"
set "PYTHON=%RUNTIME%\python.exe"
set "HOST=127.0.0.1"
set "PORT=%PORT_INPUT%"

:: --- ENVIRONMENT ---
set "PYTHONPATH=%ROOT%site-packages;%APP_DIR%"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUNBUFFERED=1"

:: --- EXECUTION ---
echo [INFO] Moving to application directory...
cd /d "%APP_DIR%"

echo [INFO] Starting MAHER AI on Port %PORT%...
echo [INFO] Accessible at: http://127.0.0.1:%PORT%

:: Open browser after 5 seconds
timeout /t 5 /nobreak >nul
start http://127.0.0.1:%PORT%

"%PYTHON%" "wsgi.py"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Application crashed with exit code %ERRORLEVEL%
    pause
)
"@
$batContentCustom | Set-Content (Join-Path $BUILD_DIR "run_custom_port.bat")

# 6d. Create run_port_80.bat (Standard HTTP Port)
Write-Host "[INFO] Creating run_port_80.bat..."
$batContent80 = @"
@echo off
setlocal
title MAHER AI - Port 80 (Standard HTTP)

:: --- CONFIGURATION ---
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "APP_DIR=%ROOT%app\backend"
set "PYTHON=%RUNTIME%\python.exe"
set "HOST=0.0.0.0"
set "PORT=80"

:: --- ENVIRONMENT ---
set "PYTHONPATH=%ROOT%site-packages;%APP_DIR%"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUNBUFFERED=1"

:: --- EXECUTION ---
echo [INFO] Moving to application directory...
cd /d "%APP_DIR%"

echo [INFO] Starting MAHER AI on Standard Port 80...
echo [INFO] NOTE: This may require Administrator privileges.
echo [INFO] Accessible at: http://localhost

:: Open browser after 5 seconds
timeout /t 5 /nobreak >nul
start http://localhost

"%PYTHON%" "wsgi.py"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Application crashed with exit code %ERRORLEVEL%
    echo [TIP] If you see "Permission denied", right-click this script and "Run as Administrator".
    echo [TIP] If you see "Address already in use", disable IIS (World Wide Web Publishing Service).
    pause
)
"@
$batContent80 | Set-Content (Join-Path $BUILD_DIR "run_port_80.bat")

# 6e. Create run_https.bat (HTTPS Support)
Write-Host "[INFO] Creating run_https.bat..."
$batContentHttps = @"
@echo off
setlocal
title MAHER AI - Network HTTPS Mode (0.0.0.0:443)

:: --- CONFIGURATION ---
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "APP_DIR=%ROOT%app\backend"
set "PYTHON=%RUNTIME%\python.exe"
set "HOST=0.0.0.0"
set "PORT=443"

:: --- ENVIRONMENT ---
set "PYTHONPATH=%ROOT%site-packages;%APP_DIR%"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUNBUFFERED=1"

:: --- EXECUTION ---
echo [INFO] Moving to application directory...
cd /d "%APP_DIR%"

echo [INFO] Checking for SSL Certificates...
if not exist "server.crt" (
    echo [WARN] Missing server.crt!
    echo [INFO] Falling back to standard execution...
)

echo [INFO] Starting MAHER AI (HTTPS Mode)...
echo [WARN] This mode requires Administrator privileges (Port 443).
echo [INFO] Accessible remotely at: https://YOUR_SERVER_IP
"%PYTHON%" "wsgi.py"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Application crashed with exit code %ERRORLEVEL%
    pause
)
"@
$batContentHttps | Set-Content (Join-Path $BUILD_DIR "run_https.bat")

# 6.5 Create MetaBrain Test Script
Write-Host "[INFO] Creating run_metabrain_test.bat..."
$batContentTest = @"
@echo off
setlocal
title MAHER AI - MetaBrain Connectivity Test

:: --- CONFIGURATION ---
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "APP_DIR=%ROOT%app\backend"
set "PYTHON=%RUNTIME%\python.exe"

:: --- ENVIRONMENT ---
set "PYTHONPATH=%ROOT%site-packages;%APP_DIR%"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUNBUFFERED=1"

:: --- EXECUTION ---
echo [INFO] Running MetaBrain Connectivity Test...
echo [INFO] Reading credentials from config\.env ...
echo.

cd /d "%APP_DIR%"
"%PYTHON%" "test_metabrain.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Test script failed with exit code %ERRORLEVEL%
) else (
    echo.
    echo [SUCCESS] Test script completed.
)

pause
"@
$batContentTest | Set-Content (Join-Path $BUILD_DIR "run_metabrain_test.bat")

# 7. Copy Config
if (Test-Path ".env") {
    Copy-Item ".env" "$BUILD_DIR\config\.env"
}
elseif (Test-Path ".env.example") {
    Copy-Item ".env.example" "$BUILD_DIR\config\.env"
}

# 8. Create README.txt (Instructions for Server Admin)
Write-Host "[INFO] Creating README.txt..."
$readmeContent = @"
MAHER AI - Enterprise Edition
=============================

INSTALLATION:
1. Extract this zip file to a folder (e.g., C:\Apps\MAHER_AI).
2. Ensure you have Write permissions to this folder (for logs).

RUNNING:
1. Double-click 'run_local.bat' (Default, Port 8080).
2. Or 'run_custom_port.bat' to choose a port (e.g., 3000).
3. The black console window must stay open.
4. Your browser should open automatically.

TROUBLESHOOTING:
- If 'Address already in use', try 'run_custom_port.bat' with a different port.
- If run.bat fails, read MANUAL_START_GUIDE.txt.
- Check 'logs' folder for errors.
- Ensure 'Visual C++ Redistributable' is installed on the target machine.
"@
$readmeContent | Set-Content (Join-Path $BUILD_DIR "README.txt")

# 8b. Create setup_firewall.bat (Optional - One time run as Admin)
Write-Host "[INFO] Creating setup_firewall.bat..."
$fwContent = @"
@echo off
verify >nul
title MAHER AI - Firewall Setup
echo Requesting Admin Rights...
:: Check for admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Must run as Administrator.
    pause
    exit /b
)

echo [INFO] Opening Port 8080 for MAHER AI...
netsh advfirewall firewall add rule name="MAHER_AI_8080" dir=in action=allow protocol=TCP localport=8080 profile=any

if %errorLevel% equ 0 (
    echo [SUCCESS] Port 8080 is now open!
    echo You can now run 'run_network.bat'.
) else (
    echo [ERROR] Failed to open port.
)
pause
"@
$fwContent | Set-Content (Join-Path $BUILD_DIR "setup_firewall.bat")

# 8c. Create Detailed MANUAL_START_GUIDE.txt (Generated)
Write-Host "[INFO] Creating MANUAL_START_GUIDE.txt..."
$manualGuide = @"
MAHER AI - MANUAL STARTUP GUIDE (NO .BAT FILES)
===============================================

If security policies block .bat files, follow these steps to run the application manually from Command Prompt.

PHASE 1: OPEN FIREWALL (One-Time Setup)
---------------------------------------
(Requires Admin Rights. If you cannot get Admin rights, ask IT to "Open TCP Port 8080 for Inbound Traffic".)

1. Open Command Prompt as Administrator (Right-click -> Run as Administrator).
2. Paste this command and hit Enter:
   netsh advfirewall firewall add rule name="MAHER_AI_8080" dir=in action=allow protocol=TCP localport=8080 profile=any

PHASE 2: START THE SERVER (Network Mode)
----------------------------------------
1. Open Command Prompt (Normal or Admin).

2. Navigate to the extracted folder (e.g., C:\Apps\MAHER_AI):
   cd C:\Apps\MAHER_AI

3. Configure the Environment (Copy and Paste this line):
   set PYTHONPATH=.\site-packages;.\app\backend

4. Start the Server (Copy and Paste this line):
   .\runtime\python.exe .\app\backend\wsgi.py

5. CONFIRMATION:
   You should see: "Serving on http://0.0.0.0:8080"

6. ACCESS:
   - From this machine: http://localhost:8080
   - From network:      http://YOUR_SERVER_IP:8080

TROUBLESHOOTING
---------------
ERROR: "ModuleNotFoundError: No module named 'app'"
FIX: You skipped Step 3 (set PYTHONPATH).

ERROR: "Address already in use"
FIX: Another app is using Port 8080.
     Run this manual command instead to change port:
     set PORT=9090 && .\runtime\python.exe .\app\backend\wsgi.py

ERROR: "Access Denied" (Logs)
FIX: Move the folder out of "Program Files" to "C:\Users\Public".

ERROR: "Content is being blocked" (Internet Explorer)
FIX: This is "IE Enhanced Security Configuration".
     1. Try accessing from your LAPTOP/PC: http://YOUR_SERVER_IP:8080
     2. Try using Chrome/Edge (if installed).
     3. Try http://127.0.0.1:8080 (Trusted Zone).
"@
$manualGuide | Set-Content (Join-Path $BUILD_DIR "MANUAL_START_GUIDE.txt")

# 8d. Pre-generate SSL Certificate for target server
Write-Host "[INFO] Generating Self-Signed Certificate for target IP: 10.55.27.119..."
$TARGET_IP = "10.55.27.119"
# Execute generate_cert.py inside the constructed app directory using the embedded python
Set-Location "$APP_DIR\backend"
Start-Process -FilePath "..\..\runtime\python.exe" -ArgumentList """generate_cert.py""", """$TARGET_IP""" -Wait -NoNewWindow
Set-Location "..\..\.."

# 9. Zip Package
Write-Host "[INFO] Zipping Final Package..."
Compress-Archive -Path "$BUILD_DIR\*" -DestinationPath $ZIP_NAME -Force

Write-Host "=========================================="
Write-Host "Build Complete!"
Write-Host "Package: $ZIP_NAME"
Write-Host "=========================================="
