# MAHER AI - Codebase Analysis, Eval Recommendations & Readiness Assessment

## 1. Executive Summary

MAHER AI is an enterprise-grade virtual maintenance assistant built on a React 19 + Flask architecture with Gemini AI integration. It features a Plan-Execute-Verify (PEV) orchestration engine, 40+ specialized tools, 3 automated workflows, and a hybrid task router. This report covers:

- Full functional analysis
- Sandbox environment compatibility assessment
- Multi-user readiness gaps
- Local model (gptoss) integration readiness
- Comprehensive eval recommendations

---

## 2. Architecture & Functionality Analysis

### 2.1 Frontend (React 19 + TypeScript + Vite)

| Component | File | Purpose |
|-----------|------|---------|
| App Shell | `App.tsx` | View routing, sidebar, message history |
| Chat | `components/Chat.tsx` | Main conversational interface with file upload |
| Agent Studio | `components/AgentStudio.tsx` | Create/manage custom AI agents |
| Agent Builder | `components/AgentBuilderWizard.tsx` | Guided agent creation flow |
| Toolroom | `components/Toolroom.tsx` | Browse/execute 40+ specialized tools |
| Knowledge Upload | `components/KnowledgeUpload.tsx` | Attach documents to agents |
| Analytics | `components/Analytics.tsx` | Performance metrics dashboard |
| Progress Viz | `components/ProgressVisualization.tsx` | Orchestrator progress display |
| Thinking Process | `components/ThinkingProcess.tsx` | Transparent AI reasoning |

**API Client** (`api.ts`): TypeScript singleton wrapping all backend calls with typed request/response interfaces. Supports streaming via `AsyncGenerator`.

### 2.2 Backend (Flask + Python)

**Core Entry Points:**
- `app.py` (1641 lines) - Flask routes, Gemini proxy, orchestrator endpoints
- `run_production.py` - Waitress WSGI production server
- `wsgi.py` - Alternative WSGI entry

**Orchestration Engines:**

1. **PEV Orchestrator** (`pev_orchestrator.py`) - LangGraph state machine:
   - Planner: Gemini-powered task decomposition (temp=0.1)
   - Executor: Resource routing via HybridOrchestrator
   - Verifier: Hallucination detection (temp=0.0), confidence scoring
   - Retry loop: max 2 attempts with verification feedback

2. **Hybrid Orchestrator** (`hybrid_orchestrator.py`) - Task router:
   - Decomposes requests into subtasks
   - Matches subtasks to resources by capability
   - Executes via ThreadPoolExecutor (parallel) or sequential
   - AI fallback when tools fail

**Tools (11 modules, 40+ functions):**
- `pdf_utilities.py` - merge, split, extract, convert
- `word_utilities.py` - create, extract, convert
- `excel_utilities.py` - read, create, pivot, chart
- `ocr_effocr.py` - offline OCR (EasyOCR, 80+ languages)
- `email_utilities.py` - draft, template, schedule
- `equipment_lookup.py`, `safety_validator.py`, `cost_estimator.py`
- `document_search.py`

**Workflows (3 async modules):**
- `maintenance_checklist.py`
- `incident_analyzer.py`
- `equipment_scheduler.py`

**Data Layer:**
- SQLite via SQLAlchemy ORM (`models.py`)
- Agent model with status tracking (DRAFT/PUBLISHED)
- Knowledge stored as JSON files per agent
- Feedback stored in `feedback_store.json`

### 2.3 AI Model Integration

All LLM calls go through Gemini API (`generativelanguage.googleapis.com/v1beta`):

| Use Case | Model | Temperature | Location |
|----------|-------|-------------|----------|
| Chat proxy | `gemini-2.5-flash-lite` | user-configured | `app.py:672` |
| Planning | `gemini-2.5-flash-lite` | 0.1 | `pev_orchestrator.py:278` |
| Verification | `gemini-2.5-flash-lite` | 0.0 | `pev_orchestrator.py:531` |
| Compilation | `gemini-2.5-flash-lite` | 0.3 | `pev_orchestrator.py:699` |
| Task Decomposition | `gemini-2.5-flash-lite` | 0.1 | `hybrid_orchestrator.py:209` |
| AI Fallback | `gemini-2.5-flash-lite` | 0.7 | `hybrid_orchestrator.py:1044` |
| Agent Execution | `gemini-2.5-flash-lite` | default | `app.py:1051` |

**Critical Finding**: The model name is hardcoded as a string literal in **13+ locations** across 3 files. There is no centralized model configuration. This is the primary blocker for local model integration.

---

