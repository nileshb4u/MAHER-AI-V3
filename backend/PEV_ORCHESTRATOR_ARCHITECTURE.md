# Plan-Execute-Verify (PEV) Orchestrator Architecture

## Overview

The PEV Orchestrator implements a **"Trustworthy, SME-Driven, Deterministic AI"** architecture that acts as the central "Brain" of the MAHER AI framework. Unlike standard chatbots that simply generate text, this orchestrator acts as a Router and Project Manager, preventing hallucinations through rigorous verification.

## Core Philosophy

**"Plan → Execute → Verify"** - Every response goes through three distinct phases:

1. **Planning** - Understand intent, decompose tasks, select appropriate agents
2. **Execution** - Route to domain specialists, collect raw data
3. **Verification** - Rigorously verify data against original question, reject hallucinations

## Architecture Pattern

```
User Input → Planner → Executor → Verifier → [Decision]
                ↑                              ↓
                └────────── Retry ─────────────┘
                           (if verification fails)
```

### State Machine Implementation

Implemented using **LangGraph** for cyclic state management:

```python
from langgraph.graph import StateGraph

workflow = StateGraph(OrchestratorState)
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)
workflow.add_node("verifier", verifier_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "executor")
workflow.add_edge("executor", "verifier")
workflow.add_conditional_edges("verifier", should_continue, {
    "accept": END,
    "retry": "planner",
    "max_retries": END
})
```

## Module Breakdown

### 1. Planner (Integration Hub Core)

**Location**: `pev_orchestrator.py:_planner_node()`

**Responsibilities**:
- **Intent Recognition**: Analyzes user input using NLP
- **Dynamic Lookup**: Consults Domain Agent Registry for available capabilities
- **Task Decomposition**: Breaks complex queries into dependency graphs
- **Constraint Enforcement**: Only routes to available agents (no invented capabilities)

**Key Features**:
- Low temperature (0.1) for deterministic planning
- Retry-aware: Incorporates previous verification feedback
- Outputs structured `ExecutionPlan` with Pydantic validation

**Example Output**:
```json
{
  "subtasks": [
    {
      "id": "subtask_1",
      "description": "Check vibration data for pump P-101",
      "preferred_resource_type": "tool",
      "required_capabilities": ["vibration_analysis", "sensor_data"],
      "priority": 1,
      "dependencies": []
    }
  ],
  "execution_strategy": "sequential",
  "reasoning": "Query requires real-time sensor data, routed to vibration tool"
}
```

### 2. Executor (Task Manager)

**Location**: `pev_orchestrator.py:_executor_node()`

**Responsibilities**:
- **Routing**: Dispatches tasks to correct Domain Agents
- **Data Aggregation**: Collects raw outputs (JSON, SQL results, logs)
- **Context Passing**: Enables Agent A output → Agent B input workflows

**Key Features**:
- Reuses `HybridOrchestrator` execution logic for compatibility
- Collects **raw data** separately for verification
- Tracks success/failure per subtask

**Data Collection**:
```python
raw_data = [
    {
        'subtask': 'Check vibration data',
        'data': {'sensor_reading': 2.3, 'unit': 'mm/s'},
        'source': 'Vibration Analysis Tool'
    }
]
```

### 3. Verifier (Quality Control - Hallucination Prevention)

**Location**: `pev_orchestrator.py:_verifier_node()`

**THE KEY DIFFERENTIATOR** - This module prevents hallucinations.

**Responsibilities**:
1. **Self-Correction**: Compares raw data against original question
2. **Looping**: Rejects insufficient/irrelevant data, sends back to Planner
3. **Citation Enforcement**: Ensures all claims are backed by data

**Verification Checklist**:

```python
verification_result = {
    "data_completeness": 0.0-1.0,  # Does data answer the question?
    "relevance_score": 0.0-1.0,     # Is data relevant to query?
    "hallucination_detected": bool, # Would answering require invented info?
    "confidence_score": 0.0-1.0,    # Overall confidence
    "action": "accept|retry"        # Decision
}
```

**Decision Logic**:
- `data_completeness >= 0.7 AND relevance >= 0.7 AND no_hallucination` → **ACCEPT**
- `retry_count < max_retries AND (low_completeness OR low_relevance)` → **RETRY**
- Otherwise → **ACCEPT with warning**

**Example Verification**:
```json
{
  "verified": true,
  "confidence_score": 0.92,
  "data_completeness": 0.95,
  "relevance_score": 0.90,
  "hallucination_detected": false,
  "missing_information": [],
  "action": "accept"
}
```

### 4. Domain Agent Library (The Workers)

**Location**: Registry (`registry.json`) + Database (`models.Agent`)

**Characteristics**:
- **Isolation**: Each agent is standalone with specific permissions
- **Tool Usage**: Connects to Data Query Manager (SAP BW, DCS, System1)
- **Plug-and-Play**: Agents can be added/removed without restarting

**Agent Types**:
1. **AI Agents** (from database) - Natural language specialists
2. **Tools** (from registry) - Document processing, inventory checks, etc.
3. **Workflows** (from registry) - Multi-step Python modules

## Success Metrics

As defined in the PRD:

| Metric | Target | How Measured |
|--------|--------|--------------|
| **Hallucination Rate** | < 1% | % of responses where `hallucination_detected = true` |
| **Routing Accuracy** | High | % of queries sent to correct agent on first try |
| **Data Completeness** | > 70% | Average `data_completeness` score from Verifier |
| **Resolution Time** | Optimized | Time from Request → Verified Response |

## API Endpoints

### 1. Process Request (No Files)

