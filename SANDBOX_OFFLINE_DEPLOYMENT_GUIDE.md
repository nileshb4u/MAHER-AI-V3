# 📦 Sandbox/Offline Deployment Guide - MAHER AI

## Overview

This guide provides step-by-step instructions to prepare MAHER AI for deployment in a **sandbox/air-gapped/offline environment** where internet access is restricted or unavailable.

---

## Table of Contents

1. [Current Dependencies Analysis](#current-dependencies-analysis)
2. [Frontend Offline Preparation](#frontend-offline-preparation)
3. [Backend Offline Preparation](#backend-offline-preparation)
4. [Complete Offline Package Creation](#complete-offline-package-creation)
5. [Offline Installation Instructions](#offline-installation-instructions)
6. [Testing Offline Setup](#testing-offline-setup)
7. [Troubleshooting](#troubleshooting)

---

## 🔍 Current Dependencies Analysis

### External Internet Dependencies

MAHER AI currently relies on these external resources:

#### Frontend (index.html):
```html
<!-- CDN Dependencies -->
1. React 19.2.0 - https://aistudiocdn.com/react@^19.2.0
2. @google/genai SDK - https://aistudiocdn.com/@google/genai@^1.28.0
3. react-markdown - https://aistudiocdn.com/react-markdown@^10.1.0
4. Tailwind CSS - https://cdn.tailwindcss.com
```

#### Backend (Python):
```
1. Flask==3.1.0
2. Flask-Cors==5.0.0
3. Flask-Limiter==3.10.0
4. python-dotenv==1.0.1
5. requests==2.32.3
6. waitress==3.0.2
7. Werkzeug==3.1.3
8. pdfplumber==0.11.0
9. python-docx==1.1.0
```

#### Gemini API:
- External API calls to: https://generativelanguage.googleapis.com/v1beta

---

## 🎨 Frontend Offline Preparation

### Step 1: Download npm Packages Locally

Instead of using CDN imports, we'll bundle everything locally.

#### 1.1 Update package.json

```json
{
  "name": "maher-ai---virtual-maintenance-assistant",
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "@google/generative-ai": "^0.21.0",
    "react-markdown": "^10.1.0"
  },
  "devDependencies": {
    "@types/node": "^22.14.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^5.0.0",
    "typescript": "~5.8.2",
    "vite": "^6.2.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

#### 1.2 Remove CDN Script Tags from index.html

**Current index.html** has:
```html
<script type="importmap">
{
  "imports": {
    "react": "https://aistudiocdn.com/react@^19.2.0",
    "@google/genai": "https://aistudiocdn.com/@google/genai@^1.28.0",
    "react-markdown": "https://aistudiocdn.com/react-markdown@^10.1.0"
  }
}
</script>
```

**Replace with** (remove importmap entirely - Vite will bundle everything)

#### 1.3 Update Component Imports

Change from:
```typescript
import { GoogleGenAI } from '@google/genai';
```

To:
```typescript
import { GoogleGenerativeAI } from '@google/generative-ai';
```

### Step 2: Download Tailwind CSS Locally

#### 2.1 Create tailwind.config.js

```bash
# On internet-connected machine
cd /path/to/MAHER_NEW_UI
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**tailwind.config.js:**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./App.tsx",
  ],
  theme: {
    extend: {
      colors: {
        'brand-blue': '#0A1929',
        'brand-light-blue': '#1E3A5F',
        'brand-accent-orange': '#FF6B35',
        'brand-accent-green': '#4ECDC4',
        'brand-gray': '#8E9AAF',
        'brand-light-gray': '#C5D3E8',
      },
    },
  },
  plugins: [],
}
```

#### 2.2 Create styles.css

Create `styles.css` in project root:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom global styles */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
```

#### 2.3 Update index.html

Remove:
```html
<script src="https://cdn.tailwindcss.com"></script>
```

Add link to compiled CSS (Vite will handle this):
```html
<link rel="stylesheet" href="/styles.css">
```

#### 2.4 Update main entry point

In `index.tsx`, add:
```typescript
import './styles.css';
```

### Step 3: Create Offline Package

#### 3.1 Install All Dependencies (Internet Required)

```bash
# On internet-connected machine
npm install
```

This downloads all packages to `node_modules/`

#### 3.2 Build for Production

```bash
npm run build
```

This creates `dist/` folder with all assets bundled.

#### 3.3 Create Offline npm Cache

```bash
# Create offline package with all dependencies
npm pack
npm cache clean --force

# Create tarball of node_modules
tar -czf node_modules.tar.gz node_modules/

# Alternative: Use npm-pack-all
npx npm-pack-all
```

---

## 🐍 Backend Offline Preparation

### Step 1: Download Python Packages

#### 1.1 Download Wheel Files (Internet Required)

```bash
# On internet-connected machine with same Python version and OS

# Create downloads directory
mkdir python_offline_packages
cd python_offline_packages

# Download all packages with dependencies
pip download -r ../backend/requirements.txt --dest . --platform manylinux2014_x86_64 --python-version 3.11 --only-binary=:all:

# Alternative: Download for multiple platforms
pip download -r ../backend/requirements.txt --dest . --platform manylinux2014_x86_64 --platform win_amd64 --platform macosx_10_9_x86_64

# Download source distributions as backup
pip download -r ../backend/requirements.txt --dest ./source --no-binary :all:
```

**Expected files** (approximately 50-100 files):
```
python_offline_packages/
├── Flask-3.1.0-py3-none-any.whl
├── Flask_Cors-5.0.0-py3-none-any.whl
├── Flask_Limiter-3.10.0-py3-none-any.whl
├── python_dotenv-1.0.1-py3-none-any.whl
├── requests-2.32.3-py3-none-any.whl
├── waitress-3.0.2-py3-none-any.whl
├── Werkzeug-3.1.3-py3-none-any.whl
├── pdfplumber-0.11.0-py3-none-any.whl
├── python_docx-1.1.0-py3-none-any.whl
├── ... (and all dependencies)
```

#### 1.2 Create requirements-offline.txt

```bash
# List all downloaded packages
pip freeze > requirements-offline.txt
```

#### 1.3 Package Python Offline Files

```bash
cd ..
tar -czf python_offline_packages.tar.gz python_offline_packages/
```

### Step 2: Download Python Itself (if needed)

If the sandbox doesn't have Python installed:

```bash
# Download Python standalone distribution
# Linux:
wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz

# Windows:
# Download Python-3.11.7-amd64.exe from python.org

# Create portable Python (Windows)
# Download python-3.11.7-embed-amd64.zip
```

---

## 📦 Complete Offline Package Creation

### Directory Structure for Offline Package

```
maher_ai_offline/
├── README_OFFLINE.md
├── install_offline.sh (Linux/Mac)
├── install_offline.bat (Windows)
├── frontend/
│   ├── dist/ (built frontend)
│   ├── node_modules/ (optional)
│   └── package.json
├── backend/
│   ├── app.py
│   ├── file_parser.py
│   ├── wsgi.py
│   ├── requirements.txt
│   └── __init__.py
├── python_packages/
│   ├── *.whl (all wheel files)
│   └── requirements-offline.txt
├── config/
│   ├── .env.example
│   ├── nginx.conf.example
│   └── maher-ai.service
├── docs/
│   ├── DEPLOYMENT.md
│   ├── KNOWLEDGE_UPLOAD_FEATURE.md
│   └── USER_EXPERIENCE_GUIDE.md
└── scripts/
    ├── setup_venv.sh
    └── start_server.sh
```

### Create Packaging Script

**create_offline_package.sh:**

```bash
#!/bin/bash

###############################################################################
# MAHER AI - Offline Package Creator
# Run this on an internet-connected machine
###############################################################################

set -e

echo "=================================="
echo "MAHER AI - Creating Offline Package"
echo "=================================="

PACKAGE_DIR="maher_ai_offline"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="maher_ai_offline_${TIMESTAMP}"

# Create package directory
echo "Creating package directory..."
mkdir -p ${PACKAGE_DIR}/{frontend,backend,python_packages,config,docs,scripts}

# Step 1: Build Frontend
echo "Building frontend..."
npm install
npm run build

# Copy frontend
echo "Copying frontend files..."
cp -r dist ${PACKAGE_DIR}/frontend/
cp package.json ${PACKAGE_DIR}/frontend/
cp -r node_modules ${PACKAGE_DIR}/frontend/ # Optional: for rebuilds

# Step 2: Copy Backend
echo "Copying backend files..."
cp backend/*.py ${PACKAGE_DIR}/backend/
cp backend/requirements.txt ${PACKAGE_DIR}/backend/

# Step 3: Download Python Packages
echo "Downloading Python packages..."
mkdir -p ${PACKAGE_DIR}/python_packages
pip download -r backend/requirements.txt --dest ${PACKAGE_DIR}/python_packages

# Step 4: Copy Configuration
echo "Copying configuration files..."
cp .env.example ${PACKAGE_DIR}/config/
cp nginx.conf.example ${PACKAGE_DIR}/config/
cp maher-ai.service ${PACKAGE_DIR}/config/

# Step 5: Copy Documentation
echo "Copying documentation..."
cp DEPLOYMENT.md ${PACKAGE_DIR}/docs/
cp KNOWLEDGE_UPLOAD_FEATURE.md ${PACKAGE_DIR}/docs/
cp USER_EXPERIENCE_GUIDE.md ${PACKAGE_DIR}/docs/
cp README.md ${PACKAGE_DIR}/docs/

# Step 6: Create Installation Scripts
echo "Creating installation scripts..."

# Linux/Mac installation script
cat > ${PACKAGE_DIR}/install_offline.sh << 'EOF'
#!/bin/bash
set -e

echo "Installing MAHER AI (Offline Mode)..."

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install packages from local wheels
echo "Installing Python packages from offline cache..."
pip install --no-index --find-links=python_packages -r backend/requirements.txt

# Setup configuration
echo "Setting up configuration..."
cp config/.env.example .env
echo "Please edit .env file and add your GEMINI_API_KEY"

# Create knowledge storage
mkdir -p backend/knowledge_storage

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Add your GEMINI_API_KEY"
echo "3. Run: ./scripts/start_server.sh"
EOF

chmod +x ${PACKAGE_DIR}/install_offline.sh

# Windows installation script
cat > ${PACKAGE_DIR}/install_offline.bat << 'EOF'
@echo off
echo Installing MAHER AI (Offline Mode)...

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install packages from local wheels
echo Installing Python packages from offline cache...
pip install --no-index --find-links=python_packages -r backend\requirements.txt

REM Setup configuration
echo Setting up configuration...
copy config\.env.example .env
echo Please edit .env file and add your GEMINI_API_KEY

REM Create knowledge storage
mkdir backend\knowledge_storage

echo Installation complete!
echo.
echo Next steps:
echo 1. Edit .env file
echo 2. Add your GEMINI_API_KEY
echo 3. Run: scripts\start_server.bat
pause
EOF

# Create start script
cat > ${PACKAGE_DIR}/scripts/start_server.sh << 'EOF'
#!/bin/bash
set -e

# Activate virtual environment
source ../venv/bin/activate

# Start server
cd ../backend
python wsgi.py
EOF

chmod +x ${PACKAGE_DIR}/scripts/start_server.sh

# Create README
cat > ${PACKAGE_DIR}/README_OFFLINE.md << 'EOF'
# MAHER AI - Offline Installation

This package contains everything needed to run MAHER AI in an offline/air-gapped environment.

## Installation

### Linux/Mac:
```bash
./install_offline.sh
```

### Windows:
```
install_offline.bat
```

## Configuration

1. Edit .env file:
```bash
nano .env
```

2. Add your Gemini API key:
```
GEMINI_API_KEY=your_key_here
SECRET_KEY=generate_with_python_secrets
```

## Running

### Linux/Mac:
```bash
./scripts/start_server.sh
```

### Windows:
```
scripts\start_server.bat
```

## Documentation

See docs/ folder for complete documentation:
- DEPLOYMENT.md - Deployment guide
- KNOWLEDGE_UPLOAD_FEATURE.md - Knowledge upload docs
- USER_EXPERIENCE_GUIDE.md - User guide

## Support

For issues, check DEPLOYMENT.md troubleshooting section.
EOF

# Step 7: Create archive
echo "Creating compressed archive..."
tar -czf ${PACKAGE_NAME}.tar.gz ${PACKAGE_DIR}

echo ""
echo "=================================="
echo "Offline package created successfully!"
echo "Package: ${PACKAGE_NAME}.tar.gz"
echo "Size: $(du -h ${PACKAGE_NAME}.tar.gz | cut -f1)"
echo "=================================="
echo ""
echo "Transfer this file to your offline environment and extract it:"
echo "  tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "  cd ${PACKAGE_DIR}"
echo "  ./install_offline.sh"
```

**Make it executable:**
```bash
chmod +x create_offline_package.sh
```

---

## 🚀 Offline Installation Instructions

### On Internet-Connected Machine

```bash
# 1. Run the packaging script
./create_offline_package.sh

# 2. Transfer the resulting .tar.gz file to offline environment
# Use USB drive, secure file transfer, etc.
```

### On Offline/Sandbox Machine

```bash
# 1. Extract the package
tar -xzf maher_ai_offline_YYYYMMDD_HHMMSS.tar.gz
cd maher_ai_offline

# 2. Run installation
./install_offline.sh

# 3. Configure environment
nano .env
# Add your GEMINI_API_KEY and SECRET_KEY

# 4. Start the server
./scripts/start_server.sh
```

**The application will be accessible at:** `http://localhost:8080`

---

## 🧪 Testing Offline Setup

### Pre-Deployment Testing

Before deploying to production offline environment:

#### 1. Test on Internet-Connected Machine (Offline Mode)

```bash
# Disable network temporarily
sudo ifconfig en0 down  # Mac
sudo ip link set eth0 down  # Linux

# Or use airplane mode on laptop

# Try to start the application
./scripts/start_server.sh

# Test in browser: http://localhost:8080
# Verify:
# - Frontend loads
# - Static assets load
# - Chat interface works
# - Knowledge upload works

# Re-enable network
sudo ifconfig en0 up
```

#### 2. Check for Network Calls

Use browser DevTools:
1. Open Chrome DevTools (F12)
2. Go to Network tab
3. Filter: "All"
4. Clear network log
5. Interact with the app
6. Check for any external requests (should be none except Gemini API)

#### 3. Verify Python Packages

```bash
# Activate venv
source venv/bin/activate

# Check installed packages
pip list

# Verify no internet access needed
pip install --no-index --find-links=python_packages Flask

# Should succeed without internet
```

---

## 🔧 Advanced Configuration for Offline Environments

### Gemini API Considerations

**Important:** The Gemini API requires internet access. For completely offline operation:

#### Option 1: Proxy Setup

Set up a proxy server that bridges offline environment to internet:

```bash
# In .env
GEMINI_API_BASE=http://your-proxy-server:8080/v1beta
```

#### Option 2: Local LLM (Future Enhancement)

Replace Gemini with local LLM:
- Ollama
- LLaMA.cpp
- GPT4All

**Example configuration:**
```python
# backend/app.py
# Instead of Gemini API, use local model
from ollama import Client

client = Client(host='http://localhost:11434')
response = client.generate(model='llama2', prompt=prompt)
```

### Static Asset Verification

Ensure all assets are local:

```bash
# Check frontend build for external URLs
grep -r "http://" dist/
grep -r "https://" dist/
grep -r "cdn" dist/

# Should return minimal results (only API calls)
```

---

## 📝 Offline Package Checklist

Before creating offline package:

### Frontend:
- [ ] All npm packages installed locally
- [ ] Tailwind CSS compiled and bundled
- [ ] No CDN imports in index.html
- [ ] Production build created (`npm run build`)
- [ ] Build output verified in `dist/`
- [ ] No external font CDNs
- [ ] No external icon CDNs

### Backend:
- [ ] All Python packages downloaded as wheels
- [ ] requirements.txt complete
- [ ] requirements-offline.txt created
- [ ] Compatible wheel files for target platform
- [ ] Source distributions included as backup

### Configuration:
- [ ] .env.example included
- [ ] Deployment scripts included
- [ ] Documentation copied
- [ ] Installation scripts created
- [ ] README_OFFLINE.md created

### Testing:
- [ ] Tested offline mode on similar environment
- [ ] All features functional without internet
- [ ] Knowledge upload works
- [ ] File parsing works
- [ ] Static files serve correctly

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Cause:** Missing dependency in offline package

**Solution:**
```bash
# On internet machine, add to requirements.txt
pip freeze > requirements-full.txt

# Re-download packages
pip download -r requirements-full.txt --dest python_packages
```

### Issue: Frontend shows blank page

**Cause:** Assets not loading

**Solution:**
```bash
# Check dist/ folder exists
ls -la dist/

# Rebuild frontend
npm run build

# Check Flask static_folder path
# backend/app.py should have: static_folder='../dist'
```

### Issue: Python wheel incompatible

**Cause:** Wrong platform/Python version

**Solution:**
```bash
# Download for specific platform
pip download -r requirements.txt --dest . \
  --platform manylinux2014_x86_64 \
  --python-version 3.11 \
  --only-binary=:all:

# Or download source distributions
pip download -r requirements.txt --dest . --no-binary :all:
```

### Issue: Tailwind styles not applying

**Cause:** Tailwind not compiled

**Solution:**
```bash
# Rebuild with Tailwind
npm install -D tailwindcss
npm run build

# Verify styles.css in dist/
ls dist/assets/*.css
```

### Issue: "Cannot connect to Gemini API"

**Cause:** No internet access in offline environment

**Solution:**
- Set up proxy server for API access
- Or use local LLM (see Advanced Configuration)
- Or ensure API requests whitelisted in firewall

---

## 📊 Package Size Estimates

| Component | Approximate Size |
|-----------|------------------|
| Frontend dist/ | 2-5 MB |
| Frontend node_modules/ | 200-300 MB (optional) |
| Python wheels | 50-100 MB |
| Documentation | 1-2 MB |
| Scripts & Config | < 1 MB |
| **Total Package** | **~250-400 MB** (compressed: ~80-150 MB) |

---

## 🔄 Updating Offline Package

To update the offline package with new features:

```bash
# 1. Update code on internet machine
git pull

# 2. Rebuild frontend
npm install
npm run build

# 3. Download new Python packages (if requirements changed)
pip download -r backend/requirements.txt --dest python_packages

# 4. Re-create offline package
./create_offline_package.sh

# 5. Transfer new package to offline environment

# 6. On offline machine, backup old version
mv maher_ai_offline maher_ai_offline.backup

# 7. Extract and install new version
tar -xzf maher_ai_offline_NEW.tar.gz
cd maher_ai_offline
./install_offline.sh
```

---

## 🎯 Production Deployment Checklist

### Pre-Deployment:
- [ ] Create offline package on internet machine
- [ ] Verify package completeness
- [ ] Test in isolated environment
- [ ] Document any customizations
- [ ] Prepare rollback plan

### Deployment:
- [ ] Transfer package to offline environment
- [ ] Extract package
- [ ] Run installation script
- [ ] Configure .env file
- [ ] Create knowledge_storage directory
- [ ] Set correct file permissions
- [ ] Test application startup
- [ ] Verify all features work

### Post-Deployment:
- [ ] Monitor logs for errors
- [ ] Test knowledge upload
- [ ] Test agent creation
- [ ] Verify API connectivity (if applicable)
- [ ] Document deployment date and version
- [ ] Train users on offline limitations

---

## 📚 Additional Resources

### For Different Platforms

**CentOS/RHEL:**
```bash
# Use yum instead of apt
sudo yum install python3 python3-pip

# Python packages same process
```

**Windows Server:**
```batch
REM Use PowerShell or Command Prompt
python -m venv venv
venv\Scripts\activate.bat
pip install --no-index --find-links=python_packages -r requirements.txt
```

**Docker (Offline):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy offline packages
COPY python_packages /tmp/packages
COPY backend /app/backend
COPY frontend/dist /app/dist

# Install from local packages
RUN pip install --no-index --find-links=/tmp/packages -r backend/requirements.txt

EXPOSE 8080
CMD ["python", "backend/wsgi.py"]
```

Build and save Docker image:
```bash
docker build -t maher-ai-offline .
docker save maher-ai-offline > maher-ai-offline.tar
# Transfer maher-ai-offline.tar to offline environment
docker load < maher-ai-offline.tar
```

---

## ✅ Summary

Your offline package should include:

1. **Frontend**: Compiled static files in `dist/`
2. **Backend**: Python source files
3. **Dependencies**: All Python wheels
4. **Configuration**: .env template, nginx config
5. **Scripts**: Installation and startup scripts
6. **Documentation**: Complete guides

**Total Time to Create Package:** 30-60 minutes
**Installation Time (Offline):** 5-10 minutes
**Result:** Fully functional offline MAHER AI deployment

---

**Questions or Issues?**
- Review error logs in offline environment
- Check file permissions
- Verify Python version matches wheel files
- Consult DEPLOYMENT.md for additional help
