#!/usr/bin/env python3
"""
Test that orchestrator correctly routes document processing requests to tools
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from hybrid_orchestrator import HybridOrchestrator


async def test_document_routing():
    """Test various document processing requests"""

    print("=" * 80)
    print("  Testing Orchestrator Document Routing")
    print("=" * 80)

    # Initialize orchestrator
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("\n⚠️  GEMINI_API_KEY not set - decomposition will fail")
        print("   Set it with: export GEMINI_API_KEY='your-key-here'")
        return

    orchestrator = HybridOrchestrator(gemini_api_key=gemini_key)

    # Test cases
    test_cases = [
        {
            "request": "Convert my Word document to PDF",
            "expected_capabilities": ["word_processing", "document_conversion", "pdf_processing"],
            "expected_resource_type": "tool"
        },
        {
            "request": "Merge these three PDF files into one",
            "expected_capabilities": ["pdf_processing", "document_merge"],
            "expected_resource_type": "tool"
        },
        {
            "request": "Extract tables from this PDF file",
            "expected_capabilities": ["pdf_processing", "table_extraction"],
            "expected_resource_type": "tool"
        },
        {
            "request": "Create an Excel spreadsheet with pivot tables",
            "expected_capabilities": ["excel_processing", "pivot_tables"],
            "expected_resource_type": "tool"
        },
        {
            "request": "Use OCR to extract text from this scanned document",
            "expected_capabilities": ["ocr", "text_extraction"],
            "expected_resource_type": "tool"
        },
        {
            "request": "Generate an email draft with attachments",
            "expected_capabilities": ["email_automation", "draft_creation"],
            "expected_resource_type": "tool"
        }
    ]

    results = {
        "total": len(test_cases),
        "correct_routing": 0,
        "incorrect_routing": 0,
        "errors": 0
    }

    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"Test {idx}: {test_case['request']}")
        print(f"{'─' * 80}")

        try:
            # Decompose the task
            decomposition = await orchestrator.decompose_task(test_case['request'])

            subtasks = decomposition.get('subtasks', [])
            print(f"\n✓ Decomposed into {len(subtasks)} subtask(s)")

            # Check each subtask
            all_correct = True
            for i, subtask in enumerate(subtasks, 1):
                resource_type = subtask.get('preferred_resource_type', 'unknown')
                capabilities = subtask.get('required_capabilities', [])

                print(f"\n  Subtask {i}: {subtask.get('description', 'N/A')[:60]}...")
                print(f"    Resource type: {resource_type}")
                print(f"    Capabilities: {', '.join(capabilities)}")

                # Check if it's routing to tools for document operations
                if resource_type != test_case['expected_resource_type']:
                    print(f"    ⚠️  Expected '{test_case['expected_resource_type']}' but got '{resource_type}'")
                    all_correct = False
                else:
                    print(f"    ✓ Correct resource type")

                # Try to match resources
                matched = orchestrator.match_resources(subtask)
                if matched:
                    print(f"    ✓ Matched to: {matched[0].get('name')}")
                    print(f"    Tool type: {matched[0].get('type')}")
                else:
                    print(f"    ✗ No matching resources found!")
                    all_correct = False

            if all_correct:
                results['correct_routing'] += 1
                print(f"\n  ✅ Test {idx} PASSED")
            else:
                results['incorrect_routing'] += 1
                print(f"\n  ⚠️  Test {idx} NEEDS REVIEW")

        except Exception as e:
            results['errors'] += 1
            print(f"\n  ❌ Test {idx} ERROR: {str(e)[:100]}")

    # Summary
    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80)
    print(f"Total tests: {results['total']}")
    print(f"Correct routing: {results['correct_routing']}/{results['total']}")
    print(f"Incorrect routing: {results['incorrect_routing']}")
    print(f"Errors: {results['errors']}")

    if results['correct_routing'] == results['total']:
        print("\n🎉 SUCCESS: All document requests routed correctly to tools!")
    elif results['correct_routing'] >= results['total'] * 0.8:
        print("\n✓ MOSTLY WORKING: Most requests routed correctly (≥80%)")
    else:
        print("\n⚠️  ISSUES: Many requests not routing correctly")

    print("=" * 80)

    return results['correct_routing'] == results['total']


async def test_simple_conversion():
    """Test a simple conversion request"""
    print("\n" + "=" * 80)
    print("  Simple Test: 'Convert file to PDF'")
    print("=" * 80)

    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("\n⚠️  GEMINI_API_KEY not set - skipping test")
        return

    orchestrator = HybridOrchestrator(gemini_api_key=gemini_key)

    # This is what the user tried
    user_request = "convert this file to pdf"

    print(f"\nUser request: '{user_request}'")
    print("\nDecomposing task...")

    try:
        decomposition = await orchestrator.decompose_task(user_request)

        subtasks = decomposition.get('subtasks', [])
        strategy = decomposition.get('execution_strategy', 'sequential')

        print(f"\n✓ Task decomposed:")
        print(f"  Subtasks: {len(subtasks)}")
        print(f"  Strategy: {strategy}")

        for i, subtask in enumerate(subtasks, 1):
            print(f"\n  Subtask {i}:")
            print(f"    Description: {subtask.get('description')}")
            print(f"    Resource type: {subtask.get('preferred_resource_type')}")
            print(f"    Capabilities: {subtask.get('required_capabilities')}")

            # Try to match
            matched = orchestrator.match_resources(subtask)
            if matched:
                print(f"    ✓ Matched to: {matched[0].get('name')}")
                print(f"      Module: {matched[0].get('module_path')}.{matched[0].get('function')}")
            else:
                print(f"    ✗ No match found - will use AI agent as fallback")

        # Check if it's using tools
        using_tools = any(
            subtask.get('preferred_resource_type') == 'tool'
            for subtask in subtasks
        )

        if using_tools:
            print("\n✅ SUCCESS: Request will be routed to document tools!")
        else:
            print("\n⚠️  WARNING: Request will be routed to AI agents instead of tools")
            print("   This means the actual file conversion won't happen")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")


def main():
    """Main entry point"""
    if not os.getenv('GEMINI_API_KEY'):
        print("=" * 80)
        print("  ERROR: GEMINI_API_KEY not found")
        print("=" * 80)
        print("\nThe orchestrator uses Gemini AI for task decomposition.")
        print("Please add GEMINI_API_KEY to your .env file:")
        print("\n  1. Edit backend/.env")
        print("  2. Add: GEMINI_API_KEY='your-api-key-here'")
        print("  3. Save and run this test again")
        print("\nOr set it temporarily:")
        print("  export GEMINI_API_KEY='your-api-key-here'")
        print("=" * 80)
        sys.exit(1)

    # Run tests
    asyncio.run(test_simple_conversion())
    asyncio.run(test_document_routing())


if __name__ == "__main__":
    main()
