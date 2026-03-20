# Orchestrator Document Tools Fix

## Problem Identified

When you ran `python run_production.py` and sent the request **"convert this file to pdf"**, the orchestrator routed it to an AI agent (GeoInsight Assistant) instead of using the document conversion tools.

### Why This Happened

The orchestrator's task decomposition prompt only knew about maintenance/engineering capabilities. It didn't know about the 35 document processing tools we added, so it defaulted to using AI agents.

## Fix Applied

Updated `hybrid_orchestrator.py` line 92-123 to include document processing capabilities in the task decomposition prompt.

### Before (Old Prompt)
```python
Available capability types:
- maintenance_planning, checklist_generation, scheduling
- incident_analysis, root_cause_analysis
- inventory_check, equipment_lookup
- safety_validation, cost_estimation
- document_search, technical_data
- natural_language_processing, analysis, recommendations
```

### After (New Prompt)
```python
Available capability types:
MAINTENANCE & ENGINEERING:
- maintenance_planning, checklist_generation, scheduling
- incident_analysis, root_cause_analysis
- inventory_check, equipment_lookup
- safety_validation, cost_estimation
- document_search, technical_data

DOCUMENT PROCESSING (use 'tool' resource type):
- pdf_processing: merge PDFs, split PDF, extract text/tables, convert to/from PDF, OCR
- word_processing: create Word docs, extract text/tables/headings, convert to PDF/HTML, add content
- excel_processing: read/create/modify Excel, pivot tables, charts, data analysis, export CSV
- email_automation: generate drafts, templates, signatures, schedule, parse emails
- document_conversion: Word→PDF, PDF→Word, HTML, CSV, format conversions
- ocr: offline OCR with EasyOCR, extract text from images/scanned PDFs
- text_extraction: extract text from PDFs, Word docs, tables
- table_extraction: extract tables from PDFs, Word, Excel

AI CAPABILITIES:
- natural_language_processing, analysis, recommendations

IMPORTANT: For document operations (PDF, Word, Excel, email), prefer 'tool' resource type.
```

## Testing the Fix

Run the routing test to verify document requests are now routed to tools:

```bash
cd backend

# Make sure GEMINI_API_KEY is set
export GEMINI_API_KEY='your-api-key-here'

# Run the routing test
python test_document_routing.py
```

**Expected output:**
```
Test 1: Convert my Word document to PDF
────────────────────────────────────────────────────────────────────────────────
✓ Decomposed into 1 subtask(s)

  Subtask 1: Convert Word document to PDF
    Resource type: tool
    Capabilities: word_processing, document_conversion
    ✓ Correct resource type
    ✓ Matched to: Word to PDF Converter
    Tool type: tool

  ✅ Test 1 PASSED

...

🎉 SUCCESS: All document requests routed correctly to tools!
```

## How to Use Document Tools Correctly

### Important: File Paths Required

The document tools need actual file paths to work. When using the orchestrator, you need to provide:

1. **Input file path** (what to convert)
2. **Output file path** (where to save the result)
3. **File type** (Word, Excel, PDF, etc.)

### Example Requests That Will Work

#### Good Request Format:
```
"Convert the Word document at /path/to/report.docx to PDF and save it as /path/to/report.pdf"
```

#### Better Request (More Specific):
```
{
  "input": "Convert Word to PDF",
  "parameters": {
    "input_file": "/path/to/report.docx",
    "output_file": "/path/to/report.pdf"
  }
}
```

#### Bad Request (Won't Work):
```
"convert this file to pdf"
```
**Why it won't work:** No file specified, no file type specified

### Making It Work in Production

For your landing page UI, you need to:

1. **File Upload Handling**: Allow users to upload files
2. **Automatic File Type Detection**: Detect if it's a Word doc, Excel file, etc.
3. **Temporary File Storage**: Store uploaded files temporarily
4. **Provide Full Paths**: Pass full file paths to the orchestrator

### Example: Frontend → Backend Flow

#### Frontend (Upload File)
```javascript
// User uploads file
const formData = new FormData();
formData.append('file', uploadedFile);
formData.append('action', 'convert_to_pdf');

fetch('/api/hybrid-orchestrator/process-file', {
  method: 'POST',
  body: formData
})
```

