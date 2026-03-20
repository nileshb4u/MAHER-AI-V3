# Universal Document Tools for MAHER

This document provides information about the universal document processing tools integrated into the MAHER orchestrator.

## 📦 Installation

### Core Dependencies (Required)

Install the core dependencies that work on all platforms:

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- **PyPDF2** & **pypdf** - PDF processing
- **python-docx** - Word document handling
- **openpyxl** & **pandas** - Excel processing
- **mammoth** - Word to HTML conversion
- **reportlab** - PDF generation
- **Pillow** - Image processing

### Optional Dependencies

Some features require additional setup:

#### OCR Support (Optional)

For OCR functionality on scanned PDFs, you need:

1. **Tesseract OCR Binary** (platform-specific)
   - **Windows**: Download installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`

2. **pytesseract Python package**
   ```bash
   pip install pytesseract==0.3.10
   ```

**Note**: If OCR is not available, the tools will:
- Still extract text from regular (non-scanned) PDFs
- Return helpful error messages when OCR is requested
- Gracefully degrade functionality

#### Word to PDF Conversion (Optional)

For Word → PDF conversion, you need:

1. **docx2pdf package**
   ```bash
   pip install docx2pdf==0.1.8
   ```

2. **MS Office or LibreOffice** installed on the system

**Alternatives**: If docx2pdf is not available:
- Use `word_to_html` to convert to HTML format
- Use `mammoth` library (already included)
- Export manually from Word/LibreOffice

---

## 🛠️ Available Tools

### PDF Utilities (8 Tools)

| Tool ID | Function | Requires OCR? | Requires docx2pdf? |
|---------|----------|---------------|-------------------|
| `tool_pdf_merge` | Merge PDFs | No | No |
| `tool_pdf_split` | Split PDFs | No | No |
| `tool_pdf_extract_text` | Extract text | Optional | No |
| `tool_pdf_extract_tables` | Extract tables | No | No |
| `tool_pdf_convert` | Convert to PDF | No | Optional (for Word) |
| `tool_pdf_to_word` | PDF to Word | No | No |
| `tool_pdf_info` | Get PDF metadata | No | No |
| `ocr_scanned_pdf` | OCR scanned docs | **Yes** | No |

### Word Utilities (9 Tools)

| Tool ID | Function | Requires docx2pdf? |
|---------|----------|-------------------|
| `tool_word_create` | Create Word docs | No |
| `tool_word_extract_text` | Extract text | No |
| `tool_word_extract_headings` | Extract structure | No |
| `tool_word_extract_tables` | Extract tables | No |
| `tool_word_add_table` | Add tables | No |
| `tool_word_to_pdf` | Convert to PDF | **Yes** |
| `tool_word_to_html` | Convert to HTML | No |
| `tool_word_modify` | Modify documents | No |
| `tool_word_info` | Get metadata | No |

### Excel Utilities (8 Tools)

All Excel tools work without optional dependencies:

- `tool_excel_read` - Read Excel files
- `tool_excel_create` - Create spreadsheets
- `tool_excel_modify` - Modify files
- `tool_excel_pivot` - Create pivot tables
- `tool_excel_chart` - Add charts
- `tool_excel_analyze` - Data analysis
- `tool_excel_to_csv` - Convert to CSV
- `tool_excel_info` - Get metadata

### Email Utilities (5 Tools)

All Email tools work without optional dependencies:

- `tool_email_generate` - Generate drafts
- `tool_email_template` - Use templates
- `tool_email_schedule` - Schedule emails
- `tool_email_parse` - Parse emails
- `tool_email_signature` - Generate signatures

---

## 🚀 Usage Examples

### PDF Operations (No Optional Dependencies Required)

```python
from tools.pdf_utilities import merge_pdfs, extract_text_from_pdf, split_pdf

# Merge PDFs
result = merge_pdfs(
    input_files=['doc1.pdf', 'doc2.pdf'],
    output_file='merged.pdf'
)

# Extract text (works without OCR for regular PDFs)
result = extract_text_from_pdf(
    input_file='document.pdf',
    use_ocr=False  # Set to True only if OCR is available
)

# Split PDF
result = split_pdf(
    input_file='large.pdf',
    output_dir='./pages',
    split_type='pages'  # One file per page
)
```

### Word Operations (No Optional Dependencies Required)

```python
from tools.word_utilities import create_word_document, extract_text_from_word

