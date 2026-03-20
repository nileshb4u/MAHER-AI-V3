# File Upload Support for Orchestrator

## Problem Solved

Previously, when users attached files via the UI attachment icon, the orchestrator ignored them and only processed the text prompt. This caused errors like:

```
No such file or directory: 'Convert the input file to a Word document'
```

## Solution

Added a new endpoint `/api/hybrid-orchestrator/process-with-files` that:
1. Accepts file uploads via multipart/form-data
2. Saves files to a temporary directory
3. Passes file paths to the orchestrator
4. Routes to appropriate document processing tools
5. Cleans up temporary files after processing

## Frontend Usage

### Update Your UI to Use the New Endpoint

**Before (text only):**
```javascript
fetch('/api/hybrid-orchestrator/process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ input: userPrompt })
})
```

**After (with file support):**
```javascript
// Create form data
const formData = new FormData();
formData.append('input', userPrompt);

// Add all attached files
const fileInput = document.getElementById('fileInput');
for (const file of fileInput.files) {
  formData.append('files', file);
}

// Send to new endpoint
fetch('/api/hybrid-orchestrator/process-with-files', {
  method: 'POST',
  body: formData  // No Content-Type header needed
})
.then(response => response.json())
.then(result => {
  console.log('Files processed:', result.files_processed);
  console.log('Results:', result.results);
});
```

## Example Usage

### Convert Word to PDF

**User uploads:** `report.docx`
**User types:** "Convert to PDF"

**What happens:**
1. File saved to: `/tmp/maher_orchestrator_xxx/report.docx`
2. Orchestrator receives:
   ```
   Convert to PDF

   Files provided:
   - report.docx (.docx, 15234 bytes) at path: /tmp/maher_orchestrator_xxx/report.docx

   Use the file paths above to process the documents.
   ```
3. Orchestrator routes to `Word to PDF Converter` tool
4. Tool extracts:
   - `input_file`: `/tmp/maher_orchestrator_xxx/report.docx`
   - `output_file`: `/tmp/report_output.pdf`
5. Conversion happens, result returned

### Extract Tables from PDF

**User uploads:** `financial_report.pdf`
**User types:** "Extract all tables"

**What happens:**
1. File saved to temp location
2. Routes to `PDF Table Extractor` tool
3. Extracts tables and returns as JSON/Excel

### OCR Scanned Document

**User uploads:** `scanned_invoice.png`
**User types:** "Extract text using OCR"

**What happens:**
1. Routes to `Local Offline OCR` tool
2. Uses EasyOCR to extract text
3. Returns extracted text

## API Endpoint Details

### POST `/api/hybrid-orchestrator/process-with-files`

**Request Format:** `multipart/form-data`

**Form Fields:**
- `input` (string, required): Text description of what to do
- `files` (file array, required): One or more file attachments

**Response:**
```json
{
  "success": true,
  "request_id": "REQ-20250115-143022",
  "decomposition": { ... },
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
        "resource": "Word to PDF Converter",
        "type": "tool",
        "data": {
          "success": true,
          "output_file": "/tmp/report_output.pdf",
          "pages": 5
        }
      }
    ]
  },
  "files_processed": [
    {
      "filename": "report.docx",
      "path": "/tmp/maher_orchestrator_xxx/report.docx",
      "size": 15234,
      "extension": ".docx"
    }
  ],
  "timestamp": "2025-01-15T14:30:22"
}
```

## Implementation Notes

### File Path Extraction

The orchestrator now extracts file paths using regex:
```python
file_path_pattern = r'at path:\s*([^\s]+)'
file_paths = re.findall(file_path_pattern, description)
```

### Parameter Mapping

For document processing tools, parameters are auto-mapped:
- `input_file` → First uploaded file
- `output_file` → Auto-generated temp path with correct extension
- `pdf_file` → First uploaded file (if PDF operation)
- `image_path` → First uploaded file (if OCR operation)

### Output File Handling

Output files are generated based on the operation:
- Word to PDF: `{filename}_output.pdf`
- PDF to Word: `{filename}_output.docx`
- Extract tables: `{filename}_tables.xlsx`

The output extension is determined by:
1. Parameter name (e.g., `output_file` with "pdf" in description → `.pdf`)
2. Operation type (Word to PDF → `.pdf`)
3. Default to `.pdf` if unclear

### Temporary File Cleanup

Files are automatically cleaned up after processing:
```python
shutil.rmtree(temp_dir)
```

In production, you may want to:
- Keep files for a short period (5-10 minutes)
- Allow users to download output files
- Use a scheduled cleanup task instead of immediate deletion

## Complete Frontend Example

```html
<!-- File upload form -->
<form id="orchestratorForm">
  <textarea name="prompt" placeholder="What do you want to do?"></textarea>
  <input type="file" id="fileInput" name="files" multiple>
  <button type="submit">Process</button>
</form>

<script>
document.getElementById('orchestratorForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const prompt = e.target.prompt.value;
  const fileInput = e.target.files;

  const formData = new FormData();
  formData.append('input', prompt);

  // Add all selected files
  for (const file of fileInput.files) {
    formData.append('files', file);
  }

  try {
    const response = await fetch('/api/hybrid-orchestrator/process-with-files', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();

    if (result.success) {
      console.log('Success!');
      console.log('Files processed:', result.files_processed);
      console.log('Results:', result.results);

      // Show results to user
      displayResults(result);
    } else {
      console.error('Error:', result.error);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
});
</script>
```

## Testing

### Test with cURL

```bash
# Convert Word to PDF
curl -X POST http://localhost:8080/api/hybrid-orchestrator/process-with-files \
  -F "input=Convert to PDF" \
  -F "files=@/path/to/document.docx"

# Extract PDF tables
curl -X POST http://localhost:8080/api/hybrid-orchestrator/process-with-files \
  -F "input=Extract all tables" \
  -F "files=@/path/to/report.pdf"

# OCR scanned document
curl -X POST http://localhost:8080/api/hybrid-orchestrator/process-with-files \
  -F "input=Extract text using OCR" \
  -F "files=@/path/to/scanned.png"
```

### Test with Python

```python
import requests

url = 'http://localhost:8080/api/hybrid-orchestrator/process-with-files'

# Upload and convert
files = {'files': open('document.docx', 'rb')}
data = {'input': 'Convert this Word document to PDF'}

response = requests.post(url, files=files, data=data)
result = response.json()

print(result['files_processed'])
print(result['results'])
```

## Migration Guide

### If you're currently using `/api/hybrid-orchestrator/process`

**Option 1: Use the new endpoint for all requests**
- Update all frontend code to use `/process-with-files`
- Always send as `multipart/form-data`
- Files are optional - works without files too

**Option 2: Use conditionally**
```javascript
function sendToOrchestrator(prompt, files) {
  if (files && files.length > 0) {
    // Use file upload endpoint
    return sendWithFiles(prompt, files);
  } else {
    // Use JSON endpoint
    return sendJSON(prompt);
  }
}
```

## Files Changed

1. **`backend/app.py`** - Added `/api/hybrid-orchestrator/process-with-files` endpoint
2. **`backend/hybrid_orchestrator.py`** - Enhanced `_extract_parameters()` to handle file paths
3. **`backend/FILE_UPLOAD_SUPPORT.md`** - This documentation

---

**Status:** ✅ Ready to use
**Tested:** Pending frontend integration
**Cleanup:** Automatic temp file cleanup enabled
