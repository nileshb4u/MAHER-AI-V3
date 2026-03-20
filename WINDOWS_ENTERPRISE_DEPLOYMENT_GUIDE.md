# Windows Enterprise Offline Deployment Guide

**Application:** MAHER AI (Maintenance Assistant)
**Target Environment:** Windows Server (Air-gapped / Offline)
**Security Constraints:** No Admin Rights, No Installation, No Internet

---

## 🏗️ 1. Deployment Overview

This guide details the creation of a **standalone, portable authentication package** for Windows Server. The package contains a pre-configured Python runtime, application code, and all dependencies, requiring **zero installation** on the target server.

### 📦 Package Structure
The final artifact delivered to IT/Security will be a zip file with this structure:

```text
MAHER_AI_Enterprise_Package/
├── runtime/                  # Embeddable Python 3.10 (Signed, Official)
│   ├── python.exe           # Python Interpreter
│   ├── python310.dll        # Core DLL
│   └── ...                  # Minimal standard library
├── site-packages/           # External Dependencies (Frozen, Offline)
│   ├── flask/
│   ├── sqlalchemy/
│   └── ...                  # All pip packages
├── app/                     # Application Source Code
│   ├── backend/             # Python Backend
│   └── frontend/            # React Frontend (Static Build)
├── logs/                    # Application Logs (Write-enabled)
├── config/                  # Configuration Files
│   └── .env                 # Environment Variables
├── run.bat                  # ★ Main Startup Script (Double-click to run)
└── README.txt               # IT Handoff Instructions
```

---

## 🛠️ 2. Build Instructions (On Internet-Connected Machine)

**Role:** Build Engineer
**Machine:** Windows 10/11 (Development)

### Step 2.1: Prepare Build Environment

1.  **Project Root:** Open terminal in `MAHER_NEW_UI`.
2.  **Dependencies:** Ensure `backend/requirements.txt` is free of restricted packages (e.g., specific CUDA versions if GPU is not allowed).

### Step 2.2: Download Embeddable Python

We use the official **Windows Embeddable Package (64-bit)** from Python.org to avoid installation.

1.  Download: [python-3.10.11-embed-amd64.zip](https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip)
2.  Extract to: `MAHER_AI_Enterprise_Package/runtime`

### Step 2.3: Configure Python Runtime

The embeddable Python ignores `site-packages` by default. We must enable it.

1.  Navigate to `runtime/`.
2.  Open `python310._pth` in Notepad.
3.  **Uncomment** (remove `#`) the line: `import site`
4.  **Add** `..\site-packages` to the file list.

**Correct `python310._pth` content:**
```text
python310.zip
.
..
..\site-packages
# Uncomment to run site.main() automatically
import site
```

### Step 2.4: Install Dependencies (Lite or Full)

We provide two build scripts depending on your needs.

**Option A: Lite Version (Recommended for Authentication/Core Logic)**
- **Script:** `build_enterprise_pkg.ps1`
- **Excludes:** `torch`, `easyocr`, `cuda` (Heavy ML libraries)
- **Size:** ~71 MB
- **Use Case:** Standard application logic, no local OCR.

**Option B: Full Version (If Offline OCR is required)**
- **Script:** `build_enterprise_pkg_full.ps1`
- **Includes:** Everything (Torch, EasyOCR, etc.)
- **Size:** ~1.6 GB+
- **Use Case:** Full offline ML capabilities.
- **Warning:** Requires stable internet to build and significantly more disk space.

**To build manually:**
```powershell
# Lite
pip install -r backend/requirements.txt --target=site-packages --no-compile --only-binary=:all: --platform win_amd64 --python-version 310 --no-deps

# Full (remove --no-deps and filtering)
```

> **Security Note:** We use `--only-binary=:all:` to ensure no compilation is required on the server (which would fail).

### Step 2.5: Assemble Application

1.  Copy `backend` folder to `MAHER_AI_Enterprise_Package/app/backend`.
2.  Copy build `dist` folder (Frontend) to `MAHER_AI_Enterprise_Package/app/frontend`.
    *Ensure `backend/app.py` points to this static folder.*
3.  Create `logs` directory.

---

## 🚀 3. Startup Script (`run.bat`)

This script wires everything together without touching the Windows Registry or System PATH.

**File:** `MAHER_AI_Enterprise_Package/run.bat`

```batch
@echo off
setlocal
title MAHER AI - Enterprise Server

:: --- CONFIGURATION ---
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "APP_DIR=%ROOT%app\backend"
set "PYTHON=%RUNTIME%\python.exe"

:: --- ENVIRONMENT ---
:: Force Python to see our portable site-packages
set "PYTHONPATH=%ROOT%site-packages;%APP_DIR%"
:: Prevent Python from writing .pyc files (Security/Read-only safety)
set "PYTHONDONTWRITEBYTECODE=1"
:: Unbuffered output for immediate logging
set "PYTHONUNBUFFERED=1"

:: --- DIAGNOSTICS ---
echo [INFO] Starting MAHER AI in Enterprise Mode...
echo [INFO] Root: %ROOT%
echo [INFO] Python: %PYTHON%
echo [INFO] App Dir: %APP_DIR%

:: --- EXECUTION ---
echo [INFO] Launching Waitress Server...
"%PYTHON%" "%APP_DIR%\wsgi.py"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Application crashed with exit code %ERRORLEVEL%
    pause
)
```

---

## 🛡️ 4. Security & Compliance Checklist

**For IT Security Approval:**

- [x] **No Installation:** Does NOT appear in "Add/Remove Programs".
- [x] **No Registry:** Does NOT read/write HKCU or HKLM.
- [x] **No System PATH:** Does NOT modify global environment variables.
- [x] **No Admin Rights:** Runs entirely in user-space.
- [x] **No Internet:** Application logic contains no hardcoded external calls (except configured API endpoints).
- [x] **Signed Binaries:** Uses official python.org binaries (Digital Signature: Python Software Foundation).

---

## 🧪 5. Validation Instructions

To verify the package before deployment:

1.  **Clean VM Test:** Copy zip to a Windows Sandbox or clean VM (no Python installed).
2.  **Unzip:** Extract to `C:\Apps\MAHER_AI`.
3.  **Run:** Double-click `run.bat`.
4.  **Verify:**
    *   Console shows "Serving on http://0.0.0.0:8080".
    *   Browser opens `http://localhost:8080`.
    *   Logs appear in `logs/` folder.

---

## 📦 6. IT Handoff

**Description:** MAHER AI Portable Logic Container
**Type:** Self-contained Python Application
**Port:** 8080 (Configurable in .env)
**Requirements:** File Read/Write access to own folder only.

**Approval Request:**
"Requesting approval to deploy portable folder `MAHER_AI` to application server. Package contains vendor-supplied Python runtime and application code. No installation or OS changes required."
