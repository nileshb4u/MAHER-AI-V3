#!/usr/bin/env python3
"""
Quick test script to verify orchestrator is working
"""
import requests
import json
import os

# Get port from environment or use default
PORT = int(os.environ.get('PORT', 8080))
BASE_URL = f"http://localhost:{PORT}"

def test_orchestrator():
    print("=" * 60)
    print("Testing MAHER Orchestrator Agent")
    print("=" * 60)

    # Test query for logistics
    test_query = "I need to plan logistics for transporting equipment"

    print(f"\nSending test query: '{test_query}'")
    print("\nCalling orchestrator endpoint...")

    try:
        response = requests.post(
            f"{BASE_URL}/api/orchestrator/process",
            json={"input": test_query},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print("\n✓ Orchestrator Response Received!")
            print("-" * 60)

            # Check orchestration data
            if 'orchestration' in data:
                orch = data['orchestration']
                print(f"\nStrategy: {orch.get('strategy', 'N/A')}")
                print(f"Agents Used: {len(orch.get('agents_used', []))}")

                for agent in orch.get('agents_used', []):
                    print(f"  - {agent.get('name')} ({agent.get('agent_id')})")

                print(f"\nReasoning: {orch.get('reasoning', 'N/A')[:200]}...")

            # Show response preview
            response_text = data.get('response', '')
            print(f"\nResponse Preview (first 300 chars):")
            print("-" * 60)
            print(response_text[:300] + "...")

            # Check for orchestrator engagement message
            if "🔧 MAHER Orchestrator engaged:" in response_text:
                print("\n✓ SUCCESS: Orchestrator is working correctly!")
                print("  The specialized agents are being engaged.")
            else:
                print("\n⚠ WARNING: Response doesn't show orchestrator engagement")
                print("  This might indicate the agents aren't being selected properly.")

        elif response.status_code == 429:
            print("\n⚠ Rate limit exceeded. Wait a moment and try again.")
        else:
            print(f"\n✗ Error: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to server!")
        print(f"  Make sure the backend server is running at {BASE_URL}")
        print("\n  Start it with:")
        print("    Windows: cd backend && python run_production.py")
        print("    Linux:   cd /home/user/MAHER_NEW_UI/backend && python run_production.py")
        print("\n  Note: Default port is 8080 (set PORT env var to change)")
    except Exception as e:
        print(f"\n✗ Error: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_orchestrator()
