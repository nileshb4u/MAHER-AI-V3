"""
Test script for verifying document tools integration with MAHER orchestrator
"""

import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_tool_imports():
    """Test that all document tools can be imported"""
    print("Testing tool imports...")

    try:
        from tools import pdf_utilities
        print("✓ PDF utilities imported successfully")
    except Exception as e:
        print(f"✗ PDF utilities import failed: {e}")
        return False

    try:
        from tools import word_utilities
        print("✓ Word utilities imported successfully")
    except Exception as e:
        print(f"✗ Word utilities import failed: {e}")
        return False

    try:
        from tools import excel_utilities
        print("✓ Excel utilities imported successfully")
    except Exception as e:
        print(f"✗ Excel utilities import failed: {e}")
        return False

    try:
        from tools import email_utilities
        print("✓ Email utilities imported successfully")
    except Exception as e:
        print(f"✗ Email utilities import failed: {e}")
        return False

    return True


def test_registry():
    """Test that registry.json is valid and contains new tools"""
    print("\nTesting registry.json...")

    try:
        with open('registry.json', 'r') as f:
            registry = json.load(f)
        print("✓ Registry JSON is valid")
    except Exception as e:
        print(f"✗ Registry JSON invalid: {e}")
        return False

    # Check for new tool categories
    tools = registry.get('resources', {}).get('tools', [])
    tool_ids = [tool['id'] for tool in tools]

    # Check for PDF tools
    pdf_tools = [t for t in tool_ids if 'pdf' in t]
    if len(pdf_tools) >= 5:
        print(f"✓ Found {len(pdf_tools)} PDF tools")
    else:
        print(f"✗ Expected at least 5 PDF tools, found {len(pdf_tools)}")
        return False

    # Check for Word tools
    word_tools = [t for t in tool_ids if 'word' in t]
    if len(word_tools) >= 5:
        print(f"✓ Found {len(word_tools)} Word tools")
    else:
        print(f"✗ Expected at least 5 Word tools, found {len(word_tools)}")
        return False

    # Check for Excel tools
    excel_tools = [t for t in tool_ids if 'excel' in t]
    if len(excel_tools) >= 5:
        print(f"✓ Found {len(excel_tools)} Excel tools")
    else:
        print(f"✗ Expected at least 5 Excel tools, found {len(excel_tools)}")
        return False

    # Check for Email tools
    email_tools = [t for t in tool_ids if 'email' in t]
    if len(email_tools) >= 3:
        print(f"✓ Found {len(email_tools)} Email tools")
    else:
        print(f"✗ Expected at least 3 Email tools, found {len(email_tools)}")
        return False

    # Check capability index
    capability_index = registry.get('capability_index', {})

    required_capabilities = [
        'pdf_processing',
        'word_processing',
        'excel_processing',
        'email_automation'
    ]

    for cap in required_capabilities:
        if cap in capability_index:
            print(f"✓ Capability '{cap}' registered")
        else:
            print(f"✗ Capability '{cap}' missing")
            return False

    return True


def test_tool_functions():
    """Test that tool functions can be called"""
    print("\nTesting tool function availability...")

    # Test PDF utilities
    try:
        from tools.pdf_utilities import get_pdf_info, merge_pdfs
        print("✓ PDF utility functions accessible")
    except Exception as e:
        print(f"✗ PDF utility functions not accessible: {e}")
        return False

    # Test Word utilities
    try:
        from tools.word_utilities import create_word_document, extract_text_from_word
        print("✓ Word utility functions accessible")
    except Exception as e:
        print(f"✗ Word utility functions not accessible: {e}")
        return False

    # Test Excel utilities
    try:
        from tools.excel_utilities import read_excel, create_excel
        print("✓ Excel utility functions accessible")
    except Exception as e:
        print(f"✗ Excel utility functions not accessible: {e}")
        return False

    # Test Email utilities
    try:
        from tools.email_utilities import generate_email_draft, create_email_from_template
        print("✓ Email utility functions accessible")
    except Exception as e:
        print(f"✗ Email utility functions not accessible: {e}")
        return False

    return True


def test_email_template():
    """Test email template generation"""
    print("\nTesting email template generation...")

    try:
        from tools.email_utilities import create_email_from_template

        # Test with maintenance notification template
        result = create_email_from_template(
            template_name="maintenance_notification",
            data={
                "equipment_name": "Test Pump",
                "equipment_id": "PUMP-001",
                "maintenance_date": "2025-11-20",
                "duration": "2 hours",
                "technician": "John Doe",
                "tasks": "Lubrication and inspection"
            }
        )

        if result.get("success"):
            print("✓ Email template generation works")
            print(f"  Subject: {result.get('subject', 'N/A')[:50]}...")
            return True
        else:
            print(f"✗ Email template generation failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"✗ Email template test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MAHER Document Tools Integration Test")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Tool Imports", test_tool_imports()))
    results.append(("Registry Validation", test_registry()))
    results.append(("Function Availability", test_tool_functions()))
    results.append(("Email Template", test_email_template()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<40} {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print("=" * 60)
    print(f"Total: {total_passed}/{total_tests} tests passed")
    print("=" * 60)

    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
