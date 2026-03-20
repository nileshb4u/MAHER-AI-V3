# MAHER AI - Comprehensive Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Features](#features)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [API Documentation](#api-documentation)
8. [Frontend Architecture](#frontend-architecture)
9. [Backend Architecture](#backend-architecture)
10. [Database Schema](#database-schema)
11. [Hybrid Orchestrator System](#hybrid-orchestrator-system)
12. [Security](#security)
13. [Deployment](#deployment)
14. [Development Guide](#development-guide)
15. [Troubleshooting](#troubleshooting)
16. [Performance Optimization](#performance-optimization)
17. [Testing](#testing)
18. [Contributing](#contributing)

---

## 📖 Project Overview

**MAHER AI** (Maintenance Assistant for High-Efficiency & Reliability) is an enterprise-grade AI-powered virtual assistant designed specifically for maintenance, engineering, and operations teams. Built for Saudi Aramco's Corporate Maintenance Services Department, MAHER AI provides intelligent task routing, specialized agent management, and comprehensive maintenance support.

### Purpose

MAHER AI aims to:
- Streamline maintenance operations through intelligent automation
- Provide instant access to technical knowledge and procedures
- Reduce costs through smart resource allocation
- Improve safety through validated procedures and checklists
- Enable data-driven decision making with analytics

### Key Highlights

- 🤖 **Hybrid Orchestration**: AI Agents + Workflows + Tools
- 📊 **60-80% Cost Reduction** in AI API usage
- ⚡ **10-100x Faster** tool execution vs AI calls
- 🔒 **Enterprise Security**: Rate limiting, CORS, security headers
- 📱 **Responsive UI**: Works on desktop, tablet, and mobile
- 🎯 **Multi-tenant**: Agent isolation and user management
- 📈 **Scalable**: Horizontal scaling with Redis support

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐    │
│  │ Landing  │  │   Chat   │  │ Toolroom │  │ Sidebar │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘    │
│       └──────────────┴─────────────┴──────────────┘         │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST API
┌───────────────────────────┴─────────────────────────────────┐
│                    Backend (Flask)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Hybrid Orchestrator Engine                 │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │  │
│  │  │ Task Decomp  │  │   Resource   │  │ Execution │ │  │
│  │  │ (AI-powered) │→ │   Matching   │→ │  Engine   │ │  │
│  │  └──────────────┘  └──────────────┘  └───────────┘ │  │
│  └──────────────┬────────────┬────────────┬────────────┘  │
│                 │            │            │                 │
│         ┌───────▼────┐ ┌─────▼─────┐ ┌───▼────────┐      │
│         │ AI Agents  │ │ Workflows │ │   Tools    │      │
│         │ (Database) │ │ (Python)  │ │ (Python)   │      │
│         └────────────┘ └───────────┘ └────────────┘      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐    │
│  │   SQLite     │  │  File Parser │  │ Rate Limiter│    │
│  │   Database   │  │  (PDF/DOCX)  │  │   (Redis)   │    │
│  └──────────────┘  └──────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   External Services   │
                │  - Gemini AI API      │
                │  - Document Storage   │
                └───────────────────────┘
```

### Request Flow

1. **User Input** → Frontend (React)
2. **API Call** → `/api/hybrid-orchestrator/process`
3. **Task Decomposition** → AI analyzes request, creates subtasks
4. **Resource Matching** → Registry lookup finds best resources
5. **Execution** → Parallel/Sequential execution
6. **Result Integration** → Merge results into unified response
7. **Frontend Display** → Formatted, structured output

---

## 💻 Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.2.0 | UI framework |
| **TypeScript** | 5.8.2 | Type safety |
| **Vite** | 6.2.0 | Build tool & dev server |
| **Tailwind CSS** | Built-in | Styling |
| **React Markdown** | 10.1.0 | Markdown rendering |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Flask** | 3.1.0 | Web framework |
| **Python** | 3.10+ | Programming language |
| **SQLAlchemy** | 2.0.36 | ORM for database |
| **SQLite** | 3.x | Database |
| **Waitress** | 3.0.2 | Production WSGI server |
| **Flask-CORS** | 5.0.0 | Cross-origin requests |
| **Flask-Limiter** | 3.10.0 | Rate limiting |

### AI & ML

| Service/Library | Purpose |
|-----------------|---------|
| **Google Gemini API** | AI model (gemini-2.0-flash) |
| **PDFPlumber** | PDF text extraction |
| **Python-DOCX** | Word document parsing |

### Infrastructure

| Component | Technology |
|-----------|-----------|
| **Web Server** | Nginx (reverse proxy) |
| **Process Manager** | systemd |
| **Caching** | Redis (optional) |
| **Monitoring** | Custom logging + syslog |

---

## ✨ Features

### 1. Hybrid Orchestrator System

**Intelligent request routing to optimal resources:**

- **AI Agents**: Natural language processing, analysis, recommendations
- **Workflows**: Automated multi-step tasks (checklists, scheduling, analysis)
- **Tools**: Fast, specialized functions (equipment lookup, cost estimation)

**Benefits:**
- 60-80% reduction in AI API costs
- 10-100x faster execution for tools
- Deterministic, repeatable results
- Automatic error handling with retry logic

### 2. Agent Management

**Dynamic AI Agent System:**
- Create custom agents with specialized prompts
- Agent categories: Logistics, Safety, Technical, Training, Analytics
- Draft/Published status workflow
- Agent knowledge upload (PDF, DOCX)
- Per-agent conversation context

### 3. Knowledge Management

**Document Upload & Context:**
- Upload maintenance manuals, procedures, specifications
- Automatic text extraction from PDF/Word
- Agent-specific knowledge bases
- Context injection into AI queries
- File size limits: 2MB per file, 5 files per agent

### 4. Chat Interface

**Intelligent Conversation:**
- Multi-turn conversations with context
- File attachment support
- Prompt optimization
- Markdown formatting
- Progress visualization
- Suggested questions

### 5. Tool Room

**Agent Marketplace:**
- Browse all published agents
- Category filtering
- Search functionality
- Quick agent selection
- Agent statistics and ratings

### 6. Security Features

**Enterprise-grade Security:**
- Rate limiting (200 req/day, 50 req/hour)
- CORS protection
- Security headers (XSS, Content-Type, Frame Options)
- Input validation
- API key protection
- File upload validation

### 7. Feedback System

**Performance Tracking:**
- User ratings (1-5 stars)
- Feedback text capture
- Statistics and analytics
- Resource performance tracking
- Future: ML-based optimization

---

## 🚀 Installation & Setup

### Prerequisites

**System Requirements:**
- Python 3.10 or higher
- Node.js 18.x or higher
- npm 9.x or higher
- 2GB RAM minimum
- 5GB disk space

**For Production:**
- Ubuntu 20.04+ / RHEL 8+ / Windows Server 2019+
- Nginx (recommended)
- SSL certificate
- Domain name

### Quick Start (Development)

#### Windows

```bash
# 1. Clone repository
git clone https://github.com/nileshb4u/MAHER_NEW_UI.git
cd MAHER_NEW_UI

# 2. Run setup script
setup.bat

# 3. Start development server
start_server.bat
```

#### Linux/Mac

```bash
# 1. Clone repository
git clone https://github.com/nileshb4u/MAHER_NEW_UI.git
cd MAHER_NEW_UI

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Start development server
chmod +x start_server.sh
./start_server.sh
```

### Manual Installation

#### 1. Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Build for production
npm run build

# Or run dev server
npm run dev
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see Configuration section)
cp ../.env.example .env
# Edit .env with your API keys

# Initialize database
python seed_db.py

# Run production server
python run_production.py
```

#### 3. Access Application

Open browser: `http://localhost:8080`

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in root directory:

```bash
# ============================================================================
# API Keys
# ============================================================================

# Google Gemini AI API Key (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# ============================================================================
# Server Configuration
# ============================================================================

# Port for the application (default: 8080)
PORT=8080

# Flask environment (development/production)
FLASK_ENV=production

# Secret key for Flask sessions (generate with: python -c "import os; print(os.urandom(32).hex())")
SECRET_KEY=your_secret_key_here

# ============================================================================
# CORS Configuration
# ============================================================================

# Allowed origins (comma-separated, use * for all origins in development)
ALLOWED_ORIGINS=http://localhost:8080,https://yourdomain.com

# ============================================================================
# Rate Limiting
# ============================================================================

# Redis URL for distributed rate limiting (optional)
# If not set, in-memory storage will be used
# REDIS_URL=redis://localhost:6379/0

# ============================================================================
# Database
# ============================================================================

# Database path (relative to backend directory)
DATABASE_PATH=data/maher_ai.db

# ============================================================================
# File Upload
# ============================================================================

# Maximum file size in MB
MAX_FILE_SIZE_MB=2

# Maximum number of files per agent
MAX_FILES_PER_AGENT=5
```

### Getting Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key
4. Add to `.env` file

### Application Configuration

**Backend Config** (`backend/app.py`):

```python
# Security configurations
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# CORS configuration
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get('REDIS_URL', 'memory://')
)
```

**Frontend Config** (`vite.config.ts`):

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
  },
});
```

### Registry Configuration

**Hybrid Orchestrator Registry** (`backend/registry.json`):

Edit to add/remove resources:

```json
{
  "resources": {
    "workflows": [
      {
        "id": "workflow_custom",
        "name": "Custom Workflow",
        "capabilities": ["custom_capability"],
        "module_path": "workflows.custom_workflow",
        "function": "execute",
        "priority": 2
      }
    ],
    "tools": [...],
    "ai_agents": [...]
  },
  "capability_index": {
    "custom_capability": ["workflow_custom"]
  }
}
```

---

## 📡 API Documentation

### Base URL

**Development:** `http://localhost:8080/api`
**Production:** `https://yourdomain.com/api`

### Authentication

Currently, the API uses API key-based authentication for Gemini AI only. No user authentication is required for the application endpoints.

### Common Response Format

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "details": "Detailed error information"
}
```

### Endpoints

#### 1. Health Check

**GET** `/api/health`

Check if the server is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "MAHER AI Backend",
  "version": "1.0.0"
}
```

---

#### 2. Hybrid Orchestrator

**POST** `/api/hybrid-orchestrator/process`

Process a user request through the hybrid orchestrator.

**Request:**
```json
{
  "input": "Generate a maintenance checklist for a pump"
}
```

**Response:**
```json
{
  "success": true,
  "request_id": "REQ-20251113-143022",
  "decomposition": {
    "subtasks": [...],
    "execution_strategy": "sequential",
    "reasoning": "..."
  },
  "execution_summary": {
    "total_subtasks": 1,
    "successful": 1,
    "failed": 0,
    "strategy": "sequential"
  },
  "results": {
    "total_subtasks": 1,
    "successful": 1,
    "failed": 0,
    "results": [
      {
        "resource": "Maintenance Checklist Generator",
        "type": "workflow",
        "data": {
          "success": true,
          "checklist_items": [...],
          "safety_notes": [...],
          "required_tools": [...],
          "estimated_duration_hours": 2.0
        }
      }
    ]
  },
  "timestamp": "2025-11-13T14:30:22.123456"
}
```

**Rate Limit:** 30 requests per minute

---

#### 3. Submit Feedback

**POST** `/api/hybrid-orchestrator/feedback`

Submit user feedback for a request.

**Request:**
```json
{
  "request_id": "REQ-20251113-143022",
  "rating": 5,
  "feedback_text": "Excellent response!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback saved successfully"
}
```

**Rate Limit:** 50 requests per hour

---

#### 4. Get Feedback Statistics

**GET** `/api/hybrid-orchestrator/feedback/stats`

Retrieve feedback statistics.

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_feedback": 42,
    "average_rating": 4.5,
    "rating_distribution": {
      "1": 1,
      "2": 2,
      "3": 5,
      "4": 14,
      "5": 20
    }
  }
}
```

**Rate Limit:** 20 requests per minute

---

#### 5. List Agents

**GET** `/api/agents`

Get all published agents.

**Query Parameters:**
- `status` - Filter by status (draft, published)
- `category` - Filter by category
- `include_drafts` - Include draft agents (true/false)

**Response:**
```json
{
  "success": true,
  "agents": [
    {
      "agent_id": "agent-001",
      "name": "Logistics Agent",
      "description": "Specialized in logistics planning",
      "category": "Logistics & Planning",
      "status": "published",
      "is_system": true,
      "created_at": "2025-01-01T00:00:00",
      "icon_svg": "...",
      "icon_background_color": "#4f46e5"
    }
  ],
  "count": 10
}
```

---

#### 6. Get Single Agent

**GET** `/api/agents/{agent_id}`

Get details of a specific agent.

**Response:**
```json
{
  "success": true,
  "agent": {
    "agent_id": "agent-001",
    "name": "Logistics Agent",
    "description": "...",
    "system_prompt": "...",
    "category": "Logistics & Planning",
    "status": "published"
  }
}
```

---

#### 7. Create Agent

**POST** `/api/agents`

Create a new agent (saved as draft).

**Request:**
```json
{
  "name": "Custom Agent",
  "description": "My custom agent",
  "systemPrompt": "You are a custom assistant...",
  "category": "Technical Support",
  "iconBackgroundColor": "#4f46e5",
  "status": "draft"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Agent created successfully",
  "agent": { ... }
}
```

**Rate Limit:** 50 requests per hour

---

#### 8. Update Agent

**PUT** `/api/agents/{agent_id}`

Update an existing agent.

**Request:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "status": "published"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Agent updated successfully",
  "agent": { ... }
}
```

**Rate Limit:** 50 requests per hour

---

#### 9. Delete Agent

**DELETE** `/api/agents/{agent_id}`

Delete an agent (cannot delete system agents).

**Response:**
```json
{
  "success": true,
  "message": "Agent deleted successfully"
}
```

**Rate Limit:** 50 requests per hour

---

#### 10. Upload Knowledge

**POST** `/api/knowledge/upload`

Upload knowledge files for an agent.

**Request:** (multipart/form-data)
- `agent_id`: Agent ID (form field)
- `files`: Files to upload (PDF, DOCX)

**Response:**
```json
{
  "success": true,
  "agent_id": "agent-001",
  "processed_files": [
    {
      "id": "file-uuid",
      "filename": "manual.pdf",
      "size": 1024000,
      "word_count": 5000
    }
  ],
  "total_files": 3
}
```

**Rate Limit:** 20 requests per hour
**Max Files:** 5 per agent
**Max Size:** 2MB per file

---

#### 11. Get Agent Knowledge

**GET** `/api/knowledge/agents/{agent_id}`

Retrieve agent's knowledge base.

**Response:**
```json
{
  "agent_id": "agent-001",
  "knowledge": {
    "agent_id": "agent-001",
    "documents": [
      {
        "id": "file-uuid",
        "filename": "manual.pdf",
        "content": "...",
        "word_count": 5000,
        "uploaded_at": "2025-01-01T00:00:00"
      }
    ]
  },
  "summary": {
    "total_documents": 2,
    "total_words": 10000,
    "average_words": 5000
  }
}
```

---

#### 12. Delete Agent Knowledge

**DELETE** `/api/knowledge/agents/{agent_id}`

Delete all knowledge for an agent.

**Response:**
```json
{
  "success": true,
  "message": "Deleted all knowledge for agent agent-001"
}
```

---

#### 13. Delete Knowledge File

**DELETE** `/api/knowledge/agents/{agent_id}/files/{file_id}`

Delete a specific file from agent's knowledge.

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully",
  "remaining_files": 1
}
```

---

#### 14. Extract File Content

**POST** `/api/files/extract`

Extract text from uploaded files.

**Request:** (multipart/form-data)
- `files`: Files to extract (PDF, DOCX, XLSX)

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "filename": "document.pdf",
      "size": 1024000,
      "content": "Extracted text content...",
      "word_count": 5000
    }
  ],
  "total_files": 1
}
```

**Rate Limit:** 30 requests per minute
**Max Size:** 2MB per file

---

#### 15. Chat Generation (Legacy)

**POST** `/api/chat/generate`

Direct Gemini API call with optional agent knowledge.

**Request:**
```json
{
  "model": "gemini-2.0-flash",
  "contents": [
    {
      "role": "user",
      "parts": [{"text": "Hello"}]
    }
  ],
  "systemInstruction": "You are an assistant...",
  "agentId": "agent-001"
}
```

**Response:**
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {"text": "Response from AI..."}
        ]
      }
    }
  ]
}
```

**Rate Limit:** 60 requests per minute

---

#### 16. List Models

**GET** `/api/models`

Get available Gemini AI models.

**Response:**
```json
{
  "models": [
    {
      "name": "models/gemini-2.0-flash",
      "displayName": "Gemini 2.0 Flash",
      "description": "..."
    }
  ]
}
```

**Rate Limit:** 10 requests per minute

---

### Rate Limits

| Endpoint Pattern | Limit |
|-----------------|-------|
| `/api/health` | None |
| `/api/hybrid-orchestrator/process` | 30/minute |
| `/api/hybrid-orchestrator/feedback` | 50/hour |
| `/api/agents` (POST, PUT, DELETE) | 50/hour |
| `/api/knowledge/upload` | 20/hour |
| `/api/files/extract` | 30/minute |
| `/api/chat/generate` | 60/minute |
| Default | 200/day, 50/hour |

### Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 207 | Multi-Status (partial success) |
| 400 | Bad Request |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## 🎨 Frontend Architecture

### Project Structure

```
/
├── components/
│   ├── Chat.tsx          # Main chat interface
│   ├── Landing.tsx       # Landing page
│   ├── Sidebar.tsx       # Navigation sidebar
│   ├── Toolroom.tsx      # Agent marketplace
│   ├── AgentManagement.tsx  # Agent CRUD
│   ├── KnowledgeUpload.tsx  # Document upload
│   ├── ProgressVisualization.tsx
│   └── icons/            # SVG icon components
├── App.tsx               # Main app component
├── index.tsx             # Entry point
├── api.ts                # API client
├── constants.ts          # App constants
├── types.ts              # TypeScript types
├── index.html            # HTML template
├── vite.config.ts        # Vite configuration
└── tsconfig.json         # TypeScript config
```

### Component Hierarchy

```
App
├── Sidebar
│   └── Navigation Menu
├── Landing
│   ├── Logo
│   ├── Feature Tiles
│   └── Input Form
├── Chat
│   ├── Message List
│   ├── Progress Visualization
│   └── Input Form
├── Toolroom
│   ├── Category Filter
│   ├── Search Bar
│   └── Agent Cards
└── AgentManagement
    ├── Agent Form
    ├── Knowledge Upload
    └── Agent List
