<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />

# MAHER AI - Virtual Maintenance Assistant

**An enterprise-grade AI-powered assistant for maintenance, engineering, and operations teams**

[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Node](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org)
[![React](https://img.shields.io/badge/react-19-blue.svg)](https://react.dev)
[![Flask](https://img.shields.io/badge/flask-3.1-lightgrey.svg)](https://flask.palletsprojects.com)

[Quick Start](#-quick-start) • [Features](#-features) • [Documentation](#-documentation) • [Architecture](#-architecture) • [Deployment](#-deployment)

</div>

---

## 📖 Overview

**MAHER AI** (Maintenance Assistant for High-Efficiency & Reliability) is a sophisticated AI assistant designed for Saudi Aramco's Corporate Maintenance Services Department. It combines the power of AI agents, automated workflows, and specialized tools to deliver intelligent, cost-effective maintenance support.

### 🎯 Key Highlights

- **🤖 Skills-Based Architecture**: AI skills defined as Markdown files — no code changes required
- **🔗 3-Tier AI Fallback**: GPT-OSS (vLLM) → MetaBrain (Aramco) → Gemini — works offline-first
- **💰 60-80% Cost Reduction**: Minimize AI API usage through smart resource allocation
- **⚡ 10-100x Faster**: Tools and workflows execute instantly vs AI calls
- **🔒 Enterprise Security**: Rate limiting, CORS protection, security headers
- **📱 Responsive UI**: Beautiful interface works on all devices
- **🎯 Extensible**: Add skills by dropping a `.md` file into `backend/skills/`

---

## ✨ Features

### Hybrid Orchestrator System

The core intelligence of MAHER AI that:
- **Analyzes** user requests with AI
- **Decomposes** complex tasks into subtasks
- **Matches** subtasks to optimal resources
- **Executes** in parallel or sequential order
- **Integrates** results into unified responses

**Resource Types:**
| Type | Purpose | Speed | Cost |
|------|---------|-------|------|
| **🔧 Tools** | Fast, specialized operations | 0.05-0.1s | Free |
| **⚙️ Workflows** | Automated multi-step tasks | 0.3-0.5s | Free |
| **🤖 AI Agents** | Natural language, analysis | 3-5s | API cost |

### Built-in Resources

**3 Workflows:**
1. **Maintenance Checklist Generator** - Equipment-specific checklists with safety notes
2. **Incident Analyzer** - Root cause analysis and recommendations
3. **Equipment Scheduler** - Optimized maintenance scheduling

**4 Tools:**
1. **Equipment Lookup** - Retrieve specifications and manuals
2. **Safety Validator** - Validate procedures against standards
3. **Cost Estimator** - Labor, parts, and downtime calculations
4. **Document Search** - Technical documentation search

**6 Built-in Skills** (defined as `backend/skills/*.md`):
- Schematic Analyst — P&IDs and electrical diagrams
- Procedure Writer — SOP generation
- Incident Report Analyzer — root cause / CAPA
- Contracts Assistant — clause review
- Operations Copilot — alarm troubleshooting
- Project Planner — turnaround planning

### User Interface

- 💬 **Chat Interface**: Multi-turn conversations with context
- 📎 **File Attachments**: Upload PDFs, Word, Excel (max 2MB)
- ✨ **Prompt Optimization**: AI-powered prompt enhancement
- 📊 **Tool Room**: Browse and select specialized agents
- 🎨 **Agent Management**: Create custom AI agents
- 📚 **Knowledge Upload**: Add documents to agents
- ⭐ **Feedback System**: Rate responses (1-5 stars)

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.10 or higher
- **Node.js** 18 or higher
- At least one AI provider credential (see `.env` section below)

### Option 1: Automated Setup (Recommended)

**Windows:**
```cmd
git clone https://github.com/nileshb4u/MAHER-AI-V3.git
cd MAHER-AI-V3
setup.bat
# Edit backend\.env and configure at least one AI provider
start.bat
```

**Linux/Mac:**
```bash
git clone https://github.com/nileshb4u/MAHER-AI-V3.git
cd MAHER-AI-V3
chmod +x setup.sh && ./setup.sh
# Edit backend/.env and configure at least one AI provider
chmod +x start_server.sh && ./start_server.sh
```

Open: **http://localhost:3000** (frontend) / **http://localhost:8080** (backend API)

### Option 2: Manual Setup

```bash
# 1. Clone repository
git clone https://github.com/nileshb4u/MAHER-AI-V3.git
cd MAHER-AI-V3

# 2. Configure environment
cp backend/.env.example backend/.env   # or create from scratch
# Set at least one AI provider (see Environment Variables below)

# 3. Install frontend
npm install

# 4. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pyyaml          # required for skills/*.md loader
python seed_db.py

# 5. Start servers
# Terminal 1 – backend
python run_production.py

# Terminal 2 – frontend
cd .. && npm run dev
```

Open: **http://localhost:8080**

### 🎯 Try Your First Query

```
Generate a preventive maintenance checklist for a centrifugal pump
```

You should see:
- ⚙️ Workflow executed (not AI)
- Structured checklist
- Safety notes
- Required tools
- Estimated duration

**More Queries to Try:**
- "Look up equipment PUMP-001"
- "Estimate cost for 4-hour pump maintenance"
- "Analyze an incident with pump vibration"

---

## 📚 Documentation

### Quick Links

| Document | Description |
|----------|-------------|
| **[Quick Start Guide](QUICK_START_GUIDE.md)** | Get started in 5 minutes |
| **[Comprehensive Documentation](COMPREHENSIVE_DOCUMENTATION.md)** | Complete project documentation (Part 1) |
| **[Documentation Part 2](COMPREHENSIVE_DOCUMENTATION_PART2.md)** | Security, deployment, testing, optimization |
| **[Hybrid Orchestrator Guide](backend/HYBRID_ORCHESTRATOR_README.md)** | Deep dive into orchestration system |
| **[Frontend Testing Guide](FRONTEND_TESTING_GUIDE.md)** | Test the UI |

### Feature Guides

| Document | Description |
|----------|-------------|
| **[Agent Management Guide](AGENT_MANAGEMENT_GUIDE.md)** | Create and manage AI agents |
| **[Knowledge Upload Feature](KNOWLEDGE_UPLOAD_FEATURE.md)** | Add documents to agents |
| **[User Experience Guide](USER_EXPERIENCE_GUIDE.md)** | Complete UX documentation |

### Deployment & Operations

| Document | Description |
|----------|-------------|
| **[Production Deployment](PRODUCTION_DEPLOYMENT.md)** | Deploy to Linux/Windows servers |
| **[Sandbox Offline Deployment](SANDBOX_OFFLINE_DEPLOYMENT_GUIDE.md)** | Air-gapped deployment |
| **[Security Checklist](SECURITY_CHECKLIST.md)** | Security best practices |
| **[Deployment Guide](DEPLOYMENT.md)** | General deployment guide |

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                   │
│  Landing | Chat | Toolroom | Agent Studio | Knowledge        │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API  (port 8080)
┌───────────────────────────┴─────────────────────────────────┐
│                    Backend (Flask + Python)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │               Skills Orchestrator                       │ │
│  │  SkillRetriever → GPT-OSS function calling → answer    │ │
│  └───┬────────────────┬────────────────┬──────────────────┘ │
│      │                │                │                     │
│  ┌───▼───┐       ┌────▼────┐      ┌───▼─────────────────┐ │
│  │ Tools │       │Workflows│      │  Skills (*.md files) │ │
│  │ (4)   │       │  (3)    │      │  llm_agent / RAG     │ │
│  └───────┘       └─────────┘      └──────────────────────┘ │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────────────────────┐ │
│  │ SQLite Database  │  │  AI Provider chain (fallback)    │ │
│  │ (user agents,    │  │  GPT-OSS → MetaBrain → Gemini    │ │
│  │  chat sessions)  │  │  (set MODEL_PROVIDER in .env)    │ │
│  └──────────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- React 19.2 + TypeScript 5.8
- Vite 6.2 (build tool)
- Tailwind CSS (styling)
- React Markdown (rendering)

**Backend:**
- Flask 3.1 (web framework)
- Python 3.10+
- SQLAlchemy 2.0 (ORM)
- SQLite (database)
- Waitress 3.0 (WSGI server)

**AI Providers (3-tier fallback):**
- GPT-OSS / vLLM (self-hosted, primary)
- MetaBrain (Saudi Aramco enterprise AI, secondary)
- Google Gemini AI (last-resort fallback)

**Document Parsing:**
- PDFPlumber (PDF parsing)
- Python-DOCX (Word parsing)

**Infrastructure:**
- Nginx (reverse proxy)
- systemd (process management)
- Redis (optional, for rate limiting)

---

## 🔒 Security

### Built-in Security Features

- ✅ **API Key Protection**: Server-side storage, never exposed to client
- ✅ **Rate Limiting**: 200 req/day, 50 req/hour per IP (configurable)
- ✅ **CORS Protection**: Whitelist allowed origins
- ✅ **Security Headers**: XSS, Clickjacking, MIME-sniffing protection
- ✅ **Input Validation**: File type, size, and content validation
- ✅ **SQL Injection Prevention**: ORM with parameterized queries
- ✅ **Path Traversal Prevention**: Secure file path handling
- ✅ **HTTPS Ready**: SSL/TLS configuration included

### Configuration

```bash
# backend/.env

# --- AI Provider (at least one required) ---
MODEL_PROVIDER=gpt-oss          # primary: gpt-oss | metabrain | gemini

# GPT-OSS / vLLM (self-hosted)
VLLM_SERVER_URL=http://localhost:8000
VLLM_MODEL_PATH=/home/cdsw/gpt-oss

# MetaBrain (Aramco enterprise AI)
METABRAIN_CLIENT_ID=your_client_id
METABRAIN_CLIENT_SECRET=your_secret
METABRAIN_BASE_URL=https://metabrain.aramco.com

# Gemini (fallback)
GEMINI_API_KEY=your_key_here

# --- Server ---
SECRET_KEY=your_flask_secret_key
ALLOWED_ORIGINS=https://yourdomain.com
ADMIN_PASSWORD=maher_admin_2026
```

See [Security Checklist](SECURITY_CHECKLIST.md) for comprehensive security guidelines.

---

## 📊 Performance

### Benchmarks

| Operation | Time | Cost |
|-----------|------|------|
| **Tool Execution** | 0.05-0.1s | $0 |
| **Workflow Execution** | 0.3-0.5s | $0 |
| **AI Agent** | 3-5s | API cost |
| **Hybrid (Tool+AI)** | 0.5-1s | Reduced API cost |

### Cost Savings

**Before (AI-only):**
- 100% API calls
- $1.00 per 1000 queries

**After (Hybrid):**
- 20-40% API calls
- $0.20-$0.40 per 1000 queries
- **60-80% cost reduction**

### Scalability

- **Horizontal**: Multiple backend instances with load balancer
- **Vertical**: Increase server resources (CPU/RAM)
- **Caching**: Redis for distributed rate limiting
- **Database**: Upgrade to PostgreSQL for production

---

## 🚀 Deployment

### Development

```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate
python app.py

# Terminal 2 - Frontend
npm run dev
```

### Production (Linux)

```bash
# Build
npm run build

# Setup systemd service
sudo cp maher-ai.service /etc/systemd/system/
sudo systemctl enable maher-ai
sudo systemctl start maher-ai

# Setup Nginx
sudo cp nginx.conf.example /etc/nginx/sites-available/maher-ai
sudo ln -s /etc/nginx/sites-available/maher-ai /etc/nginx/sites-enabled/
sudo systemctl reload nginx

# Setup SSL (Let's Encrypt)
sudo certbot --nginx -d yourdomain.com
```

### Production (Docker)

```bash
docker-compose up -d
```

### Export for Sandbox (Offline)

To prepare a clean, offline-ready bundle:

```powershell
./prepare_export.ps1
```

This will create a `MAHER_AI_Offline_Bundle_YYYYMMDD.zip` file containing only the necessary source code and documentation, excluding development artifacts like `node_modules` and `.git`.

See [Sandbox Offline Deployment Guide](SANDBOX_OFFLINE_DEPLOYMENT_GUIDE.md) for detailed instructions on how to deploy this bundle in an air-gapped environment.

---

## 📁 Project Structure

```
MAHER-AI-V3/
├── components/              # React components
│   ├── Chat.tsx            # Chat interface
│   ├── Landing.tsx         # Landing page
│   ├── Toolroom.tsx        # Skill marketplace
│   ├── AgentStudio.tsx     # Custom skill builder
│   └── icons/              # SVG icons
├── backend/                # Flask backend
│   ├── app.py              # Main Flask app
│   ├── models.py           # Database models (users, sessions)
│   ├── skill_retriever.py  # Semantic skill lookup
│   ├── skills_orchestrator.py  # Skills orchestration engine
│   ├── model_client.py     # 3-tier AI provider client
│   ├── registry.json       # Tools & workflows registry
│   ├── skills/             # *** Skill definitions (Markdown) ***
│   │   ├── agent-1-schematic-analyst.md
│   │   ├── agent-2-procedure-writer.md
│   │   ├── agent-3-incident-report-analyzer.md
│   │   ├── agent-4-contracts-assistant.md
│   │   ├── agent-5-operations-copilot.md
│   │   └── agent-6-project-planner.md
│   ├── workflows/          # Workflow modules
│   │   ├── maintenance_checklist.py
│   │   ├── incident_analyzer.py
│   │   └── equipment_scheduler.py
│   ├── tools/              # Tool modules
│   │   ├── equipment_lookup.py
│   │   ├── safety_validator.py
│   │   ├── cost_estimator.py
│   │   └── document_search.py
│   └── data/               # SQLite database (auto-created)
├── public/                 # Static assets
├── dist/                   # Production build (generated)
├── package.json            # Node dependencies
├── vite.config.ts          # Vite configuration
├── setup.bat / setup.sh    # One-click setup scripts
├── start.bat               # Windows one-click start
└── README.md               # This file
```

---

## 🛠️ Available Scripts

### Frontend

```bash
npm run dev        # Start dev server (port 5173)
npm run build      # Build for production
npm run preview    # Preview production build
```

### Backend

```bash
python app.py                 # Development server
python run_production.py      # Production server
python seed_db.py             # Initialize database
python test_hybrid_orchestrator.py  # Test orchestrator
```

---

## 🎨 Customization

### Add Custom Workflow

1. **Create Python module:**
```python
# backend/workflows/my_workflow.py
async def my_function(param1: str) -> Dict[str, Any]:
    return {"success": True, "result": "..."}
```

2. **Register in registry.json:**
```json
{
  "id": "workflow_my_workflow",
  "name": "My Workflow",
  "capabilities": ["my_capability"],
  "module_path": "workflows.my_workflow",
  "function": "my_function",
  "priority": 2
}
```

3. **Add to capability index:**
```json
{
  "capability_index": {
    "my_capability": ["workflow_my_workflow"]
  }
}
```

### Add Custom Tool

Same process as workflow. See [Hybrid Orchestrator Guide](backend/HYBRID_ORCHESTRATOR_README.md).

### Add a New Skill (file-based)

1. Create `backend/skills/my-skill.md`
2. Add YAML frontmatter with `id`, `name`, `description`, `category`, and `tool_schema`
3. Write the system prompt as the Markdown body
4. Restart the backend or call `POST /api/skills-orchestrator/reload`

### Create a Custom Agent (UI-based)

1. Navigate to **Agent Studio**
2. Fill in the wizard (name, category, system prompt)
3. Save as draft or publish
4. Upload knowledge documents (optional)
5. Published agents appear immediately in the Toolroom

---

## 🧪 Testing

### Manual Testing

```bash
# Backend
cd backend
python test_hybrid_orchestrator.py

# Frontend
npm run dev
# Open http://localhost:5173 and test UI
```

### Test Queries

✅ "Generate a preventive maintenance checklist for a pump"
✅ "Look up equipment PUMP-001"
✅ "Estimate cost for 4 hour maintenance"
✅ "I need a checklist AND cost estimate" (multi-resource)
✅ "Analyze an incident with vibration"

### API Testing

```bash
# Health check
curl http://localhost:8080/api/health

# List agents
curl http://localhost:8080/api/agents

# Process request
curl -X POST http://localhost:8080/api/hybrid-orchestrator/process \
  -H "Content-Type: application/json" \
  -d '{"input": "Generate a checklist"}'
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Server won't start**
```bash
# Check Python version
python --version  # Should be 3.10+

# Check port availability
lsof -i :8080  # Linux/Mac
netstat -an | find "8080"  # Windows

# Try different port
PORT=8081 python run_production.py
```

**2. AI provider not responding**
```bash
# Check MODEL_PROVIDER in backend/.env
# Valid values: gpt-oss | metabrain | gemini

# For GPT-OSS, verify the vLLM server is reachable
curl $VLLM_SERVER_URL/health

# Fallback: set MODEL_PROVIDER=gemini and add GEMINI_API_KEY
```

**3. Rate limit exceeded (Gemini fallback)**
- Wait 1 minute and try again
- Switch primary provider to GPT-OSS or MetaBrain

**4. Frontend blank/not loading**
```bash
# Rebuild frontend
npm run build

# Hard refresh browser
# Ctrl+Shift+R (Windows/Linux)
# Cmd+Shift+R (Mac)
```

See [Troubleshooting Section](COMPREHENSIVE_DOCUMENTATION_PART2.md#-troubleshooting) for more solutions.

---

## 📈 Monitoring & Logs

### Application Logs

```bash
# systemd logs
sudo journalctl -u maher-ai -f

# Nginx logs
sudo tail -f /var/log/nginx/maher-ai-access.log
sudo tail -f /var/log/nginx/maher-ai-error.log

# Python logs
tail -f backend/logs/app.log
```

### Health Check

```bash
# Simple health check
curl http://localhost:8080/api/health

# Expected response:
# {"status": "healthy", "service": "MAHER AI Backend", "version": "1.0.0"}
```

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit (`git commit -m 'feat: Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Contribution Areas

- New workflows and tools
- UI/UX improvements
- Bug fixes
- Documentation
- Tests
- Performance optimizations

---

## 📄 License

This project is proprietary to Saudi Aramco / MAHER AI. All rights reserved.

---

## 📞 Support

### Getting Help

1. **Documentation**: Check comprehensive docs
2. **Quick Start**: See [Quick Start Guide](QUICK_START_GUIDE.md)
3. **Issues**: Open GitHub issue with details
4. **Discussions**: GitHub Discussions forum

### Reporting Bugs

Include:
- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment (OS, browser, versions)

### Feature Requests

Use GitHub Issues with:
- Problem description
- Proposed solution
- Use case
- Benefits

---

## 🎉 Acknowledgments

Built with:
- [React](https://react.dev/) - UI framework
- [Flask](https://flask.palletsprojects.com/) - Backend framework
- GPT-OSS / vLLM — primary AI provider (self-hosted)
- MetaBrain — Aramco enterprise AI provider
- [Google Gemini AI](https://ai.google.dev/) — fallback AI provider
- [Vite](https://vitejs.dev/) - Build tool
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM

---

## 🔗 Quick Links

### Documentation

- [📖 Complete Documentation](COMPREHENSIVE_DOCUMENTATION.md)
- [🚀 Quick Start Guide](QUICK_START_GUIDE.md)
- [🎯 Hybrid Orchestrator](backend/HYBRID_ORCHESTRATOR_README.md)
- [🔒 Security Checklist](SECURITY_CHECKLIST.md)
- [🚢 Deployment Guide](PRODUCTION_DEPLOYMENT.md)

### Features

- [🤖 Agent Management](AGENT_MANAGEMENT_GUIDE.md)
- [📚 Knowledge Upload](KNOWLEDGE_UPLOAD_FEATURE.md)
- [🎨 User Experience](USER_EXPERIENCE_GUIDE.md)

### Testing

- [🖥️ Frontend Testing](FRONTEND_TESTING_GUIDE.md)
- [🧪 Backend Testing](backend/test_hybrid_orchestrator.py)

---

<div align="center">

**Built with ❤️ for Saudi Aramco's Corporate Maintenance Services**

[Report Bug](https://github.com/nileshb4u/MAHER_NEW_UI/issues) • [Request Feature](https://github.com/nileshb4u/MAHER_NEW_UI/issues) • [View Docs](COMPREHENSIVE_DOCUMENTATION.md)

**MAHER AI - Intelligent Maintenance, Simplified**

</div>