## 3. Sandbox Environment Compatibility

### 3.1 Current State

| Aspect | Status | Details |
|--------|--------|---------|
| External API dependency | **BLOCKING** | App crashes on startup if `GEMINI_API_KEY` missing (`app.py:68-70` raises `ValueError`) |
| File system access | MODERATE | Writes to `backend/data/`, `backend/knowledge_storage/`, `backend/temp_uploads/` |
| Network access | HIGH | All LLM calls require internet to `generativelanguage.googleapis.com` |
| Port binding | OK | Configurable via `PORT` env var (default 8080) |
| Process model | OK | Waitress WSGI, configurable threads |
| Database | OK | SQLite file-based, no external DB required |
| Dependencies | MODERATE | PyTorch + EasyOCR are ~2GB; may exceed sandbox limits |

### 3.2 Issues for Sandboxed Deployment

1. **Hard crash without API key** (`app.py:68-70`):
   ```python
   if not GEMINI_API_KEY:
       raise ValueError("GEMINI_API_KEY must be set")
   ```
   This prevents the app from starting at all in a sandbox without an API key. Should be a warning with graceful degradation.

2. **No local model fallback**: Every LLM call targets the Gemini REST API. There is no abstraction layer, OpenAI-compatible endpoint support, or local model adapter.

3. **Heavy dependencies**: `torch==2.2.0` + `torchvision` + `easyocr` total ~2GB. In a constrained sandbox, these may fail to install or exceed memory limits.

4. **Temp file cleanup**: `tempfile.mkdtemp()` in `app.py:1260` creates directories but cleanup is not guaranteed on crash.

5. **Absolute paths**: Knowledge storage uses `os.path.dirname(__file__)` which is fine, but the database path (`backend/data/maher_ai.db`) assumes write permissions.

### 3.3 Recommendations for Sandbox Compatibility

- **Make API key optional**: Convert the hard crash to a warning; disable AI endpoints if no key is set.
- **Add a model abstraction layer**: Create a `ModelClient` class that can target Gemini API, OpenAI-compatible endpoints (for gptoss), or mock responses.
- **Make OCR/torch optional**: Wrap PyTorch imports in try/except; provide a lightweight mode without OCR.
- **Configure writable directories** via environment variables instead of hardcoding relative paths.
- **Add temp file cleanup** using `atexit` handlers or context managers.

---

## 4. Multi-User Handling Assessment

### 4.1 Current State

| Feature | Status | Details |
|---------|--------|---------|
| Authentication | **MISSING** | No login, no tokens, no session auth |
| User identity | MINIMAL | `created_by` field defaults to `default_user`; can pass `?user=<name>` in query |
| Data isolation | **MISSING** | All users see all published agents; knowledge bases are shared |
| Session management | **MISSING** | No session tracking; no conversation persistence server-side |
| Rate limiting | PER-IP | `Flask-Limiter` uses `get_remote_address` - shared IP = shared limits |
| Concurrent requests | PARTIAL | Waitress handles threads, but `asyncio.new_event_loop()` per request is not ideal |

### 4.2 Specific Multi-User Gaps

1. **Agent visibility** (`app.py:160-207`): Agents are filtered by `created_by`, but with no auth, any client can impersonate any user by passing `?user=<anyone>`.

2. **Knowledge storage** (`app.py:86-89`): Knowledge is keyed by `agent_id`, not by user. If two users create agents with similar workflows, they share the namespace.

3. **Database sessions** (`hybrid_orchestrator.py:57-80`): `SessionLocal()` is opened and closed per call with no connection pooling configuration. Under concurrent load, this could cause SQLite locking issues.

4. **Event loop per request** (`app.py:1216-1221`):
   ```python
   loop = asyncio.new_event_loop()
   asyncio.set_event_loop(loop)
   ```
   Creating a new event loop per request is expensive and not thread-safe. Under concurrent users, this can cause race conditions.

5. **No CSRF protection**: No CSRF tokens for state-changing operations.

### 4.3 Recommendations for Multi-User

- Add JWT or session-based authentication middleware
- Scope all data operations (agents, knowledge, feedback) by authenticated user ID
- Replace per-request event loops with a shared loop or use synchronous execution
- Add connection pooling for SQLite (`pool_size`, `pool_pre_ping`)
- Consider PostgreSQL for production multi-user deployments
- Add request-scoped logging with user context

---

## 5. Local Model (gptoss) Integration Readiness

### 5.1 Current Barriers

The codebase is **not ready** for gptoss or any local model. The barriers are:

