# Testing the Hybrid Orchestrator Frontend

## ✅ What Was Updated

The frontend now connects to the new **Hybrid Orchestrator** instead of the old orchestrator.

### Changes Made:
1. **Endpoint Changed**: `/api/orchestrator/process` → `/api/hybrid-orchestrator/process`
2. **Response Formatting**: Beautiful display of workflow/tool/AI agent results
3. **Visual Indicators**:
   - ⚙️ Workflows
   - 🔧 Tools
   - 🤖 AI Agents

## 🚀 How to Test

### 1. Start the Backend Server

```bash
cd backend
python run_production.py
```

The server should start on port **8080** (or your configured PORT).

### 2. Open Your Browser

Navigate to: `http://localhost:8080`

### 3. Try These Test Queries

#### Test Workflow - Maintenance Checklist
```
Generate a preventive maintenance checklist for a centrifugal pump
```

**Expected Result:**
- Shows "⚙️ Maintenance Checklist Generator"
- Displays checklist items, safety notes, required tools
- Shows execution strategy

#### Test Tool - Equipment Lookup
```
Look up specifications for equipment PUMP-001
```

**Expected Result:**
- Shows "🔧 Equipment Database Lookup"
- Displays manufacturer, model, specs, location

#### Test Multi-Resource Query
```
I need a maintenance checklist and cost estimate for pump maintenance taking 4 hours
```

**Expected Result:**
- Shows multiple resources used (workflow + tool)
- Displays parallel/sequential execution
- Shows both checklist AND cost breakdown

#### Test Incident Analysis
```
Analyze an incident where a pump had excessive vibration and overheating
```

**Expected Result:**
- Shows "⚙️ Incident Report Analyzer"
- Lists identified root causes
- Provides prioritized recommendations

#### Test Document Search
```
Search for pump maintenance procedures
```

**Expected Result:**
- Shows "🔧 Technical Document Search"
- Lists relevant documents with revision numbers

## 📊 What You'll See

The frontend now displays responses like this:

```
🎯 MAHER Hybrid Orchestrator
Strategy: parallel | Subtasks: 2/2 successful
Resources: ⚙️ Maintenance Checklist Generator, 🔧 Cost Estimator

---

### Maintenance Checklist Generator

Checklist Items:
1. Replace mechanical seals
2. Change bearing lubrication
3. Inspect and clean strainer/filter
...

Safety Notes:
- Lock out / Tag out all energy sources
- Full PPE including face shield if needed
...

Required Tools:
- Complete tool set
- Bearing puller
- Alignment tools
...

Estimated Duration: 2.0 hours

### Cost Estimator

Cost Estimate:
- Labor: $375
- Parts: $550
- Downtime: $8000
- Total: $9175
- Confidence: 75%
```

## 🔍 Debugging

If something doesn't work:

### Check Backend Logs
The server will show which resources were matched and executed:
```
INFO - Decomposed into 2 subtasks with parallel execution
INFO - Executing agent: Maintenance Checklist Generator
```

### Check Browser Console
Open DevTools (F12) and check the Console for any errors.

### Verify Endpoint
In the Network tab, confirm requests go to:
- ✅ `/api/hybrid-orchestrator/process`
- ❌ NOT `/api/orchestrator/process`

## 🎨 Response Formatting

The frontend intelligently formats different response types:

| Resource Type | What It Shows |
|---------------|---------------|
| **Maintenance Checklist** | Numbered items, safety notes, tools, duration |
| **Equipment Lookup** | Specs, manufacturer, model, location, criticality |
| **Cost Estimator** | Labor/parts/downtime breakdown, total, confidence |
| **Incident Analyzer** | Root causes, prioritized recommendations |
| **Document Search** | Document titles, types, revision numbers |
| **Safety Validator** | Compliance level, missing items, recommendations |
| **AI Agent** | Natural language response |

## ⚠️ Known Behaviors

1. **First request may be slower** - The orchestrator needs to decompose the task using AI
2. **Workflows are fast** - You'll see instant responses for tools/workflows
3. **AI agents are slower** - Still makes API calls to Gemini
4. **Parallel execution** - Multiple resources execute simultaneously

## 📝 Notes

- The frontend automatically rebuilds when you run `npm run build`
- Dist folder is gitignored (built on server deployment)
- All changes are committed to branch: `claude/update-image-sources-01RJ5U5EwniF2YxK2zTmDYn3`

## 🐛 Troubleshooting

### "Orchestrator request failed"
- Check backend server is running
- Verify port is 8080 (or your PORT env var)

### "No resources could be matched"
- This means your query needs AI agent handling
- Try rephrasing with more specific terms like "pump", "checklist", "cost"

### Empty or weird response
- Check browser console for errors
- Verify backend registry.json is loaded correctly
- Check backend logs for Python errors

## 🎯 Success Criteria

You'll know it's working when you see:
✅ "🎯 MAHER Hybrid Orchestrator" header
✅ Resource icons (⚙️, 🔧, 🤖)
✅ Execution strategy (parallel/sequential)
✅ Nicely formatted results (not raw JSON)
✅ Subtask success count (e.g., "2/2 successful")

Enjoy the new Hybrid Orchestrator! 🚀