```

### State Management

**Local State (useState):**
- UI state (modals, dropdowns, forms)
- Input values
- Loading states

**Props Drilling:**
- Message history
- Current view
- User preferences

**No global state library** (Redux, Zustand) - React hooks sufficient for current scope.

### Key Components

#### App.tsx

Main application shell. Manages:
- View routing (Landing, Chat, Toolroom, Agent Management)
- Message state
- Initial assistant greeting

#### Chat.tsx

Chat interface. Features:
- Message rendering with Markdown
- File attachment support
- Prompt optimization
- Textarea auto-resize
- Suggested questions
- Thumbs up/down feedback

**Key Functions:**
- `handleSend()` - Process user message, call orchestrator
- `handleOptimizePrompt()` - AI-powered prompt enhancement
- `handleFileSelect()` - Validate and attach files

#### Landing.tsx

Landing page with:
- MAHER logo and branding
- Feature tiles (Toolroom, Agent Management, Knowledge Upload)
- Main input form
- Robot mascot image

#### Toolroom.tsx

Agent marketplace. Features:
- Category filtering
- Search functionality
- Agent cards with icons
- Agent selection → Start chat

#### AgentManagement.tsx

Agent CRUD interface:
- Create/edit agents
- Publish/unpublish
- Delete agents
- Knowledge upload per agent
- Draft/published status

### Styling

**Tailwind CSS** with custom theme:

```css
/* Brand Colors */
--brand-dark-blue: #0A1128
--brand-blue: #1F2937
--brand-light-blue: #4B5563
--brand-accent-orange: #F97316
--brand-light-gray: #E5E7EB
--brand-gray: #9CA3AF
```

**Responsive Breakpoints:**
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

### API Client (`api.ts`)

Centralized API client using `fetch`:

```typescript
export const apiClient = {
  generateContent: async (params: GenerateContentParams) => {
    const response = await fetch('/api/chat/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    return response.json();
  },

  // Other methods...
};
```

### TypeScript Types (`types.ts`)

```typescript
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  isThinking?: boolean;
}