#### Backend (Process File)
```python
@app.route('/api/hybrid-orchestrator/process-file', methods=['POST'])
async def process_file():
    # Save uploaded file
    uploaded_file = request.files['file']
    action = request.form.get('action')

    # Save to temp location
    temp_input = f"/tmp/{uploaded_file.filename}"
    uploaded_file.save(temp_input)

    # Determine output path
    output_ext = '.pdf' if 'pdf' in action else '.docx'
    temp_output = f"/tmp/output_{uuid.uuid4()}{output_ext}"

    # Create specific request for orchestrator
    orchestrator_request = f"""Convert the {get_file_type(temp_input)} document at {temp_input}
    to PDF and save it as {temp_output}"""

    # Process with orchestrator
    orchestrator = HybridOrchestrator()
    result = await orchestrator.process_request(orchestrator_request)

    # Return the converted file
    return send_file(temp_output, as_attachment=True)
```

## Quick Fix for Your Landing Page

You need to update your landing page to handle file uploads properly. Here's what needs to change:

### Option 1: Add File Upload to Request

Update your frontend form to include file upload:

```html
<form id="orchestratorForm" enctype="multipart/form-data">
  <input type="text" name="request" placeholder="What do you want to do?">
  <input type="file" name="file" id="fileInput">
  <button type="submit">Process</button>
</form>
```

### Option 2: Use Direct Tool Endpoints

Instead of using the orchestrator for file conversions, create direct endpoints:

```python
# In app.py or routes.py
@app.route('/api/tools/convert-to-pdf', methods=['POST'])
async def convert_to_pdf_endpoint():
    """Direct endpoint for file conversion"""
    uploaded_file = request.files['file']

    # Determine file type
    ext = uploaded_file.filename.split('.')[-1].lower()

    # Save temp file
    temp_input = f"/tmp/input_{uuid.uuid4()}.{ext}"
    temp_output = f"/tmp/output_{uuid.uuid4()}.pdf"
    uploaded_file.save(temp_input)

    # Call appropriate tool
    if ext in ['doc', 'docx']:
        from tools.word_to_pdf_direct import word_to_pdf_direct
        result = word_to_pdf_direct(temp_input, temp_output)
    elif ext in ['xls', 'xlsx']:
        from tools.pdf_utilities import convert_to_pdf
        result = convert_to_pdf(temp_input, temp_output)
    # ... more file types

    if result.get('success'):
        return send_file(temp_output, as_attachment=True)
    else:
        return jsonify({'error': result.get('error')}), 400
```

## Testing Document Tools Directly

You can test the tools work without the orchestrator:

### Test Word to PDF
```python
from tools.word_to_pdf_direct import word_to_pdf_direct

result = word_to_pdf_direct(
    input_file="test.docx",
    output_file="test.pdf"
)

print(result)
# {'success': True, 'output_file': 'test.pdf', ...}
```

### Test PDF Tools
```python
from tools.pdf_utilities import merge_pdfs, extract_text_from_pdf

# Merge PDFs
result = merge_pdfs(
    input_files=["file1.pdf", "file2.pdf"],
    output_file="merged.pdf"
)

# Extract text
result = extract_text_from_pdf(
    pdf_file="document.pdf"
)
print(result['text'])
```

### Test OCR
```python
from tools.ocr_effocr import ocr_image_local

result = ocr_image_local(
    image_path="scanned_document.png",
    languages=['en']
)

print(result['text'])
```

## Verification Checklist

After the fix, verify:

- [ ] Run `python test_document_routing.py` - all tests pass
- [ ] Orchestrator routes "convert to PDF" to tools (not AI agents)
- [ ] File upload works in your UI
- [ ] Temporary file storage is set up
- [ ] Direct tool endpoints are available as fallback
- [ ] Error handling for missing files is in place

## Summary

### What Was Fixed
✅ Updated orchestrator to recognize document processing capabilities
✅ Added document tool routing in task decomposition
✅ Created test to verify correct routing

### What Still Needs Work (Your Side)
⚠️ Add file upload handling to landing page UI
⚠️ Implement temporary file storage
⚠️ Pass file paths (not just "this file") to orchestrator
⚠️ Or create direct tool endpoints bypassing orchestrator

### Files Modified
- `backend/hybrid_orchestrator.py` - Updated task decomposition prompt
- `backend/test_document_routing.py` - New test for routing verification
- `backend/ORCHESTRATOR_DOCUMENT_TOOLS_FIX.md` - This guide

---

**Next Steps:**
1. Test the routing fix: `python test_document_routing.py`
2. Update your landing page to handle file uploads
3. Restart production server: `python run_production.py`
4. Test with actual file conversion request