1. **Hardcoded model names**: The string `gemini-2.5-flash-lite` appears in 13+ locations across `app.py`, `pev_orchestrator.py`, and `hybrid_orchestrator.py`.

2. **Hardcoded API base URL**: `https://generativelanguage.googleapis.com/v1beta` is set in 3 separate `__init__` methods.

3. **Gemini-specific request format**: The payload structure (`contents[].parts[].text`, `systemInstruction.parts[].text`, `x-goog-api-key` header) is Gemini-proprietary.

4. **Gemini-specific response parsing**: `response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')` is repeated 10+ times.

5. **No model abstraction**: There is no interface or adapter pattern. Each call site directly constructs Gemini HTTP requests.

6. **Frontend coupling**: `api.ts` interfaces (`GeminiGenerateRequest`, `GeminiResponse`) are Gemini-specific by name and structure.

### 5.2 Integration Architecture for gptoss

To support gptoss (or any OpenAI-compatible local model), the following abstraction is needed:

```
Recommended Architecture:

                    ┌──────────────────────┐
                    │   ModelClient ABC     │
                    │   - generate()        │
                    │   - stream()          │
                    │   - get_models()      │
                    └──────┬───────────────┘
                           │
              ┌────────────┼────────────────┐
              │            │                │
    ┌─────────▼──┐  ┌──────▼─────┐  ┌──────▼──────┐
    │ GeminiClient│  │GPTOSSClient│  │ MockClient  │
    │ (REST API)  │  │(local HTTP)│  │ (testing)   │
    └────────────┘  └────────────┘  └─────────────┘
```

**Key changes needed:**

| Change | Files Affected | Effort |
|--------|---------------|--------|
| Create `ModelClient` abstraction | New: `backend/model_client.py` | Medium |
| Replace hardcoded Gemini calls | `app.py`, `pev_orchestrator.py`, `hybrid_orchestrator.py` | High (13+ call sites) |
| Add gptoss adapter | New: `backend/clients/gptoss_client.py` | Medium |
| Environment-based model selection | `.env`, `app.py` | Low |
| Update frontend interfaces | `api.ts`, `types.ts` | Low |
| Add model health checking | `app.py` health endpoint | Low |

### 5.3 gptoss Configuration Template

```env
# Model Provider: gemini | gptoss | openai_compatible
MODEL_PROVIDER=gptoss

# gptoss Configuration
GPTOSS_BASE_URL=http://localhost:11434
GPTOSS_MODEL_NAME=maher-maintenance-7b
GPTOSS_API_KEY=  # optional for local

# Fallback behavior
FALLBACK_TO_GEMINI=false
GEMINI_API_KEY=  # optional if using gptoss only
```

---

## 6. Eval Recommendations

### 6.1 Current Eval Coverage

**Existing tests** (7 files, ~1500 lines total):

| Test File | What It Tests | Automated? | Uses Real API? |
|-----------|---------------|------------|----------------|
| `test_pev_orchestrator.py` | PEV flow, hallucination detection, retry | Manual (`main()`) | Yes (Gemini) |
| `test_hybrid_orchestrator.py` | Task routing, tool execution | Manual | Yes (HTTP to server) |
| `test_orchestrator.py` | Legacy orchestrator | Manual | Yes |
| `test_orchestrator_tools.py` | Individual tool execution | Manual | Yes |
| `test_document_tools.py` | PDF/Word/Excel processing | Manual | No |
| `test_document_routing.py` | File type detection, routing | Manual | No |
| `test_new_features.py` | Agent CRUD, knowledge upload | Manual | Yes |

**Gaps in current testing:**
- No automated test framework (no pytest, no unittest runner)
- No CI/CD pipeline
- No mocking - all tests require live Gemini API
- No performance/load testing
- No eval metrics collection over time
- No regression tracking

### 6.2 Recommended Eval Framework

#### Category 1: Unit Evals (No LLM Required)

These test internal logic without any model calls:

```
1. Tool Function Evals
   - PDF merge/split/extract with sample files
   - Word document creation and extraction
   - Excel read/write/pivot operations
   - OCR accuracy on known test images
   - Email template rendering

   Metrics: Success rate, output correctness, execution time
   Files: backend/tools/*.py

2. Orchestration Logic Evals
   - Task decomposition parsing (mock LLM responses)
   - Resource matching accuracy
   - Capability index lookup correctness
   - Registry loading and validation
   - Dependency graph resolution

   Metrics: Routing accuracy, match precision/recall
   Files: backend/hybrid_orchestrator.py, backend/registry.json

3. Data Layer Evals
   - Agent CRUD operations
   - Knowledge storage read/write
   - File parser accuracy across formats
   - Database migration safety

   Metrics: Data integrity, round-trip accuracy
   Files: backend/models.py, backend/file_parser.py

4. API Contract Evals
   - All 20+ endpoints return correct status codes
   - Request validation (missing fields, bad types)
   - Rate limiting enforcement
   - CORS header correctness
   - Error response format consistency

   Metrics: Contract compliance, edge case coverage
   Files: backend/app.py
```

