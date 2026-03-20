# Build Enterprise Package (FULL VERSION - Includes Torch/OCR)
# Automates the creation of a standalone portable Python package for Windows Server
# WARNING: This package will be very large (1.5GB+) and requires a stable internet connection to build.

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# --- CONFIGURATION ---
$PYTHON_VERSION = "3.10.11"
$PYTHON_URL = "https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-embed-amd64.zip"
$BUILD_DIR = Join-Path (Get-Location) "maher_ai_enterprise_build_full"
$RUNTIME_DIR = Join-Path $BUILD_DIR "runtime"
$SITE_PACKAGES = Join-Path $BUILD_DIR "site-packages"
$APP_DIR = Join-Path $BUILD_DIR "app"
$ZIP_NAME = "MAHER_AI_Enterprise_Package_FULL.zip"

Write-Host "=========================================="
Write-Host "MAHER AI - Enterprise FULL Package Builder"
Write-Host "Target Python: $PYTHON_VERSION (Embeddable)"
Write-Host "Build Dir: $BUILD_DIR"
Write-Host "NOTE: This includes Torch and EasyOCR."
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

# 3. Configure python._pth to enable site-packages
$pthFile = Join-Path $RUNTIME_DIR "python310._pth"
Write-Host "[INFO] Configuring $pthFile..."
$content = Get-Content $pthFile
$newContent = @()
foreach ($line in $content) {
    if ($line -match "#import site") {
        $newContent += "import site" # Uncomment
    } else {
        $newContent += $line
    }
}
# Add site-packages path if not present (usually implies adding ..\site-packages)
if (-not ($newContent -contains "..\site-packages")) {
    $newContent += "..\site-packages"
}
$newContent | Set-Content $pthFile

# 4. Install Dependencies
Write-Host "[INFO] Installing ALL Dependencies (including Torch/OCR)..."
# We simply use the full requirements.txt
$reqFile = "backend\requirements.txt"

# Note: We use --no-cache-dir to minimize disk usage during build if needed, 
# but here standard install is fine.
# Pip install is notoriously slow for torch on some connections.
Write-Host "[INFO] Configuring pip to use stable timeout..."
$env:PIP_DEFAULT_TIMEOUT=1000

Write-Host "[INFO] Starting dependency install (this may take a while)..."
pip install -r $reqFile --target $SITE_PACKAGES --no-compile --only-binary=:all: --platform win_amd64 --python-version 310

# 5. Copy Application Code
Write-Host "[INFO] Copying Backend..."
Copy-Item -Path "backend\*" -Destination "$APP_DIR\backend" -Recurse -Exclude "__pycache__", "venv", ".env"

Write-Host "[INFO] Copying Frontend (dist)..."
if (Test-Path "dist") {
    Copy-Item -Path "dist\*" -Destination "$APP_DIR\dist" -Recurse
} else {
    Write-Warning "[WARN] 'dist' folder not found. Frontend might be missing. Run 'npm run build' first."
}

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

# 7. Copy Config
if (Test-Path ".env") {
    Copy-Item ".env" "$BUILD_DIR\config\.env"
} elseif (Test-Path ".env.example") {
    Copy-Item ".env.example" "$BUILD_DIR\config\.env"
}

# 8. Create README.txt (Instructions for Server Admin)
Write-Host "[INFO] Creating README.txt..."
$readmeContent = @"
MAHER AI - Enterprise Edition (FULL)
====================================

INSTALLATION:
1. Extract this zip file to a folder (e.g., C:\Apps\MAHER_AI).
2. Ensure you have Write permissions to this folder (for logs).

RUNNING:
1. Double-click 'run.bat'.
2. The black console window must stay open.
3. Open Chrome/Edge and go to: http://localhost:8080

TROUBLESHOOTING:
- If run.bat fails, read MANUAL_START_GUIDE.txt.
- Check 'logs' folder for errors.
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

# 9. Zip Package
Write-Host "[INFO] Zipping Final Package (This will take time for 1.5GB+)..."
Compress-Archive -Path "$BUILD_DIR\*" -DestinationPath $ZIP_NAME -Force

Write-Host "=========================================="
Write-Host "Build Complete!"
Write-Host "Package: $ZIP_NAME"
Write-Host "=========================================="
