#!/bin/bash

###############################################################################
# MAHER AI - Offline Package Creator
# Run this on an internet-connected machine
# This script creates a complete offline deployment package
###############################################################################

set -e

echo "======================================================"
echo "MAHER AI - Creating Offline/Sandbox Deployment Package"
echo "======================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_DIR="maher_ai_offline"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="maher_ai_offline_${TIMESTAMP}"

# Clean up old package directory if exists
if [ -d "${PACKAGE_DIR}" ]; then
    echo -e "${YELLOW}Removing old package directory...${NC}"
    rm -rf ${PACKAGE_DIR}
fi

# Create package directory structure
echo -e "${BLUE}Creating package directory structure...${NC}"
mkdir -p ${PACKAGE_DIR}/{frontend,backend,python_packages,config,docs,scripts,tools}

echo -e "${GREEN}✓ Directory structure created${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1/8: Checking prerequisites...${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}ERROR: npm is not installed${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: python3 is not installed${NC}"
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo -e "${RED}ERROR: pip is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Step 2: Install and build frontend
echo -e "${BLUE}Step 2/8: Building frontend...${NC}"

echo "Installing npm dependencies..."
npm install

echo "Building production bundle..."
npm run build

if [ ! -d "dist" ]; then
    echo -e "${RED}ERROR: Build failed - dist/ directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Frontend built successfully${NC}"
echo ""

# Step 3: Copy frontend files
echo -e "${BLUE}Step 3/8: Copying frontend files...${NC}"

cp -r dist ${PACKAGE_DIR}/frontend/
cp package.json ${PACKAGE_DIR}/frontend/
cp package-lock.json ${PACKAGE_DIR}/frontend/ 2>/dev/null || true
cp vite.config.ts ${PACKAGE_DIR}/frontend/
cp tsconfig.json ${PACKAGE_DIR}/frontend/
cp index.html ${PACKAGE_DIR}/frontend/

# Optionally copy node_modules for rebuild capability
read -p "Include node_modules for offline rebuild? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Copying node_modules (this may take a while)..."
    cp -r node_modules ${PACKAGE_DIR}/frontend/
    echo -e "${GREEN}✓ node_modules included${NC}"
else
    echo -e "${YELLOW}Skipping node_modules${NC}"
fi

echo -e "${GREEN}✓ Frontend files copied${NC}"
echo ""

# Step 4: Copy backend files
echo -e "${BLUE}Step 4/8: Copying backend files...${NC}"