#### Category 2: LLM Quality Evals (Require Model)

These measure AI output quality and should run against both Gemini and gptoss:

```
5. Hallucination Detection Evals
   - Feed known-false claims → verify the verifier catches them
   - Feed real-time data requests → verify "no data" acknowledgment
   - Feed partial data → verify confidence score reflects incompleteness

   Metrics:
   - Hallucination detection rate (target: >99%)
   - False positive rate (target: <5%)
   - Confidence score calibration

   Test Cases:
   a) "What was the pressure reading on V-101 at 2pm?" → should flag no real-time data
   b) "List all 47 pumps in Plant 3" → should not invent pump names
   c) "When was the last maintenance on Compressor C-500?" → should acknowledge no records

6. Task Routing Accuracy Evals
   - 50+ diverse queries mapped to expected resource types
   - Measure first-try routing accuracy
   - Measure capability match precision

   Metrics:
   - Routing accuracy (target: >90%)
   - Decomposition quality (subtask relevance)
   - Strategy selection correctness (parallel vs sequential)

   Test Cases:
   a) "Merge these two PDFs" → should route to pdf_utilities.merge
   b) "What pump maintenance is due?" → should route to equipment_scheduler
   c) "Generate a safety checklist" → should route to maintenance_checklist workflow

7. Response Quality Evals
   - Domain accuracy: maintenance terminology correctness
   - Safety compliance: guardrails present in safety-related responses
   - Completeness: all parts of multi-part questions answered
   - Citation: sources referenced when data is used

   Metrics:
   - Domain accuracy score (human-rated 1-5)
   - Safety guardrail presence (binary per response)
   - Completeness score (0.0-1.0)
   - Citation rate

8. Prompt Robustness Evals
   - Adversarial inputs (prompt injection attempts)
   - Edge cases (empty input, very long input, special characters)
   - Multi-language inputs
   - Ambiguous queries requiring clarification

   Metrics:
   - Injection resistance rate
   - Graceful degradation rate
   - Clarification request rate for ambiguous inputs
```

#### Category 3: System Evals (Infrastructure)

```
9. Performance Evals
   - Response latency percentiles (P50, P95, P99)
   - Throughput under concurrent users (5, 10, 25, 50)
   - Memory usage under sustained load
   - SQLite lock contention under concurrent writes
   - File upload processing time by size

   Metrics: Latency, throughput, memory, error rate under load

10. Reliability Evals
    - API timeout handling (simulate slow Gemini responses)
    - Graceful degradation when Gemini is down
    - Recovery after database corruption
    - Temp file cleanup after crashes
    - Rate limiter correctness under burst traffic

    Metrics: Recovery time, data loss, cleanup completeness

11. Security Evals
    - API key exposure in responses/logs
    - File upload path traversal attempts
    - XSS in agent system prompts rendered in UI
    - SQL injection in agent search queries
    - CORS enforcement verification

    Metrics: Vulnerability count, exposure incidents
```

#### Category 4: Model Comparison Evals (Gemini vs gptoss)

```
12. Model Parity Evals
    - Run identical eval suite against both Gemini and gptoss
    - Compare on all quality metrics
    - Identify quality gaps requiring prompt tuning

    Metrics:
    - Quality delta per eval category
    - Latency comparison
    - Cost comparison (API cost vs compute cost)

    Test Matrix:
    | Eval | Gemini Score | gptoss Score | Delta | Acceptable? |
    |------|-------------|--------------|-------|-------------|
    | Hallucination Detection | ? | ? | ? | <5% gap |
    | Routing Accuracy | ? | ? | ? | <10% gap |
    | Response Quality | ? | ? | ? | <15% gap |
    | Latency (P95) | ? | ? | ? | gptoss faster |
```

### 6.3 Eval Implementation Priorities

