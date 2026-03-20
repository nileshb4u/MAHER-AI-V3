# How to Verify Orchestrator is Using All 35 Tools

This guide shows you how to verify that the MAHER Hybrid Orchestrator can access and use all 35 tools.

## Quick Verification

Run the comprehensive test script:

```bash
cd backend
python test_orchestrator_tools.py
```

**Expected Output:**
```
Total tools registered: 35
Importable tools: 35/35 (100%)
Callable tools: 35/35 (100%)
Indexed in capabilities: 35/35 (100%)

🎉 SUCCESS: All tools are accessible to the orchestrator!
```

## What This Tests

The test script verifies:

1. ✅ **Registry Structure** - All tools are properly registered in `registry.json`
2. ✅ **Tool Imports** - All tool modules can be imported without errors
3. ✅ **Tool Callable** - All tool functions exist and are callable
4. ✅ **Capability Index** - All tools are indexed by their capabilities for intelligent routing
5. ✅ **Orchestrator Integration** - The HybridOrchestrator can load and match tools

## Tool Breakdown (35 Total)

### Original MAHER Tools (5)
- Parts Inventory Checker (REST API)
- Equipment Database Lookup
- Safety Procedure Validator
- Maintenance Cost Estimator
- Technical Document Search

### PDF Tools (7)
- PDF Merge Tool
- PDF Split Tool
- PDF Text Extractor
- PDF Table Extractor
- Convert to PDF
- PDF to Word Converter
- PDF Information

### OCR Tools (2)
- Local Offline OCR (EasyOCR)
- Local PDF OCR

### Word/DOCX Tools (8)
- Word Document Creator
- Word Text Extractor
- Word Headings Extractor
- Word Table Extractor
- Word to PDF Converter (Direct)
- Word to HTML Converter
- Add Table to Word
- Word Document Information

### Excel Tools (8)
- Excel Reader
- Excel Creator
- Excel Modifier
- Excel Pivot Table Creator
- Excel Chart Generator
- Excel Data Analyzer
- Excel to CSV Converter
- Excel Information

### Email Tools (5)
- Email Draft Generator
- Email Template Generator
- Email Scheduler
- Email Parser
- Email Signature Generator

## How the Orchestrator Uses Tools

### 1. Task Decomposition

When you send a request to the orchestrator:

```python
orchestrator.process_request("Convert this Word doc to PDF and extract tables")
```

The orchestrator:
1. Decomposes the request into subtasks
2. Identifies required capabilities for each subtask
3. Matches capabilities to tools from the registry
4. Executes the matched tools
5. Integrates results into a unified response

### 2. Capability Matching

The orchestrator uses 58 different capabilities to match tools:

```
• pdf_processing: 7 resources
• word_processing: 8 resources
• excel_processing: 8 resources
• email_automation: 5 resources
• ocr: 3 resources
• document_conversion: 2 resources
• data_analysis: 2 resources
... and 51 more
```

### 3. Example Flow

**User Request:** "Convert my Word report to PDF and extract the tables"

**Orchestrator Processing:**
```
Step 1: Decompose
  - Subtask 1: Convert Word to PDF
    Required capabilities: [word_processing, document_conversion]

  - Subtask 2: Extract tables from PDF
    Required capabilities: [pdf_processing, table_extraction]

Step 2: Match Resources
  - Subtask 1 → "Word to PDF Converter" (tool_word_to_pdf)
  - Subtask 2 → "PDF Table Extractor" (tool_pdf_extract_tables)

Step 3: Execute
  - Execute word_to_pdf_direct(input.docx, output.pdf)
  - Execute extract_tables_from_pdf(output.pdf)

Step 4: Integrate Results
  - Return: PDF file + extracted tables
```

## Verify Specific Tool Capabilities

### Check which tools handle PDF processing:

```python
from hybrid_orchestrator import HybridOrchestrator

orchestrator = HybridOrchestrator()
capability_index = orchestrator.registry['capability_index']

pdf_tools = capability_index.get('pdf_processing', [])
print(f"PDF processing tools: {pdf_tools}")
# Output: 7 tool IDs
```

### Check which tools handle OCR:

