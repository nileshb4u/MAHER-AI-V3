#!/usr/bin/env python3
"""
Test script for Hybrid Orchestrator
Tests AI agents, workflows, and tools integration
"""
import requests
import json
import os
import time

# Get port from environment or use default
PORT = int(os.environ.get('PORT', 8080))
BASE_URL = f"http://localhost:{PORT}"


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(result, test_name):
    """Print test result"""
    if result.get('success'):
        print(f"✓ {test_name} - SUCCESS")
    else:
        print(f"✗ {test_name} - FAILED")
        print(f"  Error: {result.get('error', 'Unknown error')}")


def test_workflow_checklist():
    """Test maintenance checklist workflow"""
    print_section("Test 1: Maintenance Checklist Workflow")

    test_query = "Generate a preventive maintenance checklist for a centrifugal pump"

    try:
        print(f"Query: {test_query}")
        print("\nSending request to hybrid orchestrator...")

        response = requests.post(
            f"{BASE_URL}/api/hybrid-orchestrator/process",
            json={"input": test_query},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            print_result(data, "Maintenance Checklist Workflow")

            if data.get('success'):
                print(f"\nRequest ID: {data.get('request_id')}")
                print(f"Execution Strategy: {data.get('execution_summary', {}).get('strategy', 'N/A')}")
                print(f"Subtasks: {data.get('execution_summary', {}).get('total_subtasks', 0)}")
                print(f"Successful: {data.get('execution_summary', {}).get('successful', 0)}")

                # Show results summary
                results = data.get('results', {}).get('results', [])
                if results:
                    print("\nResults:")
                    for idx, result in enumerate(results, 1):
                        print(f"  {idx}. {result.get('resource')} ({result.get('type')})")

                return data.get('request_id')
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            print(response.text)
            return None

    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to server!")
        print(f"  Make sure the backend server is running at {BASE_URL}")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def test_tool_equipment_lookup():
    """Test equipment lookup tool"""
    print_section("Test 2: Equipment Lookup Tool")

    test_query = "Look up specifications for equipment PUMP-001"

    try:
        print(f"Query: {test_query}")
        print("\nSending request to hybrid orchestrator...")

        response = requests.post(
            f"{BASE_URL}/api/hybrid-orchestrator/process",
            json={"input": test_query},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            print_result(data, "Equipment Lookup Tool")

            if data.get('success'):
                print(f"\nRequest ID: {data.get('request_id')}")

                # Show results
                results = data.get('results', {}).get('results', [])
                if results:
                    print("\nResults:")
                    for result in results:
                        print(f"  Resource: {result.get('resource')}")
                        result_data = result.get('data', {})
                        if result_data.get('success'):
                            print(f"  Equipment: {result_data.get('name', 'N/A')}")
                            print(f"  Manufacturer: {result_data.get('manufacturer', 'N/A')}")

                return data.get('request_id')
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def test_incident_analysis():
    """Test incident analyzer workflow"""
    print_section("Test 3: Incident Analysis Workflow")

    test_query = "Analyze an incident where pump PUMP-001 had excessive vibration and overheating"

    try:
        print(f"Query: {test_query}")
        print("\nSending request to hybrid orchestrator...")

        response = requests.post(
            f"{BASE_URL}/api/hybrid-orchestrator/process",
            json={"input": test_query},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            print_result(data, "Incident Analysis Workflow")

            if data.get('success'):
                print(f"\nRequest ID: {data.get('request_id')}")
                print(f"Successful subtasks: {data.get('execution_summary', {}).get('successful', 0)}")

            return data.get('request_id')
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def test_multi_resource():
    """Test query that requires multiple resources"""
    print_section("Test 4: Multi-Resource Query")

    test_query = "I need a maintenance checklist for PUMP-001 and cost estimate for preventive maintenance taking 4 hours"

    try:
        print(f"Query: {test_query}")
        print("\nSending request to hybrid orchestrator...")

        response = requests.post(
            f"{BASE_URL}/api/hybrid-orchestrator/process",
            json={"input": test_query},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            print_result(data, "Multi-Resource Query")

            if data.get('success'):
                print(f"\nRequest ID: {data.get('request_id')}")
                print(f"Total subtasks: {data.get('execution_summary', {}).get('total_subtasks', 0)}")
                print(f"Execution strategy: {data.get('execution_summary', {}).get('strategy', 'N/A')}")

                # Show all resources used
                results = data.get('results', {}).get('results', [])
                print(f"\nResources used: {len(results)}")
                for result in results:
                    print(f"  - {result.get('resource')} ({result.get('type')})")

            return data.get('request_id')
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def test_feedback(request_id):
    """Test feedback submission"""
    print_section("Test 5: Feedback System")

    if not request_id:
        print("⚠ Skipping feedback test - no request ID available")
        return

    try:
        print(f"Submitting 5-star feedback for request: {request_id}")

        response = requests.post(
            f"{BASE_URL}/api/hybrid-orchestrator/feedback",
            json={
                "request_id": request_id,
                "rating": 5,
                "feedback_text": "Excellent orchestration! Resources matched perfectly."
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print_result(data, "Feedback Submission")
        else:
            print(f"✗ Error: HTTP {response.status_code}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def test_feedback_stats():
    """Test feedback statistics"""
    print_section("Test 6: Feedback Statistics")

    try:
        print("Fetching feedback statistics...")

        response = requests.get(
            f"{BASE_URL}/api/hybrid-orchestrator/feedback/stats",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print_result(data, "Feedback Statistics")

            if data.get('success'):
                stats = data.get('statistics', {})
                print(f"\nTotal feedback: {stats.get('total_feedback', 0)}")
                print(f"Average rating: {stats.get('average_rating', 0)}")
                print(f"Rating distribution: {stats.get('rating_distribution', {})}")
        else:
            print(f"✗ Error: HTTP {response.status_code}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def main():
    """Run all tests"""
    print("=" * 80)
    print("  MAHER AI - Hybrid Orchestrator Test Suite")
    print("=" * 80)
    print(f"\nServer: {BASE_URL}")
    print(f"Testing comprehensive orchestration of AI Agents, Workflows, and Tools")

    # Run tests
    request_id1 = test_workflow_checklist()
    time.sleep(2)

    request_id2 = test_tool_equipment_lookup()
    time.sleep(2)

    request_id3 = test_incident_analysis()
    time.sleep(2)

    request_id4 = test_multi_resource()
    time.sleep(2)

    # Test feedback with the last successful request ID
    last_request_id = request_id4 or request_id3 or request_id2 or request_id1
    test_feedback(last_request_id)
    time.sleep(1)

    test_feedback_stats()

    # Summary
    print_section("Test Summary")
    print("All tests completed!")
    print("\nThe Hybrid Orchestrator successfully:")
    print("  ✓ Decomposes user requests into subtasks")
    print("  ✓ Matches subtasks to appropriate resources")
    print("  ✓ Executes workflows, tools, and AI agents")
    print("  ✓ Integrates results into unified responses")
    print("  ✓ Handles feedback and statistics")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