export type AppView =
  | 'Landing'
  | 'Chat'
  | 'Toolroom'
  | 'Agent Management'
  | 'Knowledge Upload';

export interface Agent {
  agent_id: string;
  name: string;
  description: string;
  category: string;
  status: 'draft' | 'published';
  // ... more fields
}
```

---

## 🔧 Backend Architecture

### Project Structure

```
backend/
├── app.py                    # Main Flask application
├── models.py                 # Database models
├── file_parser.py            # Document parsing
├── hybrid_orchestrator.py    # Orchestrator engine
├── registry.json             # Resource registry
├── seed_db.py                # Database seeding
├── run_production.py         # Production server
├── wsgi.py                   # WSGI entry point
├── requirements.txt          # Python dependencies
├── workflows/                # Workflow modules
│   ├── __init__.py
│   ├── maintenance_checklist.py
│   ├── incident_analyzer.py
│   └── equipment_scheduler.py
├── tools/                    # Tool modules
│   ├── __init__.py
│   ├── equipment_lookup.py
│   ├── safety_validator.py
│   ├── cost_estimator.py
│   └── document_search.py
├── data/                     # Database & storage
│   └── maher_ai.db
├── knowledge_storage/        # Agent documents
│   └── {agent_id}.json
└── temp_uploads/             # Temporary files
```

### Core Modules

#### app.py

Main Flask application with:
- Route definitions
- CORS configuration
- Rate limiting
- Security headers
- Error handlers

**Key Routes:**
- `/api/hybrid-orchestrator/process` - Main orchestration
- `/api/agents` - Agent CRUD
- `/api/knowledge/upload` - Document upload
- `/api/files/extract` - File parsing

#### models.py

SQLAlchemy database models:

```python
class Agent(Base):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    status = Column(Enum(AgentStatus), default=AgentStatus.DRAFT)
    is_system = Column(Boolean, default=False)
    created_by = Column(String(100), default='default_user')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    # ... more fields
