#!/usr/bin/env python3
"""
Test Plan-Execute-Verify (PEV) Orchestrator
Demonstrates hallucination prevention and verification flow
"""

import os
import sys
from dotenv import load_dotenv
import json

# Load environment
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from pev_orchestrator import PEVOrchestrator


def print_separator(title=""):
    """Print a visual separator"""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()


def print_result(result):
    """Pretty print the orchestrator result"""
    print_separator("RESULT SUMMARY")

    print(f"Success: {result.get('success')}")
    print(f"Request ID: {result.get('request_id')}")
    print(f"Trace ID: {result.get('trace_id')}")

    if result.get('verification'):
        verification = result['verification']
        print_separator("VERIFICATION METRICS")
        print(f"Verified: {verification.get('verified')}")
        print(f"Confidence Score: {verification.get('confidence_score', 0) * 100:.1f}%")
        print(f"Data Completeness: {verification.get('data_completeness', 0) * 100:.1f}%")
        print(f"Relevance Score: {verification.get('relevance_score', 0) * 100:.1f}%")
        print(f"Hallucination Detected: {verification.get('hallucination_detected', False)}")
        print(f"Retry Count: {verification.get('retry_count', 0)}")

    if result.get('execution_summary'):
        summary = result['execution_summary']
        print_separator("EXECUTION SUMMARY")
        print(f"Total Subtasks: {summary.get('total_subtasks')}")
        print(f"Successful: {summary.get('successful')}")
        print(f"Failed: {summary.get('failed')}")
        print(f"Strategy: {summary.get('strategy')}")

    if result.get('thinking_process'):
        print_separator("THINKING PROCESS")
        for idx, step in enumerate(result['thinking_process'], 1):
            print(f"\n{idx}. {step.get('step')} [{step.get('status')}]")
            print(f"   Description: {step.get('description')}")
            if step.get('result'):
                print(f"   Result: {json.dumps(step['result'], indent=6)}")
            if step.get('error'):
                print(f"   Error: {step['error']}")

    print_separator("FINAL ANSWER")
    print(result.get('answer', 'No answer provided'))
    print()


def test_simple_query():
    """Test 1: Simple query that should work with AI agent"""
    print_separator("TEST 1: Simple Query")

    orchestrator = PEVOrchestrator()

    user_input = "What is a centrifugal pump and how does it work?"

    print(f"User Query: {user_input}")

    result = orchestrator.process_request(
        user_input=user_input,
        user_role="Maintenance Engineer"
    )

    print_result(result)


def test_hallucination_prone_query():
    """Test 2: Query that might trigger hallucination without verification"""
    print_separator("TEST 2: Hallucination-Prone Query")

    orchestrator = PEVOrchestrator()

    user_input = "What was the vibration reading on pump P-101 at 3pm yesterday?"

    print(f"User Query: {user_input}")
    print("NOTE: This should trigger verification failure since we don't have real-time data")

    result = orchestrator.process_request(
        user_input=user_input,
        user_role="Operations Manager"
    )

    print_result(result)


def test_multi_step_query():
    """Test 3: Multi-step query requiring task decomposition"""
    print_separator("TEST 3: Multi-Step Query")

    orchestrator = PEVOrchestrator()

    user_input = "Check pump maintenance schedule and tell me which pumps need preventive maintenance this month"

    print(f"User Query: {user_input}")

    result = orchestrator.process_request(
        user_input=user_input,
        user_role="Maintenance Planner"
    )

    print_result(result)


def test_verification_retry():
    """Test 4: Query that should trigger verification retry"""
    print_separator("TEST 4: Verification Retry")

    orchestrator = PEVOrchestrator(max_retries=2)

    user_input = "Analyze the latest incident report and provide safety recommendations"

    print(f"User Query: {user_input}")
    print("NOTE: This may trigger retry if initial data is insufficient")

    result = orchestrator.process_request(
        user_input=user_input,
        user_role="Safety Officer"
    )

    print_result(result)


def main():
    """Run all tests"""
    print_separator("MAHER AI - Plan-Execute-Verify (PEV) Orchestrator Tests")

    print("""
This test suite demonstrates the new Plan-Execute-Verify architecture:

1. Planner (Integration Hub Core)
   - Analyzes user intent
   - Looks up available domain agents
   - Decomposes task into subtasks
   - Enforces constraints

2. Executor (Task Manager)
   - Routes tasks to domain agents
   - Aggregates raw data
   - Passes context between agents

3. Verifier (Quality Control)
   - Compares raw data against original question
   - Detects potential hallucinations
   - Enforces citation requirements
   - Loops back to planner if needed

SUCCESS METRICS:
- Hallucination Rate: < 1%
- Routing Accuracy: % of queries sent to correct agent first try
- Verification Pass Rate: % of queries that pass first verification
""")

    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        print("ERROR: GEMINI_API_KEY not found in environment")
        print("Please set it in your .env file")
        return

    try:
        # Run tests
        test_simple_query()
        test_hallucination_prone_query()
        test_multi_step_query()
        test_verification_retry()

        print_separator("ALL TESTS COMPLETED")
        print("""
Key Observations:
1. Check verification metrics for each query
2. Notice when verification triggers retries
3. Observe hallucination detection in action
4. Review thinking process for transparency
""")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