cp backend/*.py ${PACKAGE_DIR}/backend/
cp backend/requirements.txt ${PACKAGE_DIR}/backend/

echo -e "${GREEN}✓ Backend files copied${NC}"
echo ""

# Step 5: Download Python packages
echo -e "${BLUE}Step 5/8: Downloading Python packages...${NC}"

echo "Detecting Python version and platform..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')

echo "Python version: ${PYTHON_VERSION}"
echo "Platform: ${PLATFORM}"

echo "Downloading Python packages (this may take a few minutes)..."

# Download for current platform
pip download -r backend/requirements.txt \
    --dest ${PACKAGE_DIR}/python_packages \
    --python-version ${PYTHON_VERSION}

# Create requirements freeze
pip freeze > ${PACKAGE_DIR}/python_packages/requirements-frozen.txt

PACKAGE_COUNT=$(ls -1 ${PACKAGE_DIR}/python_packages/*.whl 2>/dev/null | wc -l || echo "0")
echo -e "${GREEN}✓ Downloaded ${PACKAGE_COUNT} packages${NC}"
echo ""

# Step 6: Copy configuration files
echo -e "${BLUE}Step 6/8: Copying configuration files...${NC}"

cp .env.example ${PACKAGE_DIR}/config/
cp .gitignore ${PACKAGE_DIR}/config/
[ -f nginx.conf.example ] && cp nginx.conf.example ${PACKAGE_DIR}/config/
[ -f maher-ai.service ] && cp maher-ai.service ${PACKAGE_DIR}/config/

echo -e "${GREEN}✓ Configuration files copied${NC}"
echo ""

# Step 7: Copy documentation
echo -e "${BLUE}Step 7/8: Copying documentation...${NC}"

cp README.md ${PACKAGE_DIR}/docs/
[ -f DEPLOYMENT.md ] && cp DEPLOYMENT.md ${PACKAGE_DIR}/docs/
[ -f KNOWLEDGE_UPLOAD_FEATURE.md ] && cp KNOWLEDGE_UPLOAD_FEATURE.md ${PACKAGE_DIR}/docs/
[ -f USER_EXPERIENCE_GUIDE.md ] && cp USER_EXPERIENCE_GUIDE.md ${PACKAGE_DIR}/docs/
[ -f SANDBOX_OFFLINE_DEPLOYMENT_GUIDE.md ] && cp SANDBOX_OFFLINE_DEPLOYMENT_GUIDE.md ${PACKAGE_DIR}/docs/
[ -f SECURITY_CHECKLIST.md ] && cp SECURITY_CHECKLIST.md ${PACKAGE_DIR}/docs/

echo -e "${GREEN}✓ Documentation copied${NC}"
echo ""

# Step 8: Create installation scripts
echo -e "${BLUE}Step 8/8: Creating installation scripts...${NC}"

# Linux/Mac installation script
cat > ${PACKAGE_DIR}/install_offline.sh << 'INSTALL_EOF'
#!/bin/bash

###############################################################################
# MAHER AI - Offline Installation Script
# Run this in the offline/sandbox environment
###############################################################################

set -e

echo "======================================"
echo "MAHER AI - Offline Installation"
echo "======================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Using Python version: ${PYTHON_VERSION}"
echo ""

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --no-index --find-links=python_packages

# Install packages from local wheels
echo "Installing Python packages from offline cache..."
pip install --no-index --find-links=python_packages -r backend/requirements.txt

echo ""
echo "Installed packages:"
pip list

# Setup configuration
echo ""
echo "Setting up configuration..."
if [ ! -f ".env" ]; then
    cp config/.env.example .env
    echo "Created .env file from template"
    echo "⚠️  IMPORTANT: Edit .env file and add your GEMINI_API_KEY"
else
    echo ".env file already exists, not overwriting"
fi

# Create knowledge storage directory
echo "Creating knowledge storage directory..."
mkdir -p backend/knowledge_storage

# Create logs directory
mkdir -p logs

# Set permissions
chmod +x scripts/*.sh 2>/dev/null || true

echo ""
echo "======================================"
echo "✓ Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file:"
echo "   nano .env"
echo ""
echo "2. Add your configuration:"
echo "   GEMINI_API_KEY=your_key_here"
echo "   SECRET_KEY=\$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
echo ""
echo "3. Start the server:"
echo "   ./scripts/start_server.sh"
echo ""
echo "The application will be available at:"
echo "   http://localhost:8080"
echo ""
INSTALL_EOF

chmod +x ${PACKAGE_DIR}/install_offline.sh

# Windows installation script
cat > ${PACKAGE_DIR}/install_offline.bat << 'INSTALL_BAT_EOF'
@echo off
echo ======================================
echo MAHER AI - Offline Installation
echo ======================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip --no-index --find-links=python_packages

REM Install packages from local wheels
echo Installing Python packages from offline cache...
pip install --no-index --find-links=python_packages -r backend\requirements.txt

echo.
echo Installed packages:
pip list

REM Setup configuration
echo.
echo Setting up configuration...
if not exist .env (
    copy config\.env.example .env
    echo Created .env file from template
    echo WARNING: Edit .env file and add your GEMINI_API_KEY
) else (
    echo .env file already exists, not overwriting
)

REM Create knowledge storage directory
echo Creating knowledge storage directory...
if not exist backend\knowledge_storage mkdir backend\knowledge_storage

REM Create logs directory
if not exist logs mkdir logs

echo.
echo ======================================
echo Installation Complete!
echo ======================================
echo.
echo Next steps:
echo 1. Edit .env file and add your configuration
echo 2. Run: scripts\start_server.bat
echo.
echo The application will be available at:
echo    http://localhost:8080
echo.
pause
INSTALL_BAT_EOF

# Start server script (Linux/Mac)
cat > ${PACKAGE_DIR}/scripts/start_server.sh << 'START_EOF'
#!/bin/bash

set -e

echo "Starting MAHER AI Backend Server..."

# Navigate to package root
cd "$(dirname "$0")/.."

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "ERROR: Virtual environment not found. Run ./install_offline.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. Please create it from config/.env.example"
    exit 1
fi

# Start the server
cd backend
echo "Server starting on http://localhost:8080"
python wsgi.py
START_EOF

chmod +x ${PACKAGE_DIR}/scripts/start_server.sh

# Start server script (Windows)
cat > ${PACKAGE_DIR}/scripts/start_server.bat << 'START_BAT_EOF'
@echo off
echo Starting MAHER AI Backend Server...

REM Navigate to package root
cd /d %~dp0\..

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found. Run install_offline.bat first
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found. Please create it from config\.env.example
    pause
    exit /b 1
)

REM Start the server
cd backend
echo Server starting on http://localhost:8080
python wsgi.py
START_BAT_EOF

# Test script
cat > ${PACKAGE_DIR}/scripts/test_offline.sh << 'TEST_EOF'
#!/bin/bash

echo "Testing offline installation..."
echo ""

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    exit 1
fi
echo "✓ Virtual environment exists"

# Activate venv
source venv/bin/activate

# Check installed packages
echo ""
echo "Checking installed packages..."
REQUIRED_PACKAGES="Flask flask-cors flask-limiter python-dotenv requests waitress pdfplumber python-docx"

for package in $REQUIRED_PACKAGES; do
    if pip show $package &> /dev/null; then
        echo "✓ $package installed"
    else
        echo "❌ $package NOT installed"
    fi
done

# Check frontend files
echo ""
echo "Checking frontend files..."
if [ -d "frontend/dist" ]; then
    echo "✓ Frontend build exists"
else
    echo "❌ Frontend build NOT found"
fi

# Check configuration
echo ""
echo "Checking configuration..."
if [ -f ".env" ]; then
    echo "✓ .env file exists"
else
    echo "⚠️  .env file not found (required for running)"
fi

echo ""
echo "Test complete!"
TEST_EOF

chmod +x ${PACKAGE_DIR}/scripts/test_offline.sh

echo -e "${GREEN}✓ Installation scripts created${NC}"
echo ""

# Create README for offline package
cat > ${PACKAGE_DIR}/README_OFFLINE.md << 'README_EOF'
# MAHER AI - Offline Installation Package

This package contains everything needed to run MAHER AI in an offline/air-gapped/sandbox environment.

## 📦 Package Contents

- `frontend/` - Built frontend application
- `backend/` - Python backend source code
- `python_packages/` - All Python dependencies as wheel files
- `config/` - Configuration templates
- `docs/` - Complete documentation
- `scripts/` - Installation and startup scripts

## 🚀 Quick Start

### Linux/macOS:

```bash
# 1. Install
./install_offline.sh

# 2. Configure
nano .env
# Add: GEMINI_API_KEY=your_key_here

# 3. Start
./scripts/start_server.sh
```

### Windows:

```batch
REM 1. Install
install_offline.bat

REM 2. Configure
notepad .env
REM Add: GEMINI_API_KEY=your_key_here

REM 3. Start
scripts\start_server.bat
```

## 📋 Prerequisites

- Python 3.8 or higher
- 500 MB free disk space
- Gemini API key (requires internet access or proxy)

## ⚙️ Configuration

### Required Settings

Edit `.env` file:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Generate with: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_secret_key_here

# Optional
HOST=0.0.0.0
PORT=8080
FLASK_ENV=production
ALLOWED_ORIGINS=*
```

### Generate SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 🧪 Testing

Test the installation:

```bash
./scripts/test_offline.sh
```

## 📚 Documentation

See `docs/` folder:

- **DEPLOYMENT.md** - Complete deployment guide
- **SANDBOX_OFFLINE_DEPLOYMENT_GUIDE.md** - This offline setup
- **KNOWLEDGE_UPLOAD_FEATURE.md** - Knowledge upload documentation
- **USER_EXPERIENCE_GUIDE.md** - User guide
- **SECURITY_CHECKLIST.md** - Security best practices

## 🌐 Accessing the Application

Once started, access at:
- **URL**: http://localhost:8080
- **Default port**: 8080 (configurable in .env)

## 🔧 Troubleshooting

### Installation Issues

**Python packages fail to install:**
```bash
# Check Python version matches packages
python3 --version

# Try installing individual packages
pip install --no-index --find-links=python_packages Flask
```

**Permission denied:**
```bash
chmod +x install_offline.sh
chmod +x scripts/*.sh
```

### Runtime Issues

**Port already in use:**
```bash
# Change PORT in .env
PORT=8081
```

**Cannot connect to Gemini API:**
- Ensure GEMINI_API_KEY is correct in .env
- Check if sandbox allows outbound HTTPS connections
- Configure proxy if needed

### Logs

Check logs:
```bash
# Application logs
tail -f maher_ai.log

# Or check console output when running start_server.sh
```

## 📊 System Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Linux, macOS, Windows |
| Python | 3.8 - 3.11 |
| RAM | 2 GB minimum, 4 GB recommended |
| Disk | 500 MB |
| Network | Internet for Gemini API (or proxy) |

## 🔒 Security Notes

- `.env` file contains sensitive API keys - keep secure
- Run behind reverse proxy (Nginx) in production
- See `docs/SECURITY_CHECKLIST.md` for complete security guide

## 🆘 Support

1. Check `docs/DEPLOYMENT.md` troubleshooting section
2. Review error messages in console/logs
3. Verify .env configuration
4. Test health endpoint: `curl http://localhost:8080/api/health`

## 📝 Version Information

- Package created: {TIMESTAMP}
- MAHER AI version: 1.0.0
- Python version required: 3.8+

## ✅ Post-Installation Checklist

- [ ] Virtual environment created
- [ ] Python packages installed
- [ ] .env file configured
- [ ] GEMINI_API_KEY added
- [ ] SECRET_KEY generated
- [ ] Server starts successfully
- [ ] Application accessible in browser
- [ ] Knowledge upload tested
- [ ] Agent creation tested

---

**Ready to use MAHER AI offline! 🚀**
README_EOF

# Replace timestamp placeholder
sed -i "s/{TIMESTAMP}/${TIMESTAMP}/g" ${PACKAGE_DIR}/README_OFFLINE.md 2>/dev/null || \
sed -i '' "s/{TIMESTAMP}/${TIMESTAMP}/g" ${PACKAGE_DIR}/README_OFFLINE.md 2>/dev/null || true

echo -e "${GREEN}✓ README created${NC}"
echo ""

# Create verification script
cat > ${PACKAGE_DIR}/tools/verify_package.sh << 'VERIFY_EOF'
#!/bin/bash

echo "Verifying offline package integrity..."
echo ""

ERRORS=0

# Check directories
echo "Checking directory structure..."
for dir in frontend backend python_packages config docs scripts; do
    if [ -d "$dir" ]; then
        echo "✓ $dir/"
    else
        echo "❌ $dir/ MISSING"
        ((ERRORS++))
    fi
done

# Check files
echo ""
echo "Checking essential files..."
for file in install_offline.sh README_OFFLINE.md config/.env.example backend/requirements.txt; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "❌ $file MISSING"
        ((ERRORS++))
    fi
done

# Check Python packages
echo ""
echo "Checking Python packages..."
WHL_COUNT=$(ls -1 python_packages/*.whl 2>/dev/null | wc -l || echo "0")
echo "Found ${WHL_COUNT} wheel files"
if [ "$WHL_COUNT" -lt 10 ]; then
    echo "⚠️  Expected more packages"
    ((ERRORS++))
fi

# Check frontend build
echo ""
echo "Checking frontend build..."
if [ -d "frontend/dist" ]; then
    FILE_COUNT=$(find frontend/dist -type f | wc -l)
    echo "✓ Frontend build contains ${FILE_COUNT} files"
else
    echo "❌ Frontend build MISSING"
    ((ERRORS++))
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ Package verification passed!"
    exit 0
else
    echo "❌ Package verification failed with ${ERRORS} errors"
    exit 1
fi
VERIFY_EOF

chmod +x ${PACKAGE_DIR}/tools/verify_package.sh

# Run verification
echo -e "${BLUE}Running package verification...${NC}"
cd ${PACKAGE_DIR}
./tools/verify_package.sh
VERIFY_RESULT=$?
cd ..

if [ $VERIFY_RESULT -ne 0 ]; then
    echo -e "${RED}Package verification failed!${NC}"
    exit 1
fi

echo ""

# Calculate sizes
PACKAGE_SIZE=$(du -sh ${PACKAGE_DIR} | cut -f1)

echo -e "${BLUE}Creating compressed archive...${NC}"
tar -czf ${PACKAGE_NAME}.tar.gz ${PACKAGE_DIR}

if [ $? -eq 0 ]; then
    ARCHIVE_SIZE=$(du -h ${PACKAGE_NAME}.tar.gz | cut -f1)
    echo -e "${GREEN}✓ Archive created successfully${NC}"
else
    echo -e "${RED}ERROR: Failed to create archive${NC}"
    exit 1
fi

echo ""
echo "======================================================"
echo -e "${GREEN}✓ Offline Package Created Successfully!${NC}"
echo "======================================================"
echo ""
echo "Package Information:"
echo "  Name: ${PACKAGE_NAME}.tar.gz"
echo "  Uncompressed size: ${PACKAGE_SIZE}"
echo "  Compressed size: ${ARCHIVE_SIZE}"
echo "  Location: $(pwd)/${PACKAGE_NAME}.tar.gz"
echo ""
echo "Package Contents:"
echo "  • Frontend build (production-ready)"
echo "  • Backend Python source code"
echo "  • Python packages (offline wheels)"
echo "  • Configuration templates"
echo "  • Complete documentation"
echo "  • Installation scripts"
echo ""
echo "Next Steps:"
echo "  1. Transfer ${PACKAGE_NAME}.tar.gz to offline environment"
echo "  2. Extract: tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "  3. Install: cd ${PACKAGE_DIR} && ./install_offline.sh"
echo "  4. Configure: Edit .env file"
echo "  5. Start: ./scripts/start_server.sh"
echo ""
echo "Documentation: ${PACKAGE_DIR}/docs/SANDBOX_OFFLINE_DEPLOYMENT_GUIDE.md"
echo ""
echo "======================================================"
