# Windows Installation Guide

## ✅ Quick Start (Works on All Windows Systems)

### Step 1: Install Core Dependencies

These packages work perfectly on Windows without any external binaries:

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- Flask & Flask-CORS (API server)
- PyPDF2 & pypdf (PDF processing)
- python-docx (Word documents)
- openpyxl & pandas (Excel files)
- mammoth (Word to HTML)
- reportlab (PDF generation)
- Pillow (Image processing)

### Step 2: Test Installation

```bash
python test_document_tools.py
```

Expected output:
```
✓ Tool Imports............................ PASSED
✓ Registry Validation..................... PASSED
✓ Function Availability................... PASSED
✓ Email Template.......................... PASSED

Total: 4/4 tests passed
```

---

## 🎯 What Works Out of the Box

### ✅ Fully Functional Features

#### PDF Tools (90% functionality)
- ✓ Merge multiple PDFs
- ✓ Split PDFs into separate files
- ✓ Extract text from regular (non-scanned) PDFs
- ✓ Extract tables from PDFs
- ✓ Convert images to PDF
- ✓ Convert text files to PDF
- ✓ PDF to Word conversion
- ✓ Get PDF metadata and info

#### Word Tools (90% functionality)
- ✓ Create Word documents
- ✓ Add formatted content, headings, paragraphs
- ✓ Add tables to Word documents
- ✓ Extract text from Word files
- ✓ Extract headings and structure
- ✓ Extract tables from Word
- ✓ Convert Word to HTML
- ✓ Modify existing Word documents
- ✓ Get Word document metadata

#### Excel Tools (100% functionality)
- ✓ Read Excel files
- ✓ Create new Excel workbooks
- ✓ Modify existing Excel files
- ✓ Create pivot tables
- ✓ Add charts (bar, line, pie)
- ✓ Perform data analysis
- ✓ Convert Excel to CSV
- ✓ Format cells and ranges
- ✓ Get Excel metadata

#### Email Tools (100% functionality)
- ✓ Generate email drafts
- ✓ Use maintenance notification templates
- ✓ Schedule emails
- ✓ Parse incoming emails
- ✓ Generate HTML signatures
- ✓ Create mailto links

---

## ⚠️ Optional Features (Disabled on Restricted Systems)

### OCR for Scanned PDFs
**Status**: Optional - Disabled by default

**Why it's optional**: Requires Tesseract OCR binary (.exe installer)

**Workaround**: Most PDFs can be read without OCR. For scanned documents:
- Use online OCR services
- Pre-process PDFs with OCR before uploading
- Use alternative tools outside MAHER

### Word to PDF Direct Conversion
**Status**: Optional - Disabled by default

**Why it's optional**: Requires MS Office or LibreOffice installation

**Workaround**: Use these alternatives that ARE included:
1. **Word to HTML** (built-in):
   ```python
   from tools.word_utilities import word_to_html
   word_to_html('document.docx', 'document.html')
   ```

2. **Manual export**: Open in Word and save as PDF

3. **Online converters**: Use free online Word to PDF services

---

## 🚀 Running the Backend

### Start the MAHER Backend Server

```bash
cd backend
python app.py
```

Expected output:
```
* Running on http://127.0.0.1:5000
```

### Test the Document Tools API

The backend will automatically load all 30 document tools when it starts.

---

## 📊 Summary of Available Features

| Category | Available Tools | Working Tools | Percentage |
|----------|----------------|---------------|------------|
| PDF | 8 | 7 | 88% |
| Word | 9 | 8 | 89% |
| Excel | 8 | 8 | 100% |
| Email | 5 | 5 | 100% |
| **TOTAL** | **30** | **28** | **93%** |

### Missing Features (Optional)
1. PDF OCR (tool_pdf_extract_text with use_ocr=True)
2. Word to PDF (tool_word_to_pdf)

Both have built-in alternatives and clear error messages.

---

## 🔧 Troubleshooting

### Issue: "textract has invalid metadata"

**Solution**: Already fixed! Textract has been removed from requirements.txt.

### Issue: pip install fails

**Check**:
```bash
python --version  # Should be Python 3.8+
pip --version     # Should be pip 24.0+
```

**Fix**:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Import errors when running tests

**Check Python path**:
```bash
cd backend
python -c "import sys; print(sys.path)"
```

**Reinstall dependencies**:
```bash
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
```

---

## ✨ What You Get

With just the core dependencies, MAHER can:

1. **Process PDFs**: Merge, split, extract text and tables from most PDFs
2. **Create Reports**: Generate Word documents with tables and formatting
3. **Analyze Data**: Read/write Excel, create pivot tables and charts
4. **Automate Emails**: Generate maintenance notifications from templates
5. **Convert Formats**: Word↔HTML, Excel↔CSV, Image→PDF
6. **Extract Information**: Pull text, tables, metadata from documents

All without requiring administrator privileges or external binary installations!

---

## 📞 Need Help?

If you encounter issues:

1. Run the test script: `python test_document_tools.py`
2. Check the error messages (they include helpful suggestions)
3. Review `DOCUMENT_TOOLS_README.md` for detailed documentation
4. Contact support with the test output

---

## 🎉 You're Ready!

The MAHER document tools are now installed and ready to use. 93% of features work without any additional setup!

Try creating your first document:

```python
from tools.excel_utilities import create_excel

result = create_excel(
    output_file='maintenance_log.xlsx',
    data=[
        ['Date', 'Equipment', 'Status'],
        ['2025-11-15', 'Pump A', 'OK'],
        ['2025-11-16', 'Motor B', 'Repair']
    ],
    headers=['Date', 'Equipment', 'Status'],
    formatting={'header_style': True, 'auto_width': True}
)

print(result)  # {'success': True, 'output_file': 'maintenance_log.xlsx', ...}
```

Happy automating! 🚀