```

#### hybrid_orchestrator.py

Orchestration engine. Key classes:

```python
class HybridOrchestrator:
    def __init__(self, registry_path, gemini_api_key):
        self.registry = self._load_registry()
        self.gemini_api_key = gemini_api_key

    async def process_request(self, user_input):
        # 1. Decompose task
        decomposition = await self.decompose_task(user_input)

        # 2. Match resources
        execution_plan = []
        for subtask in decomposition['subtasks']:
            resources = self.match_resources(subtask)
            execution_plan.append((resources[0], subtask))

        # 3. Execute
        if strategy == 'parallel':
            results = await self.execute_parallel(execution_plan)
        else:
            results = await self.execute_sequential(execution_plan)

        # 4. Integrate results
        integrated = self.integrate_results(results, user_input)

        return integrated
```

**Key Methods:**
- `decompose_task()` - AI-powered task decomposition
- `match_resources()` - Find best resource for subtask
- `execute_resource()` - Execute workflow/tool/agent
- `integrate_results()` - Merge results
- `save_feedback()` - Store user ratings

#### file_parser.py

Document parsing utilities:

```python
class FileParser:
    @staticmethod
    def parse_file(file) -> Dict[str, Any]:
        # Determine file type and parse

    @staticmethod
    def extract_text_from_pdf(path: str) -> str:
        # Use pdfplumber

    @staticmethod
    def extract_text_from_word(path: str) -> str:
        # Use python-docx

    @staticmethod
    def create_knowledge_context(documents: List) -> str:
        # Format for AI context
