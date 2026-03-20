"""
One-time migration: adds tool_schema + status:"published" to every registry.json
entry that doesn't already have them.

Run once:   python migrate_registry_schemas.py
Safe to re-run — existing tool_schema entries are not overwritten.
"""

import json
import os
import copy

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "registry.json")

# ── Schema definitions for every tool/workflow in the registry ──────────────
# Key = registry entry id, value = OpenAI tool schema dict

SCHEMAS = {
    # ── Workflows ────────────────────────────────────────────────────────────
    "workflow_equipment_scheduler": {
        "type": "function",
        "function": {
            "name": "create_equipment_maintenance_schedule",
            "description": "Creates a time-based maintenance schedule for a list of equipment, ranked by criticality and operational requirements. Returns a prioritized schedule with recommended dates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "equipment_list": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of equipment tag IDs to schedule (e.g. ['P-101','C-201','HE-305'])"
                    },
                    "time_horizon_days": {
                        "type": "integer",
                        "description": "Number of days to plan ahead (e.g. 30, 90, 365)"
                    }
                },
                "required": ["equipment_list", "time_horizon_days"]
            }
        }
    },

    # ── Tools: PDF ────────────────────────────────────────────────────────────
    "tool_parts_inventory": {
        "type": "function",
        "function": {
            "name": "check_parts_inventory",
            "description": "Checks real-time stock availability for one or more spare parts by their part numbers. Returns current stock levels and warehouse locations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "part_numbers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of part/material numbers to check (e.g. ['SAP-123456', '7890-SEAL'])"
                    }
                },
                "required": ["part_numbers"]
            }
        }
    },
    "tool_pdf_merge": {
        "type": "function",
        "function": {
            "name": "merge_pdf_files",
            "description": "Merges two or more PDF files into a single document. Use when the user wants to combine PDFs, append one PDF to another, or consolidate multiple reports into one file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Ordered list of absolute file paths to merge"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Absolute path for the merged output PDF"
                    }
                },
                "required": ["input_files", "output_file"]
            }
        }
    },
    "tool_pdf_split": {
        "type": "function",
        "function": {
            "name": "split_pdf_file",
            "description": "Splits a PDF into separate files by page ranges or by individual pages. Use when the user wants to extract specific pages or chapters from a PDF.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the source PDF"},
                    "output_dir": {"type": "string", "description": "Directory where split files will be saved"},
                    "split_type": {
                        "type": "string",
                        "enum": ["by_page", "by_range", "every_n_pages"],
                        "description": "How to split the PDF"
                    },
                    "split_value": {
                        "type": "integer",
                        "description": "Page number, range end, or N for every_n_pages"
                    }
                },
                "required": ["input_file", "output_dir", "split_type"]
            }
        }
    },
    "tool_pdf_extract_text": {
        "type": "function",
        "function": {
            "name": "extract_text_from_pdf",
            "description": "Extracts readable text from a PDF document. Supports optional OCR for scanned or image-based PDFs. Use when the user wants to read, search, or process the text content of a PDF.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the PDF file"},
                    "page_numbers": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Specific page numbers to extract (1-indexed). Leave empty for all pages."
                    },
                    "use_ocr": {
                        "type": "boolean",
                        "description": "Set true for scanned/image PDFs that contain no selectable text (default: false)"
                    }
                },
                "required": ["input_file"]
            }
        }
    },
    "tool_pdf_extract_tables": {
        "type": "function",
        "function": {
            "name": "extract_tables_from_pdf",
            "description": "Extracts all tables from a PDF and returns them as structured data. Use when the user wants to get tabular data (equipment lists, maintenance records, cost tables) from a PDF.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the PDF"},
                    "page_numbers": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Page numbers to search for tables. Leave empty for all pages."
                    }
                },
                "required": ["input_file"]
            }
        }
    },
    "tool_pdf_convert": {
        "type": "function",
        "function": {
            "name": "convert_to_pdf",
            "description": "Converts an image, Word document, or text file to PDF format. Use when the user wants to create a PDF from another file type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the source file"},
                    "output_file": {"type": "string", "description": "Absolute path for the output PDF"},
                    "source_type": {
                        "type": "string",
                        "enum": ["image", "word", "text"],
                        "description": "Type of source file"
                    }
                },
                "required": ["input_file", "output_file", "source_type"]
            }
        }
    },
    "tool_pdf_to_word": {
        "type": "function",
        "function": {
            "name": "convert_pdf_to_word",
            "description": "Converts a PDF document to an editable Word (.docx) file. Use when the user needs to edit a PDF or extract its content into Word format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the source PDF"},
                    "output_file": {"type": "string", "description": "Absolute path for the output .docx file"}
                },
                "required": ["input_file", "output_file"]
            }
        }
    },
    "tool_pdf_info": {
        "type": "function",
        "function": {
            "name": "get_pdf_info",
            "description": "Returns metadata about a PDF file: page count, title, author, creation date, file size, and whether it is encrypted or scanned.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the PDF file"}
                },
                "required": ["input_file"]
            }
        }
    },

    # ── Tools: OCR ────────────────────────────────────────────────────────────
    "tool_ocr_local": {
        "type": "function",
        "function": {
            "name": "ocr_image",
            "description": "Extracts text from an image file using offline EasyOCR. Supports 80+ languages including Arabic and English. No internet required. Use when the user uploads a photo, screenshot, or scanned image and wants the text extracted.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Absolute path to the image file (jpg, png, tiff, bmp)"},
                    "engine": {
                        "type": "string",
                        "enum": ["easyocr", "tesseract"],
                        "description": "OCR engine to use (default: easyocr)"
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Language codes to detect (e.g. ['en', 'ar']). Default: ['en']"
                    }
                },
                "required": ["image_path"]
            }
        }
    },
    "tool_ocr_pdf_local": {
        "type": "function",
        "function": {
            "name": "ocr_pdf",
            "description": "Performs OCR on a scanned PDF using offline local models (no internet). Extracts text page by page. Use for scanned maintenance manuals, permits, or inspection reports.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pdf_path": {"type": "string", "description": "Absolute path to the scanned PDF"},
                    "output_format": {
                        "type": "string",
                        "enum": ["text", "json", "searchable_pdf"],
                        "description": "Format for the extracted content (default: text)"
                    },
                    "engine": {
                        "type": "string",
                        "enum": ["easyocr", "tesseract"],
                        "description": "OCR engine (default: easyocr)"
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Language codes (default: ['en'])"
                    }
                },
                "required": ["pdf_path"]
            }
        }
    },

    # ── Tools: Word ───────────────────────────────────────────────────────────
    "tool_word_create": {
        "type": "function",
        "function": {
            "name": "create_word_document",
            "description": "Creates a formatted Word (.docx) document with headings, paragraphs, tables, and lists. Use when the user wants to generate a report, procedure, checklist, or any structured document in Word format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "output_file": {"type": "string", "description": "Absolute path for the output .docx file"},
                    "title": {"type": "string", "description": "Document title"},
                    "content": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of content blocks: [{type:'heading',level:1,text:'...'}, {type:'paragraph',text:'...'}, {type:'table',data:[[...]]}]"
                    }
                },
                "required": ["output_file", "title", "content"]
            }
        }
    },
    "tool_word_extract_text": {
        "type": "function",
        "function": {
            "name": "extract_text_from_word",
            "description": "Extracts all text content from a Word (.docx) document. Use when the user uploads a Word file and asks about its content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .docx file"},
                    "include_formatting": {
                        "type": "boolean",
                        "description": "Whether to include heading levels and formatting hints (default: false)"
                    }
                },
                "required": ["input_file"]
            }
        }
    },
    "tool_word_extract_headings": {
        "type": "function",
        "function": {
            "name": "extract_word_headings",
            "description": "Extracts the heading structure (table of contents) from a Word document. Use to understand document organization or navigate to specific sections.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .docx file"}
                },
                "required": ["input_file"]
            }
        }
    },
    "tool_word_extract_tables": {
        "type": "function",
        "function": {
            "name": "extract_tables_from_word",
            "description": "Extracts all tables from a Word document as structured data. Use when the user needs tabular data from a Word report or form.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .docx file"}
                },
                "required": ["input_file"]
            }
        }
    },
    "tool_word_to_pdf": {
        "type": "function",
        "function": {
            "name": "convert_word_to_pdf",
            "description": "Converts a Word (.docx) document to PDF format. Use when the user wants to share or print a Word document as PDF.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .docx source file"},
                    "output_file": {"type": "string", "description": "Absolute path for the output PDF"}
                },
                "required": ["input_file", "output_file"]
            }
        }
    },
    "tool_word_to_html": {
        "type": "function",
        "function": {
            "name": "convert_word_to_html",
            "description": "Converts a Word (.docx) document to HTML format for web publishing or email embedding.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .docx source file"},
                    "output_file": {"type": "string", "description": "Absolute path for the output .html file"}
                },
                "required": ["input_file", "output_file"]
            }
        }
    },
    "tool_word_add_table": {
        "type": "function",
        "function": {
            "name": "add_table_to_word",
            "description": "Adds a formatted table to an existing Word document. Use when the user wants to insert data tables, equipment lists, or cost breakdowns into a Word file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the existing .docx file"},
                    "output_file": {"type": "string", "description": "Absolute path for the modified output"},
                    "table_data": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "string"}},
                        "description": "2D array of cell values (first row = headers)"
                    },
                    "position": {
                        "type": "string",
                        "enum": ["end", "after_heading"],
                        "description": "Where to insert the table (default: end)"
                    },
                    "style": {"type": "string", "description": "Word table style name (default: 'Table Grid')"}
                },
                "required": ["input_file", "output_file", "table_data"]
            }
        }
    },
    "tool_word_info": {
        "type": "function",
        "function": {
            "name": "get_word_document_info",
            "description": "Returns metadata about a Word document: page count, word count, author, creation date, last modified.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .docx file"}
                },
                "required": ["input_file"]
            }
        }
    },

    # ── Tools: Excel ──────────────────────────────────────────────────────────
    "tool_excel_read": {
        "type": "function",
        "function": {
            "name": "read_excel_data",
            "description": "Reads data from an Excel file. Supports selecting a specific sheet and cell range. Returns the data as a structured list. Use when the user uploads an Excel file and asks about its data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .xlsx/.xls file"},
                    "sheet_name": {"type": "string", "description": "Sheet name to read (default: first sheet)"},
                    "cell_range": {"type": "string", "description": "Excel range notation e.g. 'A1:D20' (default: all data)"},
                    "as_dataframe": {"type": "boolean", "description": "Return as structured JSON table (default: true)"}
                },
                "required": ["input_file"]
            }
        }
    },
    "tool_excel_create": {
        "type": "function",
        "function": {
            "name": "create_excel_file",
            "description": "Creates a new Excel file with formatted data, headers, and optional multiple sheets. Use when the user wants to generate a spreadsheet, report, or data export in Excel format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "output_file": {"type": "string", "description": "Absolute path for the output .xlsx file"},
                    "data": {
                        "type": "object",
                        "description": "Dict of sheet_name → list of row dicts e.g. {'Sheet1': [{'col1':'val1',...}]}"
                    },
                    "headers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Column headers for the first sheet"
                    },
                    "sheet_name": {"type": "string", "description": "Name for the first sheet (default: 'Sheet1')"}
                },
                "required": ["output_file", "data"]
            }
        }
    },
    "tool_excel_modify": {
        "type": "function",
        "function": {
            "name": "modify_excel_file",
            "description": "Modifies an existing Excel file: updates cell values, adds/removes rows. Use when the user wants to update an existing spreadsheet with new data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the source .xlsx file"},
                    "output_file": {"type": "string", "description": "Absolute path for the modified output"},
                    "modifications": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of changes: [{action:'set_cell', sheet:'Sheet1', row:2, col:3, value:'new_value'}]"
                    }
                },
                "required": ["input_file", "output_file", "modifications"]
            }
        }
    },
    "tool_excel_pivot": {
        "type": "function",
        "function": {
            "name": "create_excel_pivot_table",
            "description": "Creates a pivot table from Excel data for analysis. Use when the user wants to summarize, group, or aggregate data in a spreadsheet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the source .xlsx file"},
                    "output_file": {"type": "string", "description": "Absolute path for the output with pivot table"},
                    "sheet_name": {"type": "string", "description": "Source sheet name"},
                    "pivot_config": {
                        "type": "object",
                        "description": "Pivot configuration: {index:'col_name', columns:'col_name', values:'col_name', aggfunc:'sum|mean|count'}"
                    }
                },
                "required": ["input_file", "output_file", "pivot_config"]
            }
        }
    },
    "tool_excel_chart": {
        "type": "function",
        "function": {
            "name": "add_chart_to_excel",
            "description": "Adds a chart (bar, line, or pie) to an Excel file. Use when the user wants to visualize Excel data with a chart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .xlsx file"},
                    "output_file": {"type": "string", "description": "Absolute path for the output with chart"},
                    "chart_config": {
                        "type": "object",
                        "description": "Chart config: {type:'bar|line|pie', title:'...', sheet:'Sheet1', data_range:'A1:B10'}"
                    }
                },
                "required": ["input_file", "output_file", "chart_config"]
            }
        }
    },
    "tool_excel_analyze": {
        "type": "function",
        "function": {
            "name": "analyze_excel_data",
            "description": "Performs statistical analysis on Excel data: mean, median, min, max, standard deviation, correlation. Use when the user wants statistical insights from a spreadsheet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .xlsx file"},
                    "sheet_name": {"type": "string", "description": "Sheet to analyze (default: first sheet)"},
                    "analysis_type": {
                        "type": "string",
                        "enum": ["summary", "correlation", "distribution", "trend"],
                        "description": "Type of statistical analysis to perform"
                    }
                },
                "required": ["input_file", "analysis_type"]
            }
        }
    },
    "tool_excel_to_csv": {
        "type": "function",
        "function": {
            "name": "convert_excel_to_csv",
            "description": "Exports an Excel sheet to CSV format. Use when the user needs to export data for use in another system or analysis tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .xlsx file"},
                    "output_file": {"type": "string", "description": "Absolute path for the output .csv file"},
                    "sheet_name": {"type": "string", "description": "Sheet to export (default: first sheet)"}
                },
                "required": ["input_file", "output_file"]
            }
        }
    },
    "tool_excel_info": {
        "type": "function",
        "function": {
            "name": "get_excel_info",
            "description": "Returns metadata about an Excel file: sheet names, row/column counts, data types per column, and file size.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .xlsx file"}
                },
                "required": ["input_file"]
            }
        }
    },
    "tool_excel_to_pdf": {
        "type": "function",
        "function": {
            "name": "convert_excel_to_pdf",
            "description": "Converts an Excel spreadsheet to PDF with formatted tables. Use when the user wants to share a spreadsheet as a non-editable PDF report.",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Absolute path to the .xlsx file"},
                    "output_file": {"type": "string", "description": "Absolute path for the output PDF"},
                    "sheet_name": {"type": "string", "description": "Sheet to convert (default: first sheet)"},
                    "include_all_sheets": {
                        "type": "boolean",
                        "description": "Convert all sheets to a single PDF (default: false)"
                    }
                },
                "required": ["input_file", "output_file"]
            }
        }
    },

    # ── Tools: Email ──────────────────────────────────────────────────────────
    "tool_email_generate": {
        "type": "function",
        "function": {
            "name": "generate_email_draft",
            "description": "Generates a professional Outlook-compatible email draft with proper formatting. Use when the user asks to write, compose, or draft an email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address(es) comma-separated"},
                    "subject": {"type": "string", "description": "Email subject line"},
                    "body": {"type": "string", "description": "Full email body text (can include markdown formatting)"},
                    "cc": {"type": "string", "description": "CC recipients (optional)"},
                    "priority": {
                        "type": "string",
                        "enum": ["normal", "high", "low"],
                        "description": "Email priority (default: normal)"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        }
    },
    "tool_email_template": {
        "type": "function",
        "function": {
            "name": "create_email_from_template",
            "description": "Creates an email from a predefined maintenance notification template with auto-filled data. Use for work order notifications, maintenance alerts, or equipment downtime notices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "enum": ["work_order", "maintenance_alert", "equipment_downtime", "inspection_due", "safety_notice"],
                        "description": "Template to use"
                    },
                    "data": {
                        "type": "object",
                        "description": "Template variables to fill in (depends on template_name)"
                    }
                },
                "required": ["template_name", "data"]
            }
        }
    },
    "tool_email_schedule": {
        "type": "function",
        "function": {
            "name": "schedule_email",
            "description": "Schedules an email to be sent at a future date/time, with optional recurrence. Use when the user wants to set up automated maintenance reminders or recurring notifications.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_draft": {
                        "type": "object",
                        "description": "Email to schedule: {to, subject, body, cc}"
                    },
                    "send_datetime": {
                        "type": "string",
                        "description": "ISO 8601 datetime for sending (e.g. 2025-04-01T08:00:00)"
                    },
                    "recurrence": {
                        "type": "string",
                        "enum": ["none", "daily", "weekly", "monthly"],
                        "description": "Recurrence pattern (default: none)"
                    }
                },
                "required": ["email_draft", "send_datetime"]
            }
        }
    },
    "tool_email_parse": {
        "type": "function",
        "function": {
            "name": "parse_email_content",
            "description": "Parses an incoming email to extract sender, recipients, subject, body text, and attachment metadata. Use when the user pastes an email and wants it processed or summarized.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_content": {
                        "type": "string",
                        "description": "Raw email content or pasted email text"
                    },
                    "parse_attachments": {
                        "type": "boolean",
                        "description": "Whether to list attachment names and sizes (default: true)"
                    }
                },
                "required": ["email_content"]
            }
        }
    },
    "tool_email_signature": {
        "type": "function",
        "function": {
            "name": "generate_email_signature",
            "description": "Generates a professional HTML email signature. Use when the user wants to create or update their email signature.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Full name"},
                    "title": {"type": "string", "description": "Job title"},
                    "company": {"type": "string", "description": "Company or department name"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "email": {"type": "string", "description": "Email address"}
                },
                "required": ["name", "title", "company"]
            }
        }
    },
}


def migrate():
    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    updated = 0
    for category in ("ai_agents", "workflows", "tools"):
        for entry in registry.get("resources", {}).get(category, []):
            eid = entry.get("id", "")

            # Add status if missing
            if "status" not in entry:
                entry["status"] = "published"

            # Add tool_schema if we have one and entry doesn't have it yet
            if eid in SCHEMAS and "tool_schema" not in entry:
                entry["tool_schema"] = SCHEMAS[eid]
                updated += 1

    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

    print(f"Migration complete: {updated} tool_schemas added to registry.json")


if __name__ == "__main__":
    migrate()
