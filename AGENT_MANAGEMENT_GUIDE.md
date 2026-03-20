# Skills & Agent Management Guide

This guide explains how skills and custom agents work in MAHER AI v3.

## Overview

MAHER AI v3 uses two complementary mechanisms for AI-driven capabilities:

| Mechanism | Where defined | Who manages | Loaded by |
|-----------|--------------|-------------|-----------|
| **File-based Skills** | `backend/skills/*.md` | Developers / admins | `skill_retriever.py` at startup |
| **User-created Agents** | SQLite database | Users via Agent Studio | `app.py` `/api/agents` endpoint |

Both types are callable by the Skills Orchestrator via OpenAI function-calling.

---

## File-Based Skills (`backend/skills/*.md`)

### What is a Skill File?

Each `.md` file in `backend/skills/` defines one AI skill. The file has two parts:

1. **YAML frontmatter** (between `---` delimiters) — metadata and the `tool_schema`
2. **Markdown body** — the system prompt sent to the model when the skill is invoked

### Skill File Format

```markdown
---
id: my-skill-id
name: My Skill Name
description: One-line description shown in the Toolroom.
category: maintenance      # maintenance | safety | operations | contracts | projects | other
icon_color: "#4f46e5"      # hex color for the Toolroom card
status: available          # available | draft  (draft = not loaded)
implementation_type: llm_agent
version: "1.0.0"
tool_schema:
  type: function
  function:
    name: my_skill_function   # snake_case, max 40 chars
    description: When to call this skill — used by the model to decide routing.
    parameters:
      type: object
      properties:
        param_one:
          type: string
          description: Description of the first parameter
        param_two:
          type: string
          description: Optional second parameter
          enum: ["option_a", "option_b"]
      required:
        - param_one
---

You are a specialized assistant for [domain]. Your task is to [description of
what the skill does]. Always [important behavioral instructions].
```

### Built-in Skills

Six skills ship with MAHER AI v3 in `backend/skills/`:

| File | Skill | Category |
|------|-------|----------|
| `agent-1-schematic-analyst.md` | Schematic Analyst | maintenance |
| `agent-2-procedure-writer.md` | Procedure Writer | maintenance |
| `agent-3-incident-report-analyzer.md` | Incident Report Analyzer | safety |
| `agent-4-contracts-assistant.md` | Contracts Assistant | contracts |
| `agent-5-operations-copilot.md` | Operations Copilot | operations |
| `agent-6-project-planner.md` | Project Planner | projects |

### Adding a New Skill

1. Create a new `.md` file in `backend/skills/`:
   ```bash
   touch backend/skills/my-new-skill.md
   ```

2. Add frontmatter and system prompt following the format above.

3. Reload without restarting:
   ```http
   POST /api/skills-orchestrator/reload
   Authorization: (admin session)
   ```
   Or restart the backend server.

4. Verify it loaded:
   ```bash
   curl http://localhost:8080/api/agents | python -m json.tool
   ```

### Editing an Existing Skill

Edit the `.md` file directly — no database migration or code change required. After editing, reload the skill registry (see above).

### Disabling a Skill (without deleting)

Set `status: draft` in the frontmatter. The skill will be skipped by `skill_retriever.py`.

### Database Seeding from Skill Files

`seed_db.py` reads `backend/skills/*.md` at startup to populate the SQLite `agents` table with system agents. This happens automatically the first time you run:

```bash
cd backend
python seed_db.py
```

**Requirement:** PyYAML must be installed:
```bash
pip install pyyaml
```

If PyYAML is not available, `seed_db.py` falls back to a minimal hardcoded list.

---

## User-Created Agents (Agent Studio)

Users can create custom agents through the **Agent Studio** UI. These are stored in the SQLite database and work identically to skill files at runtime.

### Creating a Custom Agent

1. Go to the home page and click **Agent Studio**
2. Fill out the wizard:
   - **Agent Name** (required)
   - **Domain / Category** (required)
   - **Task Definition** — what the agent does
   - **System Prompt** — behavioral instructions
   - **Knowledge Base** — upload PDF/DOCX/TXT files (optional)
