
# MAHER AI - Enterprise Deployment Guide (Final)
**Date:** 2026-02-15

This is the **DEFINITIVE** guide for deploying the MAHER AI Enterprise application. 
Please **IGNORE** all previous conflicting instructions or troubleshooting guides.

---

## 🚀 Step 1: Extract and Setup
1.  **Extract the Zip:** Unzip `MAHER_AI_Enterprise_Package.zip` to a folder (e.g., `C:\MAHER_AI`).
2.  **Verify Structure:** You should see folders like `app`, `config`, `frontend_dist`, `runtime` (if included), and several `.bat` files.

---

## 🛠 Step 2: Apply Critical Fixes
Before running the application, you must apply the final fix for MetaBrain connectivity (SSL, Payload, etc.).

1.  **Download the Fix Script:** Ensure you have the `final_metabrain_fix.py` file.
2.  **Run the Fix:**
    - Open a command prompt in the root folder (`C:\MAHER_AI`).
    - Run: `runtime\python.exe final_metabrain_fix.py`
    - **Expected Output:** "SUCCESS: metabrain_client.py has been completely updated..."

This script automatically:
- Disables SSL verification (to bypass corporate proxy errors).
- Fixes the "question body" payload key.
- Adds the missing `to_gemini_format` helper.
- Configures dynamic Auth URLs.

---

## ▶️ Step 3: Run the Application
Choose **ONE** of the following methods:

**Option A: Standard Local Run (Recommended)**
- Double-click **`run_local.bat`**.
- Access the app at: `http://localhost:3000`

**Option B: Network Access (For other PCs to connect)**
- Double-click **`run_network.bat`**.
- Access the app at: `http://[YOUR_IP_ADDRESS]:3000`

**Option C: Custom Port**
- Double-click **`run_custom_port.bat`**.
- Follow the prompt to enter a port (e.g., 8080).

---

## ❓ Troubleshooting

### 1. "503 Service Unavailable"
- **Cause:** Backend server is not running or crashed.
- **Fix:** Check the console window. If it closed, run the `.bat` file again.

### 2. "SSL: CERTIFICATE_VERIFY_FAILED"
- **Cause:** Corporate firewall intercepting HTTPS.
- **Fix:** Re-run `final_metabrain_fix.py`. It hardcodes `verify=False`.

### 3. "NameError: name 'CHAT_URL' is not defined"
- **Cause:** Bad manual edit.
- **Fix:** Re-run `final_metabrain_fix.py`. It restores the missing variable.

### 4. "'ModelResponse' object has no attribute 'to_gemini_format'"
- **Cause:** Missing helper class.
- **Fix:** Re-run `final_metabrain_fix.py`. It adds the `MetaBrainResponse` class.

---

## 🗑 Cleanup
You can safely **DELETE** or **IGNORE** the following files if they exist, as they are now obsolete:
- `repair_metabrain.py`
- `update_app_route.py`
- `update_metabrain_client.py`
- `patch_metabrain_ssl.py`
- `MANUAL_FIX_GUIDE.md`
- `METABRAIN_SCRIPT_ANALYSIS.md`

**`final_metabrain_fix.py` is the only script you need.**