```python
ocr_tools = capability_index.get('ocr', [])
print(f"OCR tools: {ocr_tools}")
# Output: ['tool_pdf_extract_text', 'tool_ocr_local', 'tool_ocr_pdf_local']
```

## Manual Verification

### 1. Check Registry File

```bash
cat backend/registry.json | jq '.resources.tools | length'
# Should output: 35
```

### 2. Check Capability Index

```bash
cat backend/registry.json | jq '.capability_index | keys | length'
# Should output: 58
```

### 3. Test Individual Tool Import

```python
# Test PDF tools
from tools.pdf_utilities import merge_pdfs, split_pdf, extract_text_from_pdf
print("✓ PDF tools imported")

# Test Word tools
from tools.word_utilities import create_word_doc, word_to_pdf, extract_text_from_word
print("✓ Word tools imported")

# Test Excel tools
from tools.excel_utilities import read_excel, create_excel, modify_excel
print("✓ Excel tools imported")

# Test Email tools
from tools.email_utilities import generate_email_draft, schedule_email
print("✓ Email tools imported")

# Test OCR tools
from tools.ocr_effocr import ocr_image_local, ocr_pdf_local
print("✓ OCR tools imported")
```

## Troubleshooting

### Issue: "No module named 'X'"

**Solution:** Install missing dependencies
```bash
pip install -r requirements.txt
```

### Issue: "NumPy compatibility error"

**Solution:** Downgrade NumPy for PyTorch compatibility
```bash
pip install "numpy<2.0"
```

### Issue: "Tool not found in registry"

**Solution:** Verify registry.json has the tool definition and reload
```python
orchestrator = HybridOrchestrator()
orchestrator.registry = orchestrator._load_registry()
```

## Testing Tool Execution

### Quick Test - Direct Tool Call

```python
# Test Word to PDF (your explicit request)
from tools.word_to_pdf_direct import word_to_pdf_direct

result = word_to_pdf_direct(
    input_file="test.docx",
    output_file="test.pdf"
)

if result['success']:
    print("✓ Word to PDF working")
```

### Quick Test - OCR (your explicit request)

```python
# Test Local Offline OCR
from tools.ocr_effocr import ocr_image_local

result = ocr_image_local(
    image_path="test_image.png",
    engine="easyocr",
    languages=['en']
)

if result['success']:
    print("✓ Local OCR working")
    print(f"Extracted text: {result['text'][:100]}...")
```

### Full Integration Test - Via Orchestrator

```python
import asyncio
from hybrid_orchestrator import HybridOrchestrator

async def test_orchestrator():
    orchestrator = HybridOrchestrator()

    # Test document processing request
    result = await orchestrator.process_request(
        "Convert Word document to PDF and extract text"
    )

    print(f"Success: {result['success']}")
    print(f"Resources used: {len(result['results']['results'])}")
    print(f"Strategy: {result['execution_summary']['strategy']}")

asyncio.run(test_orchestrator())
```

## Registry File Location

All tools are registered in:
```
/home/user/MAHER_NEW_UI/backend/registry.json
```

Structure:
```json
{
  "version": "1.1.0",
  "resources": {
    "tools": [ /* 35 tools */ ],
    "workflows": [ /* 3 workflows */ ],
    "ai_agents": [ /* dynamic from DB */ ]
  },
  "capability_index": { /* 58 capabilities */ }
}
```

## Verification Checklist

- [ ] Run `python test_orchestrator_tools.py` - shows 35/35 tools accessible
- [ ] Verify NumPy version < 2.0 for OCR functionality
- [ ] Check all dependencies installed: `pip list | grep -E "pypdf|openpyxl|easyocr"`
- [ ] Test Word to PDF: `python test_new_features.py`
- [ ] Test OCR: `python check_ocr.py`
- [ ] Verify registry has 35 tools: `cat registry.json | jq '.resources.tools | length'`

## Success Criteria

✅ **All 35 tools accessible to orchestrator**
✅ **All tools properly indexed by capabilities**
✅ **Orchestrator can match user requests to tools**
✅ **Tools can be executed without import errors**
✅ **OCR works offline with local models**
✅ **Word to PDF works without MS Office**

---

**Last Updated:** 2025-11-15
**Total Tools:** 35
**Status:** All operational
