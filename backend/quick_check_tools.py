#!/usr/bin/env python3
"""
Quick check to verify orchestrator can access all 35 tools
Simple pass/fail test for daily verification
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


def quick_check():
    """Quick verification that all tools are accessible"""
    print("=" * 60)
    print("  MAHER Orchestrator - Quick Tool Check")
    print("=" * 60)

    # Load registry
    registry_path = os.path.join(os.path.dirname(__file__), 'registry.json')

    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"❌ FAILED: Cannot load registry.json")
        print(f"   Error: {e}")
        return False

    # Count tools
    tools = registry.get('resources', {}).get('tools', [])
    workflows = registry.get('resources', {}).get('workflows', [])
    capability_index = registry.get('capability_index', {})

    total_tools = len(tools)
    total_workflows = len(workflows)
    total_capabilities = len(capability_index)

    print(f"\n📊 Resource Count:")
    print(f"   Tools: {total_tools}")
    print(f"   Workflows: {total_workflows}")
    print(f"   Capabilities: {total_capabilities}")

    # Expected counts
    expected_tools = 35
    expected_workflows = 3

    # Verify counts
    print(f"\n🔍 Verification:")

    tools_ok = total_tools == expected_tools
    print(f"   {'✓' if tools_ok else '✗'} Tools: {total_tools}/{expected_tools}")

    workflows_ok = total_workflows >= expected_workflows
    print(f"   {'✓' if workflows_ok else '✗'} Workflows: {total_workflows}>={expected_workflows}")

    capabilities_ok = total_capabilities > 50
    print(f"   {'✓' if capabilities_ok else '✗'} Capabilities: {total_capabilities}>50")

    # Check key tool categories
    print(f"\n📁 Tool Categories:")

    pdf_tools = [t for t in tools if 'pdf' in t.get('name', '').lower()]
    word_tools = [t for t in tools if 'word' in t.get('name', '').lower()]
    excel_tools = [t for t in tools if 'excel' in t.get('name', '').lower()]
    email_tools = [t for t in tools if 'email' in t.get('name', '').lower()]
    ocr_tools = [t for t in tools if 'ocr' in t.get('name', '').lower()]

    print(f"   PDF tools: {len(pdf_tools)}/7")
    print(f"   Word tools: {len(word_tools)}/8")
    print(f"   Excel tools: {len(excel_tools)}/8")
    print(f"   Email tools: {len(email_tools)}/5")
    print(f"   OCR tools: {len(ocr_tools)}/2")

    # Overall result
    print("\n" + "=" * 60)

    if tools_ok and workflows_ok and capabilities_ok:
        print("✅ SUCCESS: Orchestrator has access to all 35 tools!")
        print("=" * 60)
        return True
    else:
        print("⚠️  WARNING: Tool count mismatch detected")
        print("=" * 60)
        return False


def check_imports():
    """Check if key tool modules can be imported"""
    print("\n🔧 Testing Key Imports:")

    import_tests = [
        ("PDF Tools", "tools.pdf_utilities"),
        ("Word Tools", "tools.word_utilities"),
        ("Excel Tools", "tools.excel_utilities"),
        ("Email Tools", "tools.email_utilities"),
        ("OCR Tools", "tools.ocr_effocr"),
        ("Word to PDF Direct", "tools.word_to_pdf_direct"),
    ]

    all_ok = True
    for name, module_path in import_tests:
        try:
            __import__(module_path)
            print(f"   ✓ {name}")
        except Exception as e:
            print(f"   ✗ {name}: {str(e)[:50]}")
            all_ok = False

    return all_ok


def main():
    """Main entry point"""
    registry_ok = quick_check()
    imports_ok = check_imports()

    print("\n" + "=" * 60)
    if registry_ok and imports_ok:
        print("🎉 ALL CHECKS PASSED")
        print("\nYour orchestrator is ready to use all 35 tools!")
        sys.exit(0)
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("\nRun 'python test_orchestrator_tools.py' for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