| Priority | Eval Category | Rationale | Effort |
|----------|--------------|-----------|--------|
| **P0** | Unit evals (tools, routing, API) | No LLM needed, catches regressions | Low |
| **P0** | Hallucination detection evals | Core product differentiator | Medium |
| **P1** | Task routing accuracy | Directly impacts user experience | Medium |
| **P1** | Model parity (Gemini vs gptoss) | Required for gptoss rollout | High |
| **P2** | Performance/load evals | Multi-user readiness | Medium |
| **P2** | Security evals | Production hardening | Medium |
| **P3** | Response quality (human-rated) | Ongoing quality program | High |

### 6.4 Suggested Eval Infrastructure

```
/backend/evals/
├── conftest.py                  # pytest fixtures, mock LLM client
├── test_tools/
│   ├── test_pdf_utilities.py
│   ├── test_word_utilities.py
│   ├── test_excel_utilities.py
│   ├── test_ocr.py
│   └── fixtures/               # Sample PDF, DOCX, XLSX files
├── test_orchestration/
│   ├── test_routing_accuracy.py
│   ├── test_decomposition.py
│   ├── test_pev_flow.py
│   └── golden_responses/       # Expected outputs for regression
├── test_api/
│   ├── test_agent_endpoints.py
│   ├── test_chat_endpoints.py
│   ├── test_knowledge_endpoints.py
│   └── test_rate_limiting.py
├── test_llm_quality/
│   ├── test_hallucination.py
│   ├── test_safety_guardrails.py
│   ├── test_response_quality.py
│   ├── test_prompt_robustness.py
│   └── eval_datasets/          # JSON files with test cases + expected behavior
├── test_model_parity/
│   ├── test_gemini_vs_gptoss.py
│   └── comparison_report.py
├── test_performance/
│   ├── test_latency.py
│   ├── test_concurrency.py
│   └── locustfile.py           # Load testing with Locust
└── test_security/
    ├── test_injection.py
    ├── test_file_upload.py
    └── test_cors.py
```

---

## 7. Critical Issues Summary

### Blockers (Must Fix)

| # | Issue | File(s) | Impact |
|---|-------|---------|--------|
| 1 | App crashes without GEMINI_API_KEY | `app.py:68-70` | Cannot start in sandbox without key |
| 2 | Hardcoded model name in 13+ locations | `app.py`, `pev_orchestrator.py`, `hybrid_orchestrator.py` | Cannot switch to gptoss |
| 3 | No model abstraction layer | All backend files | Every model change requires editing 3+ files |
| 4 | Gemini-specific request/response format | All LLM call sites | gptoss uses OpenAI-compatible format |

### High Priority (Should Fix)

| # | Issue | File(s) | Impact |
|---|-------|---------|--------|
| 5 | No authentication | `app.py` | Any user can impersonate another |
| 6 | `asyncio.new_event_loop()` per request | `app.py:1216-1221` | Thread-unsafe under concurrent users |
| 7 | SQLite without connection pooling | `models.py:108` | Lock contention under load |
| 8 | No automated test runner | `test_*.py` | All tests are manual scripts |
| 9 | No temp file cleanup guarantee | `app.py:1260` | Disk space leak |

### Medium Priority (Nice to Fix)

| # | Issue | File(s) | Impact |
|---|-------|---------|--------|
| 10 | PyTorch/EasyOCR mandatory | `requirements.txt` | 2GB dependency for optional feature |
| 11 | Agent data isolation by user | `app.py:160-207` | Users can see others' agents via URL manipulation |
| 12 | No CSRF protection | `app.py` | State-changing POST endpoints vulnerable |
| 13 | Feedback stored in flat JSON file | `hybrid_orchestrator.py:46` | Not scalable, no user scoping |

---

## 8. Recommended Implementation Roadmap

### Phase 1: Sandbox Compatibility + Basic Evals
- Make GEMINI_API_KEY optional with graceful degradation
- Create `ModelClient` abstraction with Gemini adapter
- Add pytest infrastructure with mock model client
- Implement P0 unit evals (tools, routing, API contracts)
- Make PyTorch/OCR optional imports

### Phase 2: gptoss Integration
- Implement gptoss adapter for `ModelClient`
- Add environment-based model provider selection
- Normalize request/response format across providers
- Implement model parity eval suite
- Run comparison benchmarks

### Phase 3: Multi-User Hardening
- Add JWT authentication middleware
- Scope all data by authenticated user
- Replace SQLite with PostgreSQL for production
- Fix async event loop handling
- Add connection pooling
- Implement CSRF protection

### Phase 4: Production Eval Pipeline
- CI/CD with automated eval suite
- Eval metrics dashboard
- Golden response regression tests
- Performance benchmarking with Locust
- Security scanning integration

---

*Generated: 2026-02-03*
*Branch: claude/codebase-analysis-evals-57nJ7*
