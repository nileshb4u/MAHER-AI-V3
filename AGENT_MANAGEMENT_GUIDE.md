# Agent Management System - Complete Guide

This guide explains how to use the new agent management system that allows users to create, save, publish, and manage custom AI agents.

## 🎯 Features

- ✅ **Create Custom Agents** - Build your own AI assistants using the Agent Studio
- ✅ **Save as Draft** - Save work-in-progress agents privately
- ✅ **Publish Agents** - Make agents publicly available in the Toolroom
- ✅ **Database Storage** - All agents stored in SQLite database
- ✅ **System Agents** - 6 pre-built agents ready to use
- ✅ **Knowledge Upload** - Attach PDF/DOCX/TXT files as agent memory
- ✅ **Dynamic Toolroom** - Agents load from database, not hardcoded

---

## 🚀 Quick Start (One-Command Setup)

### For Linux/Mac:
```bash
./setup.sh
```

### For Windows:
```cmd
setup.bat
```

This automated script will:
1. ✅ Create Python virtual environment
2. ✅ Install all backend dependencies (Flask, SQLAlchemy, etc.)
3. ✅ Initialize SQLite database
4. ✅ Seed database with 6 system agents
5. ✅ Create .env template (you'll need to add your API key)
6. ✅ Install frontend dependencies (React, Vite, etc.)
7. ✅ Build production frontend

**That's it!** Everything is set up in one go.

---

## 🔧 Manual Setup (If Needed)

If you prefer to set up manually:

### 1. Backend Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Initialize and seed database
cd backend
python seed_db.py
cd ..
```

### 2. Frontend Setup
```bash
# Install dependencies
npm install

# Build for production
npm run build
```

### 3. Configure Environment
Create `backend/.env` with your Gemini API key:
```bash
GEMINI_API_KEY=your_actual_key_here
HOST=0.0.0.0
PORT=8080
THREADS=4
```

---

## 🎮 Using the System

### Start the Server

**Linux/Mac:**
```bash
./start_server.sh
```

**Windows:**
```cmd
start_server.bat
```

**Manual:**
```bash
source venv/bin/activate
cd backend
python run_production.py
```

Open **http://localhost:8080** in your browser.

---

## 📝 Creating Custom Agents

### Step 1: Navigate to Agent Studio
1. Go to the homepage
2. Click on "Agent Studio" tile

### Step 2: Fill Out Agent Details

**Required Fields:**
- **Agent Name**: Give your assistant a descriptive name
- **Agent Domain**: Choose category (maintenance, operations, safety, etc.)

**Optional But Recommended:**
- **Task Definition**: What specific job will this assistant perform?
- **Required Expertise**: What must the assistant know?
- **Knowledge Base**: Upload PDF/DOCX/TXT files
- **Decision Authority**: What can it do vs when to escalate?
- **Communication Tone**: Formal, supportive, technical?
- **Level of Detail**: Concise or step-by-step?
- **Safety Disclaimers**: Required warnings
- **Escalation Path**: When to get human help?

### Step 3: Test Your Agent
- Use the chat panel on the right to test your agent
- Refine the instructions based on responses

### Step 4: Save or Publish

**Save as Draft:**
```
Click "Save Draft" button
→ Agent saved to database (status: draft)
→ Only visible to you
→ Can be edited later
```

**Save & Deploy (Publish):**
```
Click "Save & Deploy" button
→ Agent saved to database (status: published)
→ Immediately visible in Toolroom
→ Available to all users
```

---

## 🗄️ Database Structure

### Location
```
backend/data/maher_ai.db
```

### Agent Table Schema
```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    agent_id VARCHAR(100) UNIQUE,          -- e.g., 'agent-1', 'user-agent-abc123'
    name VARCHAR(200),
    description TEXT,
    system_prompt TEXT,
    category VARCHAR(50),
    icon_svg TEXT,
    icon_background_color VARCHAR(20),
    default_provider VARCHAR(100),
    display_provider_name VARCHAR(100),
    status VARCHAR(20),                    -- 'draft' or 'published'
    is_system BOOLEAN,                     -- True for built-in agents
    created_by VARCHAR(100),               -- User tracking
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### System Agents (Pre-loaded)
1. **Schematic Analyst** - Interprets technical drawings
2. **Procedure Writer** - Creates SOPs
3. **Incident Report Analyzer** - Analyzes safety incidents
4. **Contracts Assistant** - Reviews contracts
5. **Operations Copilot** - Supports plant operators
6. **Project Planner** - Creates project plans

---

## 🔌 API Endpoints

### Get All Published Agents
```http
GET /api/agents
Response: { success: true, agents: [...], count: 6 }
```

### Get Agents Including Drafts
```http
GET /api/agents?include_drafts=true
Response: { success: true, agents: [...], count: 10 }
```

### Get Single Agent
```http
GET /api/agents/agent-1
Response: { success: true, agent: {...} }
```

### Create Agent (Save Draft)
```http
POST /api/agents
Body: {
  name: "My Custom Agent",
  description: "...",
  systemPrompt: "...",
  category: "maintenance",
  status: "draft"  # or "published"
}
Response: { success: true, message: "...", agent: {...} }
```

### Update Agent
```http
PUT /api/agents/user-agent-abc123
Body: { name: "Updated Name", ... }
Response: { success: true, message: "...", agent: {...} }
```

### Publish Agent
```http
PUT /api/agents/user-agent-abc123/publish
Response: { success: true, message: "...", agent: {...} }
```

### Delete Agent
```http
DELETE /api/agents/user-agent-abc123
Response: { success: true, message: "..." }
```

---

## 📊 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      AGENT LIFECYCLE                         │
└─────────────────────────────────────────────────────────────┘

   User Opens Agent Studio
             │
             ▼
   Fills out wizard steps
   (Name, Category, Task, Knowledge, etc.)
             │
             ▼
   Tests agent in chat panel
             │
             ├──────────────────┬──────────────────┐
             ▼                  ▼                  ▼
      Save Draft        Save & Deploy         Discard
             │                  │
             ▼                  ▼
   Saved to Database    Saved + Published
   (status: draft)      (status: published)
             │                  │
             │                  ▼
             │         Appears in Toolroom
             │         (visible to all users)
             │                  │
             │                  ▼
             │         Users can launch agent
             │         and chat with it
             │
             ▼
   Can edit and publish later
```

---

## 🗂️ File Structure

```
MAHER_NEW_UI/
├── setup.sh                    # Linux/Mac automated setup
├── setup.bat                   # Windows automated setup
├── start_server.sh             # Linux/Mac server startup
├── start_server.bat            # Windows server startup
│
├── backend/
│   ├── app.py                  # Main Flask app with agent endpoints
│   ├── models.py               # SQLAlchemy Agent model
│   ├── seed_db.py              # Database initialization script
│   ├── run_production.py       # Waitress production server
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment config (create this!)
│   │
│   └── data/
│       └── maher_ai.db         # SQLite database (auto-created)
│
├── components/
│   ├── AgentStudio.tsx         # Agent creation UI (updated)
│   └── Toolroom.tsx            # Agent listing UI (updated)
│
├── api.ts                      # Frontend API client (updated)
│
└── dist/                       # Built frontend (auto-generated)
```

---

## 🛠️ Development Tips

### View Database Contents
```bash
# Using sqlite3 CLI
sqlite3 backend/data/maher_ai.db "SELECT agent_id, name, status FROM agents;"

# Or use a GUI like DB Browser for SQLite
```

### Reset Database
```bash
# Delete database
rm backend/data/maher_ai.db

# Re-initialize
cd backend
python seed_db.py
cd ..
```

### Add More System Agents
Edit `backend/seed_db.py` and add your agent data to `SYSTEM_AGENTS` list.

### Modify Agent Schema
1. Edit `backend/models.py`
2. Delete `backend/data/maher_ai.db`
3. Run `python backend/seed_db.py`

---

## ✅ Testing the System

### Test 1: Create Draft Agent
1. Go to Agent Studio
2. Enter agent name and category
3. Click "Save Draft"
4. ✓ Success message appears
5. ✓ Agent ID is stored

### Test 2: Publish Agent
1. After saving draft, click "Save & Deploy"
2. ✓ Success message: "Agent published! Check Toolroom"
3. Go to Toolroom
4. ✓ Your agent appears in the grid

### Test 3: Agent Knowledge
1. In Agent Studio, go to "Knowledge Base" step
2. Upload a PDF/DOCX/TXT file
3. Save and publish agent
4. Launch agent from Toolroom
5. Ask questions about the uploaded document
6. ✓ Agent responds with knowledge from document

### Test 4: Update Agent
1. Create and save an agent
2. Modify the name or description
3. Click "Update Draft" or "Save & Deploy"
4. ✓ Changes are saved
5. ✓ Toolroom reflects updates

---

## 🐛 Troubleshooting

### Problem: Database not found
**Solution:**
```bash
cd backend
python seed_db.py
```

### Problem: No agents in Toolroom
**Cause:** Database not seeded or API error

**Solution:**
1. Check browser console for errors
2. Check backend logs
3. Verify database exists: `ls backend/data/`
4. Re-seed: `python backend/seed_db.py`

### Problem: "Failed to save agent"
**Cause:** Backend API error

**Solution:**
1. Check backend logs
2. Verify SQLAlchemy is installed: `pip list | grep SQLAlchemy`
3. Check .env file has valid config
4. Restart server

### Problem: Frontend not updated after changes
**Solution:**
```bash
npm run build
# Restart server
```

---

## 📚 Next Steps

### Recommended Enhancements
1. **User Authentication** - Multi-user support with login
2. **Agent Versioning** - Track changes over time
3. **Agent Analytics** - Usage stats and ratings
4. **Agent Sharing** - Export/import agents
5. **Advanced Knowledge** - Vector search, RAG integration
6. **Agent Categories** - Custom categories
7. **Agent Templates** - Pre-filled templates for common use cases

---

## 🔒 Security Notes

- **API Keys**: Never commit `.env` file to git (already in `.gitignore`)
- **Database**: Backup `backend/data/maher_ai.db` regularly
- **Rate Limiting**: Already configured (50 agent ops/hour per IP)
- **CORS**: Configure `ALLOWED_ORIGINS` in `.env` for production
- **System Agents**: Cannot be modified or deleted via API

---

## 📞 Support

For issues or questions:
1. Check this guide
2. Review `PRODUCTION_DEPLOYMENT.md`
3. Check backend logs: `backend/maher_ai.log`
4. Check browser console (F12)

---

**Version:** 1.0.0
**Last Updated:** 2025-11-12