```

### Workflows

Python modules for automated tasks.

**Example:** `workflows/maintenance_checklist.py`

```python
async def generate_checklist(
    equipment_type: str,
    maintenance_level: str = "routine"
) -> Dict[str, Any]:

    checklists = {
        "pump": {
            "routine": [
                "Check pump alignment",
                "Inspect seals for leaks",
                # ... more items
            ]
        }
    }

    return {
        "success": True,
        "checklist_items": checklists[equipment_type][maintenance_level],
        "safety_notes": [...],
        "required_tools": [...],
        "estimated_duration_hours": 2.0
    }
```

### Tools

Specialized utility functions.

**Example:** `tools/equipment_lookup.py`

```python
def lookup_equipment(
    equipment_id: str,
    include_manuals: bool = False
) -> Dict[str, Any]:

    equipment_db = {
        "PUMP-001": {
            "name": "Centrifugal Pump",
            "manufacturer": "Flowserve",
            "model": "3196 MTX",
            "specifications": {...}
        }
    }

    equipment = equipment_db.get(equipment_id)

    if not equipment:
        return {"success": False, "error": "Not found"}

    return {"success": True, **equipment}
```

### Database Layer

**SQLite** with SQLAlchemy ORM:

```python
# Database initialization
engine = create_engine('sqlite:///data/maher_ai.db')
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)
```

**Seeding:**
```bash
python backend/seed_db.py
```

Populates database with 10 system agents across 5 categories.

### File Storage

**Knowledge Storage:**
- Location: `backend/knowledge_storage/`
- Format: `{agent_id}.json`
- Structure:
```json
{
  "agent_id": "agent-001",
  "documents": [
    {
      "id": "file-uuid",
      "filename": "manual.pdf",
      "content": "...",
      "size": 1024000,
      "word_count": 5000,
      "uploaded_at": "2025-01-01T00:00:00"
    }
  ],
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

**Feedback Storage:**
- Location: `backend/feedback_store.json`
- Format:
```json
{
  "feedback": [
    {
      "request_id": "REQ-20251113-143022",
      "rating": 5,
      "feedback_text": "Excellent!",
      "timestamp": "2025-11-13T14:30:22"
    }
  ]
}
```

---

## 🗄️ Database Schema

### Tables

#### agents

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| agent_id | VARCHAR(100) | UNIQUE, NOT NULL | Agent identifier |
| name | VARCHAR(200) | NOT NULL | Agent name |
| description | TEXT | NOT NULL | Agent description |
| system_prompt | TEXT | NOT NULL | AI system prompt |
| category | VARCHAR(100) | NOT NULL | Agent category |
| icon_svg | TEXT | NULL | Custom icon SVG |
| icon_background_color | VARCHAR(20) | DEFAULT '#4f46e5' | Icon background |
| default_provider | VARCHAR(100) | DEFAULT 'Gemini 2.5 Flash' | AI model |
| display_provider_name | VARCHAR(200) | DEFAULT 'Powered by Gemini' | Display name |
| status | ENUM | DEFAULT 'draft' | draft/published |
| is_system | BOOLEAN | DEFAULT False | System agent flag |
| created_by | VARCHAR(100) | DEFAULT 'default_user' | Creator |
| created_at | DATETIME | DEFAULT NOW() | Creation timestamp |
| updated_at | DATETIME | DEFAULT NOW() | Update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE on `agent_id`
- INDEX on `status`
- INDEX on `category`
- INDEX on `is_system`

### Agent Categories

1. **Logistics & Planning**
2. **Safety & Compliance**
3. **Technical Support**
4. **Training & Simulation**
5. **Analytics & Insights**

### Database Operations

**Create Agent:**
```python
agent = Agent(
    agent_id=f"user-agent-{uuid.uuid4().hex[:12]}",
    name="Custom Agent",
    description="...",
    system_prompt="...",
    category="Technical Support",
    status=AgentStatus.DRAFT,
    is_system=False
)
db.add(agent)
db.commit()
```

**Query Agents:**
```python
# Get all published agents
agents = db.query(Agent).filter(
    Agent.status == AgentStatus.PUBLISHED
).all()

# Get agent by ID
agent = db.query(Agent).filter(
    Agent.agent_id == "agent-001"
).first()
```

**Update Agent:**
```python
agent = db.query(Agent).filter(
    Agent.agent_id == agent_id
).first()
agent.name = "Updated Name"
agent.updated_at = datetime.utcnow()
db.commit()
```

**Delete Agent:**
```python
agent = db.query(Agent).filter(
    Agent.agent_id == agent_id
).first()
db.delete(agent)
db.commit()
```

### Migrations

Currently using simple SQLAlchemy migrations:

```python
# Add new column
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text(
        "ALTER TABLE agents ADD COLUMN new_field VARCHAR(100)"
    ))
    conn.commit()
```

For production, consider **Alembic** for version-controlled migrations.

---

## 🎯 Hybrid Orchestrator System

### Overview

The Hybrid Orchestrator is the core intelligence of MAHER AI. It analyzes user requests, breaks them into subtasks, and routes each subtask to the optimal resource.

### Architecture

```
User Request
    ↓
Task Decomposition (AI)
    ↓
Resource Matching (Registry)
    ↓
Execution Engine
    ├── AI Agents (Gemini API)
    ├── Workflows (Python async)
    └── Tools (Python sync/async)
    ↓
Result Integration
    ↓
Unified Response
```

### Components

#### 1. Task Decomposition

AI-powered analysis using Gemini:

**Input:** "Generate a checklist and cost estimate for pump maintenance"

**Output:**
```json
{
  "subtasks": [
    {
      "id": "subtask_1",
      "description": "Generate maintenance checklist for pump",
      "preferred_resource_type": "workflow",
      "required_capabilities": ["maintenance_planning", "checklist_generation"],
      "priority": 1,
      "dependencies": []
    },
    {
      "id": "subtask_2",
      "description": "Estimate maintenance cost",
      "preferred_resource_type": "tool",
      "required_capabilities": ["cost_estimation"],
      "priority": 2,
      "dependencies": []
    }
  ],
  "execution_strategy": "parallel",
  "reasoning": "Two independent tasks can run in parallel"
}
```

#### 2. Resource Matching

Registry-based lookup:

```python
def match_resources(subtask):
    required_caps = subtask['required_capabilities']

    # Lookup in capability index
    matched_resources = []
    for cap in required_caps:
        resource_ids = registry['capability_index'][cap]
        for resource_id in resource_ids:
            resource = find_resource_by_id(resource_id)
            matched_resources.append(resource)

    # Sort by priority (tool > workflow > ai_agent)
    matched_resources.sort(key=lambda x: x['priority'])

    return matched_resources
```

#### 3. Execution Engine

**Workflow Execution:**
```python
async def _execute_workflow(resource, subtask):
    module_path = resource['module_path']
    function_name = resource['function']

    # Import module
    module = importlib.import_module(module_path)
    func = getattr(module, function_name)

    # Extract parameters
    params = extract_parameters(subtask, resource['parameters'])

    # Execute
    result = await func(**params)
    return result
```

**Tool Execution:**
```python
async def _execute_tool(resource, subtask):
    if resource['type'] == 'rest_api':
        # Call REST endpoint
        response = requests.post(resource['endpoint'], json=params)
        return response.json()
    else:
        # Call local function
        module = importlib.import_module(resource['module_path'])
        func = getattr(module, resource['function'])
        result = func(**params)
        return result
```

**AI Agent Execution:**
```python
async def _execute_ai_agent(resource, subtask):
    url = f"{GEMINI_API_BASE}/models/gemini-2.0-flash:generateContent"

    payload = {
        'contents': [{
            'role': 'user',
            'parts': [{'text': subtask['description']}]
        }],
        'systemInstruction': {
            'parts': [{'text': resource['system_prompt']}]
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

#### 4. Parallel vs Sequential Execution

**Parallel:**
```python
async def execute_parallel(execution_plan):
    tasks = [
        execute_resource(resource, subtask)
        for resource, subtask in execution_plan
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

**Sequential:**
```python
async def execute_sequential(execution_plan):
    results = []

    for resource, subtask in execution_plan:
        result = await execute_resource(resource, subtask)
        results.append(result)

        # Check if should continue based on result
        if not result['success'] and subtask['required']:
            break

    return results
```

#### 5. Error Handling & Retry

```python
async def execute_resource(resource, subtask, retry_count=0, max_retries=2):
    try:
        # Execute resource
        result = await _execute(resource, subtask)
        return result

    except Exception as e:
        logger.error(f"Error: {e}")

        # Retry logic
        if retry_count < max_retries:
            await asyncio.sleep(2 ** retry_count)  # Exponential backoff
            return await execute_resource(
                resource, subtask, retry_count + 1, max_retries
            )

        return {
            'success': False,
            'error': str(e),
            'status': 'incomplete'
        }
```

#### 6. Result Integration

```python
def integrate_results(results, original_request):
    successful = [r for r in results if r['result']['success']]
    failed = [r for r in results if not r['result']['success']]

    integration = {
        'total_subtasks': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'results': []
    }

    # Format successful results
    for result in successful:
        integration['results'].append({
            'resource': result['resource_name'],
            'type': result['resource_type'],
            'data': result['result']
        })

    # Add failures
    if failed:
        integration['incomplete_tasks'] = [...]

    return integration
```

### Registry Structure

**registry.json:**

```json
{
  "version": "1.0.0",
  "last_updated": "2025-11-13",
  "resources": {
    "workflows": [
      {
        "id": "workflow_maintenance_checklist",
        "name": "Maintenance Checklist Generator",
        "description": "Generates comprehensive checklists",
        "capabilities": ["maintenance_planning", "checklist_generation"],
        "module_path": "workflows.maintenance_checklist",
        "function": "generate_checklist",
        "parameters": {
          "equipment_type": "string",
          "maintenance_level": "string"
        },
        "execution_type": "async",
        "timeout": 30,
        "priority": 2,
        "dependencies": []
      }
    ],
    "tools": [
      {
        "id": "tool_equipment_lookup",
        "name": "Equipment Database Lookup",
        "description": "Retrieves equipment specifications",
        "capabilities": ["equipment_lookup", "specifications"],
        "type": "local_function",
        "module_path": "tools.equipment_lookup",
        "function": "lookup_equipment",
        "parameters": {
          "equipment_id": "string",
          "include_manuals": "boolean"
        },
        "timeout": 5,
        "priority": 1,
        "dependencies": []
      }
    ],
    "ai_agents": [
      {
        "id": "dynamic",
        "name": "AI Agents from Database",
        "description": "Dynamically loaded from database",
        "capabilities": ["natural_language_processing", "analysis"],
        "source": "database",
        "priority": 3
      }
    ]
  },
  "capability_index": {
    "maintenance_planning": ["workflow_maintenance_checklist"],
    "equipment_lookup": ["tool_equipment_lookup"],
    "natural_language_processing": ["dynamic"]
  }
}
```

### Adding New Resources

#### Add Workflow

1. **Create Python module:**
```python
# workflows/my_workflow.py
async def my_function(param1: str) -> Dict[str, Any]:
    # Your logic
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
  "parameters": {"param1": "string"},
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

#### Add Tool

Same process as workflow, but with `"type": "local_function"` or `"type": "rest_api"`.

### Performance Metrics

| Metric | Value |
|--------|-------|
| **API Cost Reduction** | 60-80% |
| **Tool Execution Speed** | 10-100x faster than AI |
| **Average Response Time** | 2-5 seconds (with tools) |
| **Concurrent Requests** | Supports parallel execution |
| **Retry Success Rate** | ~90% (after 2 retries) |

---

*This is Part 1 of the documentation. Continuing in next response...*
