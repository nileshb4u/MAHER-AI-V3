# MAHER AI v3 - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.10+
- Node.js 18+
- At least one AI provider credential (GPT-OSS, MetaBrain, or Gemini)

---

## Quick Setup

### Windows

```cmd
git clone https://github.com/nileshb4u/MAHER-AI-V3.git
cd MAHER-AI-V3

REM 1. Run setup
setup.bat

REM 2. Configure AI provider (setup.bat creates backend\.env automatically)
notepad backend\.env

REM 3. Start both servers
start.bat

REM 4. Open browser → http://localhost:3000
```

### Linux / Mac

```bash
git clone https://github.com/nileshb4u/MAHER-AI-V3.git
cd MAHER-AI-V3

# 1. Run setup
chmod +x setup.sh && ./setup.sh

# 2. Configure AI provider
nano backend/.env

# 3. Start backend
cd backend && source venv/bin/activate && python run_production.py &

# 4. Start frontend
cd .. && npm run dev

# Open: http://localhost:3000
```

---

## Environment Configuration

Edit `backend/.env` — set **at least one** AI provider:

```bash
# --- AI Provider chain: gpt-oss → metabrain → gemini ---
MODEL_PROVIDER=gpt-oss          # which provider to try first

# Option A: GPT-OSS / vLLM (self-hosted)
VLLM_SERVER_URL=http://localhost:8000
VLLM_MODEL_PATH=/home/cdsw/gpt-oss

# Option B: MetaBrain (Aramco enterprise AI)
METABRAIN_CLIENT_ID=your_client_id
METABRAIN_CLIENT_SECRET=your_secret
METABRAIN_BASE_URL=https://metabrain.aramco.com

# Option C: Gemini (quickest to set up for testing)
GEMINI_API_KEY=your_gemini_key_here

# --- Server (optional) ---
HOST=0.0.0.0
PORT=8080
THREADS=4
ADMIN_PASSWORD=maher_admin_2026
```

> **Tip for quick testing:** Set `MODEL_PROVIDER=gemini` and add your `GEMINI_API_KEY`.

---

## First Steps

### 1. Try a Workflow Query

```
Generate a preventive maintenance checklist for a centrifugal pump
```

Expected: ⚙️ **Workflow** executed (no API cost), structured checklist with safety notes.

### 2. Test a Tool Query

```
Look up equipment PUMP-001
```

Expected: 🔧 **Tool** executed (instant), equipment specs and location.

### 3. Use a Skill

In the **Toolroom**, launch **Procedure Writer** and ask:
```
Write an SOP for replacing a mechanical seal on a centrifugal pump
```

Expected: 🤖 **Skill** invoked, step-by-step SOP with PPE and LOTO steps.

### 4. Multi-Resource Query

```
I need a maintenance checklist AND cost estimate for 4-hour pump maintenance
```

Expected: **Parallel execution** — checklist + cost breakdown in one response.

---

## What You Get Out of the Box

### 3 Workflows (zero AI cost)

- **Maintenance Checklist Generator** — equipment-specific checklists
- **Incident Analyzer** — root cause analysis
- **Equipment Scheduler** — optimized maintenance scheduling

### 4 Tools (instant, zero AI cost)

- **Equipment Lookup** — specifications and manuals
- **Safety Validator** — procedure compliance checks
- **Cost Estimator** — labor, parts, downtime
- **Document Search** — technical documentation

### 6 Built-in Skills (LLM-powered, defined in `backend/skills/*.md`)

- **Schematic Analyst** — P&IDs and electrical diagrams
- **Procedure Writer** — SOP generation with PPE and LOTO
- **Incident Report Analyzer** — 5-Whys / CAPA
- **Contracts Assistant** — clause review and risk flagging
- **Operations Copilot** — alarm troubleshooting
- **Project Planner** — turnaround WBS and Gantt charts

---

## User Interface

| View | Purpose |
|------|---------|
| **Landing** | Start conversations, feature tiles |
| **Chat** | Conversation with history and file attachments |
| **Toolroom** | Browse and launch skills/agents |
| **Agent Studio** | Create custom agents |
| **Knowledge Upload** | Attach documents to agents |

---

## Common Commands

### Development

```bash
# Frontend hot-reload dev server (port 3000)
npm run dev

# Backend dev server (port 8080)
cd backend && python app.py
```

### Production

```bash
npm run build
cd backend && python run_production.py
```

### Database

```bash
# Re-seed system agents from skills/*.md files
cd backend
rm -rf data/
pip install pyyaml   # required for .md loader
python seed_db.py
```

### Reload Skills Without Restart

```bash
curl -X POST http://localhost:8080/api/skills-orchestrator/reload
```

---

## Performance

| Operation | Typical Time | AI Cost |
|-----------|-------------|---------|
| Tool execution | 0.05–0.1 s | None |
| Workflow execution | 0.3–0.5 s | None |
| Skill (LLM) | 3–5 s | Provider API cost |
| Parallel (tool + skill) | ~0.5–1 s | Reduced cost |

**Cost saving:** 60–80% fewer AI API calls compared to pure LLM approaches.

---

## Troubleshooting

### Server Won't Start

```bash
python --version   # must be 3.10+
lsof -i :8080      # check port availability (Linux/Mac)
netstat -an | find "8080"  # Windows
```

### No AI Response / Wrong Provider

```bash
# Check backend/.env
cat backend/.env | grep MODEL_PROVIDER

# Verify GPT-OSS server is up
curl $VLLM_SERVER_URL/health

# Quick fallback — switch to Gemini
# Set MODEL_PROVIDER=gemini and GEMINI_API_KEY in backend/.env
```

### Skills Not Loading

```bash
# Check backend log output on startup for "SkillRetriever: loaded N skills"
# If N is 0, check:
#   1. backend/skills/ directory exists
#   2. PyYAML is installed: pip install pyyaml
#   3. .md files have valid YAML frontmatter with tool_schema
```

---

## Next Steps

1. [Architecture & Full Docs](README.md)
2. [Skills & Agent Management](AGENT_MANAGEMENT_GUIDE.md)
3. [Production Deployment](PRODUCTION_DEPLOYMENT.md)
4. [Security Checklist](SECURITY_CHECKLIST.md)
5. [Sandbox / Offline Deployment](SANDBOX_OFFLINE_DEPLOYMENT_GUIDE.md)

---

**Happy Maintenance! 🛠️**
