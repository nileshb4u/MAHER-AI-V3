# MAHER AI v3 - Startup Scripts

## Quick Start (Windows)

```cmd
start.bat
```

This single script:
1. Checks the Python virtual environment (`backend\venv`)
2. Installs frontend `node_modules` if missing
3. Creates `backend\.env` from template if missing (then pauses for you to fill it in)
4. Starts the **backend** Flask/Waitress server in a new window (port 8080)
5. Starts the **frontend** Vite dev server in a new window (port 3000)
6. Opens your browser to `http://localhost:3000`

```cmd
restart.bat   # kill existing processes and re-run start.bat
stop.bat      # gracefully stop both servers
```

---

## Server URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend (Vite dev) | http://localhost:3000 | Main application UI |
| Backend API (Waitress) | http://localhost:8080 | Flask REST API |
| Health check | http://localhost:8080/api/health | API status |

---

## First-Time Setup

```cmd
REM 1. Run setup (creates venv, installs packages, creates .env template)
setup.bat

REM 2. Configure at least one AI provider
notepad backend\.env

REM 3. Start the application
start.bat
```

---

## `backend\.env` — Required Configuration

`setup.bat` and `start.bat` both generate a template automatically if no `.env` exists. Fill in at least one AI provider block:

```ini
# ============================================================
# MAHER AI v3 - Environment Configuration
# ============================================================

# --- AI Provider (fallback chain: gpt-oss → metabrain → gemini) ---
MODEL_PROVIDER=gpt-oss

# GPT-OSS / vLLM (self-hosted, primary)
VLLM_SERVER_URL=
VLLM_MODEL_PATH=/home/cdsw/gpt-oss

# MetaBrain (Aramco enterprise AI, secondary)
METABRAIN_CLIENT_ID=
METABRAIN_CLIENT_SECRET=
METABRAIN_BASE_URL=

# Gemini (Google AI, last resort)
GEMINI_API_KEY=

# --- Server ---
HOST=0.0.0.0
PORT=8080
THREADS=4

# --- Security ---
SECRET_KEY=
ALLOWED_ORIGINS=*
ADMIN_PASSWORD=maher_admin_2026
```

> Change `ADMIN_PASSWORD` before deploying to a shared environment.

---

## Script Details

### `start.bat`

| Step | What happens |
|------|-------------|
| 1 | Checks `backend\venv` exists (exits with error if not) |
| 2 | Runs `npm install` if `node_modules` is missing |
| 3 | Creates `backend\.env` from template and opens Notepad if missing |
| 4 | Opens a new terminal running `python app.py` on port 8080 |
| 5 | Opens a new terminal running `npm run dev` on port 3000 |
| 6 | Opens `http://localhost:3000` in the default browser |

### `restart.bat`

Kills any processes on ports 8080 and 3000 then calls `start.bat`.

### `stop.bat`

Kills processes on ports 8080 and 3000 gracefully.

---

## Troubleshooting

### "Virtual environment not found"

Run `setup.bat` first to create `backend\venv` and install all Python packages.

### "Port already in use"

```cmd
stop.bat
REM or manually:
netstat -ano | find "8080"
taskkill /PID <pid> /F
```

### "Module not found" (Python)

```cmd
cd backend
venv\Scripts\activate
pip install -r requirements.txt
pip install pyyaml   REM required for skills/*.md loader
```

### "Module not found" (Node)

```cmd
npm install
```

### Backend starts but no AI responses

Check `backend\.env` — at least one AI provider must be configured:
- `MODEL_PROVIDER=gpt-oss` and `VLLM_SERVER_URL` pointing to a running vLLM server, **or**
- `MODEL_PROVIDER=metabrain` and MetaBrain credentials, **or**
- `MODEL_PROVIDER=gemini` and a valid `GEMINI_API_KEY`

### Skills not loading

```cmd
cd backend
venv\Scripts\activate
pip install pyyaml
python -c "from skill_retriever import SkillRetriever; r=SkillRetriever('registry.json'); print(len(r._schemas), 'skills loaded')"
```

---

## Development Workflow

### Daily Development

```cmd
start.bat          REM start servers
REM ... make changes — Vite and Flask auto-reload on save ...
stop.bat           REM stop when done
```

### After Pulling Updates

```cmd
cd backend
venv\Scripts\activate
pip install -r requirements.txt
cd ..
npm install
restart.bat
```

### After Editing a Skill File (`backend/skills/*.md`)

The skill registry is reloaded at startup. For a live reload without restarting:

```cmd
curl -X POST http://localhost:8080/api/skills-orchestrator/reload
```

---

## Production Deployment

For production, build the frontend first then run Waitress directly:

```cmd
npm run build
cd backend
venv\Scripts\activate
python run_production.py
```

See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for full instructions.