# Create Word document
result = create_word_document(
    output_file='report.docx',
    title='Maintenance Report',
    content=[
        {"type": "heading", "text": "Executive Summary", "level": 1},
        {"type": "paragraph", "text": "This report covers..."},
        {"type": "table", "data": [
            ["Item", "Status", "Date"],
            ["Pump A", "OK", "2025-11-15"],
            ["Motor B", "Repair", "2025-11-16"]
        ]}
    ]
)

# Extract text
result = extract_text_from_word(
    input_file='document.docx',
    include_formatting=True
)

# Convert to HTML (alternative to PDF)
from tools.word_utilities import word_to_html
result = word_to_html(
    input_file='document.docx',
    output_file='document.html'
)
```

### Excel Operations (Fully Supported)

```python
from tools.excel_utilities import create_excel, read_excel, add_chart_to_excel

# Create Excel file
result = create_excel(
    output_file='maintenance_log.xlsx',
    data=[
        ['Date', 'Equipment', 'Task', 'Duration'],
        ['2025-11-15', 'Pump A', 'Inspection', 2.5],
        ['2025-11-16', 'Motor B', 'Repair', 4.0]
    ],
    headers=['Date', 'Equipment', 'Task', 'Duration'],
    formatting={'header_style': True, 'auto_width': True}
)

# Read Excel with pandas
result = read_excel(
    input_file='data.xlsx',
    sheet_name='Sheet1',
    as_dataframe=True
)

# Add chart
result = add_chart_to_excel(
    input_file='data.xlsx',
    output_file='data_with_chart.xlsx',
    chart_config={
        "type": "bar",
        "sheet": "Sheet1",
        "data_range": "A1:D10",
        "title": "Maintenance Hours by Equipment",
        "position": "F2"
    }
)
```

### Email Operations (Fully Supported)

```python
from tools.email_utilities import create_email_from_template, generate_email_draft

# Use maintenance notification template
result = create_email_from_template(
    template_name="maintenance_notification",
    data={
        "equipment_name": "Centrifugal Pump A",
        "equipment_id": "PUMP-A-001",
        "maintenance_date": "2025-11-20 09:00",
        "duration": "3 hours",
        "technician": "John Smith",
        "tasks": "Bearing replacement and lubrication"
    }
)

# Generate custom email
result = generate_email_draft(
    to=["maintenance@company.com"],
    subject="Urgent: Equipment Failure Alert",
    body="<h2>Alert</h2><p>Equipment requires immediate attention...</p>",
    cc=["supervisor@company.com"],
    format="html",
    priority="high"
)
```

---

## ⚠️ Error Handling

The tools provide clear error messages when optional dependencies are missing:

### OCR Not Available
```python
{
    "success": False,
    "error": "OCR not available - pytesseract and Tesseract OCR binary required",
    "note": "Install pytesseract Python package and Tesseract OCR binary to enable OCR"
}
```

### Word to PDF Not Available
```python
{
    "success": False,
    "error": "Word to PDF conversion not available",
    "note": "Requires docx2pdf package and MS Office/LibreOffice installation. Use word_to_html or pdf_utilities.convert_to_pdf as alternatives."
}
```

---

## 🔍 Testing

Run the integration tests to verify your setup:

```bash
cd backend
python test_document_tools.py
```

This will show which features are available based on your installed dependencies.

---

## 📊 Feature Matrix

| Feature Category | Core Features | Optional Features |
|-----------------|---------------|-------------------|
| **PDF** | Merge, split, extract text/tables, metadata | OCR for scanned docs |
| **Word** | Create, extract, modify, HTML conversion | PDF conversion |
| **Excel** | Full support (all features) | None |
| **Email** | Full support (all features) | None |

---

## 🐛 Troubleshooting

### "textract has invalid metadata" error

**Solution**: Textract has been removed from requirements.txt due to metadata issues. Use the built-in PDF/Word extraction tools instead.

### Windows: Can't install Tesseract OCR

**Workaround**:
1. OCR functionality is optional
2. Most PDFs can be read without OCR
3. If you need OCR, use an alternative service or install Tesseract manually

### Word to PDF not working

**Alternative solutions**:
1. Use `word_to_html()` to convert to HTML
2. Open Word document and export manually
3. Use online conversion services
4. Install LibreOffice (free alternative to MS Office)

---

## 📝 Notes

- **All core document processing features work without optional dependencies**
- **OCR and Word→PDF are the only optional features**
- **Tools gracefully degrade when optional dependencies are missing**
- **Clear error messages guide users to solutions**

For questions or issues, please refer to the main MAHER documentation or contact support.
