# MAHER AI - Startup Scripts

## Quick Start

### Start the Application
```bash
start.bat
```
This will:
1. Check all dependencies
2. Start the backend Flask server (port 5000)
3. Start the frontend Vite dev server (port 5173)
4. Open your browser to http://localhost:5173

### Restart the Application
```bash
restart.bat
```
Stops any running instances and restarts the application.

### Stop the Application
```bash
stop.bat
```
Stops all running MAHER AI servers.

---

## Script Details

### `start.bat`
**Purpose**: Complete application startup with dependency checks

**What it does**:
- ✅ Verifies backend virtual environment exists
- ✅ Checks/installs frontend node modules
- ✅ Verifies .env files exist
- ✅ Starts backend server in new window
- ✅ Starts frontend dev server in new window
- ✅ Opens browser automatically

**Requirements**:
- Backend virtual environment must be set up (run `setup.bat` first)
- Node.js must be installed

### `restart.bat`
**Purpose**: Quick restart without dependency checks

**What it does**:
- Kills existing backend/frontend processes
- Calls `start.bat` to restart

**Use when**:
- Making code changes
- Servers are unresponsive
- Need a fresh start

### `stop.bat`
**Purpose**: Gracefully stop all servers

**What it does**:
- Stops backend Flask server
- Stops frontend Vite dev server
- Shows confirmation messages

**Use when**:
- Done working
- Need to free up ports
- Switching projects

---

## Server URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Main application UI |
| Backend API | http://localhost:5000 | Flask REST API |
| Health Check | http://localhost:5000/api/health | API status |

---

## Admin Credentials

**Password**: `maher_admin_2026`

Change this in production by setting `ADMIN_PASSWORD` in `backend/.env`

---

## Troubleshooting

### "Virtual environment not found"
**Solution**: Run `setup.bat` first to create the virtual environment and install dependencies.

### "Port already in use"
**Solution**: 
1. Run `stop.bat` to kill existing processes
2. Or manually kill processes using ports 5000 and 5173

### "Module not found" errors
**Backend**: 
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend**:
```bash
npm install
```

### Servers won't start
1. Check `backend/.env` has required API keys
2. Verify Python 3.10+ is installed
3. Verify Node.js 18+ is installed
4. Check firewall isn't blocking ports 5000/5173

---

## Development Workflow

### First Time Setup
```bash
# 1. Install dependencies
setup.bat

# 2. Configure environment
# Edit backend/.env with your API keys

# 3. Start application
start.bat
```

### Daily Development
```bash
# Start working
start.bat

# Make code changes...
# Servers auto-reload on file changes

# When done
stop.bat
```

### After Pulling Updates
```bash
# Update dependencies
cd backend
venv\Scripts\activate
pip install -r requirements.txt
cd ..
npm install

# Restart application
restart.bat
```

---

## Production Deployment

For production, use the production scripts instead:

```bash
# Build frontend
npm run build

# Start production server
cd backend
python run_production.py
```

See `DEPLOYMENT.md` for full production setup instructions.