```bash
POST /api/pev-orchestrator/process
Content-Type: application/json

{
  "input": "Check pump P-101 vibration status",
  "user_id": "123",
  "user_role": "Maintenance Engineer"
}
```

**Response**:
```json
{
  "success": true,
  "request_id": "REQ-20250927-143022",
  "trace_id": "TRACE-20250927-143022-123456",
  "answer": "Verified response text...",
  "verification": {
    "verified": true,
    "confidence_score": 0.92,
    "data_completeness": 0.95,
    "relevance_score": 0.90,
    "hallucination_detected": false,
    "retry_count": 0
  },
  "execution_summary": {
    "total_subtasks": 2,
    "successful": 2,
    "failed": 0,
    "strategy": "sequential"
  },
  "thinking_process": [...],
  "timestamp": "2025-09-27T14:30:22Z"
}
```

### 2. Process with Files

```bash
POST /api/pev-orchestrator/process-with-files
Content-Type: multipart/form-data

input: "Convert this Excel file to PDF"
files: sales_data.xlsx
user_role: "Analyst"
```

### 3. Get Metrics

```bash
GET /api/pev-orchestrator/metrics
```

**Response**:
```json
{
  "hallucination_rate": 0.005,
  "average_confidence": 0.85,
  "total_requests": 1250,
  "verification_passes": 1180,
  "verification_retries": 70
}
```

## Integration with Existing Code

The PEV Orchestrator **coexists** with the existing `HybridOrchestrator`:

- **HybridOrchestrator** (`/api/hybrid-orchestrator/process`) - Still available, no breaking changes
- **PEVOrchestrator** (`/api/pev-orchestrator/process`) - New, enhanced with verification

**Execution Logic Reuse**:
```python
# PEV Executor delegates to HybridOrchestrator for actual execution
from hybrid_orchestrator import HybridOrchestrator
executor = HybridOrchestrator(...)
result = await executor.execute_resource(resource, subtask)
```

This ensures:
- ✅ No duplication of tool/workflow execution code
- ✅ All existing tools and agents work immediately
- ✅ Backward compatibility maintained

## Hallucination Prevention in Action

### Example 1: Data-Grounded Response

**User**: "What is preventive maintenance?"

**Planner**: Routes to AI Agent (general knowledge)
**Executor**: Gets AI response
**Verifier**: ✅ Accepts (general knowledge, no real-time data needed)
**Result**: Clean response

---

### Example 2: Insufficient Data

**User**: "What was pump P-101 vibration at 3pm yesterday?"

**Planner**: Routes to Vibration Tool
**Executor**: Tool returns "No historical data available"
**Verifier**:
- `data_completeness`: 0.2
- `hallucination_detected`: true (would need to invent data)
- `action`: "retry"

**Planner (Retry)**: Creates new plan to explain limitation
**Executor**: AI agent acknowledges data limitation
**Verifier**: ✅ Accepts (truthful about limitation)
**Result**: "I don't have access to historical vibration data for that timeframe."

---

### Example 3: Multi-Step with Verification

**User**: "Check pump health and order parts if needed"

**Planner**:
1. Subtask 1: Check pump health → Diagnostic Tool
2. Subtask 2: Check parts inventory → Inventory Tool
3. Subtask 3: Order parts → Workflow

**Executor**: Executes all 3, collects raw data
**Verifier**:
- Checks if diagnostic data supports "needs parts" claim
- Verifies inventory data before ordering
- ✅ Accepts only if data chain is complete

**Result**: Evidence-based response with clear data trail

## Configuration

### Environment Variables

```bash
GEMINI_API_KEY=your_key_here  # Required for AI calls
```

### Registry Setup

PEV Orchestrator reads from `registry.json` to discover:
- Available tools (document converters, APIs, etc.)
- Workflows (Python modules)
- Capability mappings

### Max Retries

```python
orchestrator = PEVOrchestrator(max_retries=2)
```

Default: 2 retries before accepting with warning

## Testing

Run the test suite:

```bash
cd backend
python test_pev_orchestrator.py
```

**Test Coverage**:
1. Simple query (AI agent)
2. Hallucination-prone query (triggers verification)
3. Multi-step query (task decomposition)
4. Verification retry (loop-back behavior)

## Monitoring & Observability

Each request includes:

- **`trace_id`**: Unique identifier for end-to-end tracking
- **`thinking_process`**: Step-by-step transparency
- **`verification`**: Detailed metrics on data quality

Use these for:
- Debugging verification failures
- Analyzing hallucination patterns
- Improving agent selection logic

## Future Enhancements

1. **Metrics Collection**: Persistent storage of verification statistics
2. **Learning from Feedback**: Improve planning based on user thumbs-up/down
3. **Advanced Routing**: ML-based agent selection
4. **Parallel Execution**: When subtasks are independent
5. **Streaming Responses**: Real-time updates during long executions

## References

- **PRD Document**: See original PRD for full specifications
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Pydantic**: Used for strict type validation of state

---

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Key**:
   ```bash
   export GEMINI_API_KEY=your_key
   ```

3. **Test the Orchestrator**:
   ```bash
   python test_pev_orchestrator.py
   ```

4. **Use in Production**:
   ```python
   from pev_orchestrator import PEVOrchestrator

   orchestrator = PEVOrchestrator()
   result = orchestrator.process_request(
       user_input="Your query here",
       user_role="Engineer"
   )

   print(result['answer'])
   print(f"Confidence: {result['verification']['confidence_score']}")
   ```

---

**Built with the core principle**: *Better to acknowledge limitation than to hallucinate.*