3. Click **Save Draft** (private) or **Save & Deploy** (visible in Toolroom)

### Agent Lifecycle

```
Agent Studio wizard
        │
        ▼
  Save Draft ──────────────────► status: draft  (only you can see it)
        │
        ▼
  Save & Deploy ───────────────► status: published → appears in Toolroom
```

### Agent Studio API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/agents` | List published agents |
| `GET` | `/api/agents?include_drafts=true` | List all (admin) |
| `GET` | `/api/agents/<id>` | Get single agent |
| `POST` | `/api/agents` | Create agent |
| `PUT` | `/api/agents/<id>` | Update agent |
| `PUT` | `/api/agents/<id>/publish` | Publish draft |
| `DELETE` | `/api/agents/<id>` | Delete agent |

### Example: Create Agent via API

```http
POST /api/agents
Content-Type: application/json

{
  "name": "Valve Inspector",
  "description": "Reviews valve inspection records and flags anomalies.",
  "systemPrompt": "You are a valve inspection specialist...",
  "category": "maintenance",
  "status": "published"
}
```

---

## Database

### Location

```
backend/data/maher_ai.db
```

### Agents Table (key columns)

| Column | Description |
|--------|-------------|
| `agent_id` | Unique ID (e.g., `agent-1`, `user-agent-abc123`) |
| `name` | Display name |
| `description` | Short description |
| `system_prompt` | LLM instructions (body of skill `.md`) |
| `category` | Domain category |
| `status` | `draft` or `published` |
| `is_system` | `true` for agents seeded from `skills/*.md` |
| `tool_schema` | JSON function-calling schema |
| `implementation_type` | `llm_agent` \| `rag_pipeline` \| `workflow` |
| `skill_version` | Semantic version (e.g., `1.0.0`) |

### Reset Database

```bash
cd backend
rm -rf data/
python seed_db.py
```

---

## File Structure

```
MAHER-AI-V3/
├── backend/
│   ├── skills/                   # *** Skill definition files ***
│   │   ├── agent-1-schematic-analyst.md
│   │   ├── agent-2-procedure-writer.md
│   │   ├── agent-3-incident-report-analyzer.md
│   │   ├── agent-4-contracts-assistant.md
│   │   ├── agent-5-operations-copilot.md
│   │   └── agent-6-project-planner.md
│   ├── skill_retriever.py        # Loads skills from files + registry.json
│   ├── skills_orchestrator.py    # Orchestrates skill execution
│   ├── skill_schema_generator.py # Auto-generates tool_schema from wizard data
│   ├── seed_db.py                # Seeds DB from skills/*.md
│   ├── models.py                 # SQLAlchemy Agent model
│   └── data/
│       └── maher_ai.db           # SQLite database
└── components/
    ├── AgentStudio.tsx           # Custom agent creation UI
    └── Toolroom.tsx              # Skill/agent listing UI
```

---

## Troubleshooting

### Skill not appearing in Toolroom

1. Check `status` in frontmatter is `available` (not `draft`)
2. Check `tool_schema` is present and correctly indented YAML
3. Check backend logs for parse errors
4. Call `POST /api/skills-orchestrator/reload`

### `seed_db.py` says "Falling back to hardcoded agents"

Install PyYAML:
```bash
cd backend && pip install pyyaml
```

### Database agent data is stale after editing a `.md` file

The database is only seeded once (first run). To re-seed after editing skill files:
```bash
cd backend
rm -rf data/
python seed_db.py
```

Or update the agent via the API (`PUT /api/agents/<id>`).

### "Skill not found in registry" error

The skill is in the database but not in the `SkillRetriever` index. Reload:
```http
POST /api/skills-orchestrator/reload
```

---

## Security Notes

- System agents (from `skills/*.md`) cannot be deleted via the user-facing API
- `ADMIN_PASSWORD` in `backend/.env` protects admin endpoints
- Skill files should be reviewed before deployment — they control LLM behavior
- Never commit provider credentials to source control

---

**Version:** 3.0.0
**Last Updated:** 2026-03-20
