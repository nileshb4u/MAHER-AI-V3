"""
Test script for Conversational Orchestrator with Document Generation

Tests:
1. Orchestrator response includes follow-up questions
2. Orchestrator response includes suggested actions
3. Document generation (PDF, Word, Excel)
4. Document download
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"


def test_orchestrator_with_follow_ups():
    """Test that orchestrator returns follow-up questions and actions"""
    
    print("\n" + "="*60)
    print("TEST 1: Orchestrator with Follow-ups and Actions")
    print("="*60)
    
    url = f"{BASE_URL}/api/orchestrator/process"
    payload = {
        "input": "Create a preventive maintenance checklist for centrifugal pump"
    }
    
    print(f"\nSending request to: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✓ Response received successfully!")
            print(f"\nAgent Response (first 200 chars):")
            print(data.get('response', '')[:200] + "...")
            
            # Check follow-up questions
            follow_ups = data.get('follow_up_questions', [])
            print(f"\n✓ Follow-up Questions ({len(follow_ups)}):")
            for i, question in enumerate(follow_ups, 1):
                print(f"  {i}. {question}")
            
            # Check suggested actions
            actions = data.get('suggested_actions', [])
            print(f"\n✓ Suggested Actions ({len(actions)}):")
            for action in actions:
                print(f"  - {action.get('label', 'N/A')} ({action.get('type', 'N/A')})")
            
            # Return response for document generation test
            return data.get('response', ''), actions
        else:
            print(f"\n✗ Error: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"\n✗ Exception: {str(e)}")
        return None, None


def test_document_generation(content, format="pdf"):
    """Test document generation"""
    
    print("\n" + "="*60)
    print(f"TEST 2: Document Generation ({format.upper()})")
    print("="*60)
    
    url = f"{BASE_URL}/api/documents/generate"
    payload = {
        "content": content,
        "format": format,
        "title": "Maintenance Checklist",
        "metadata": {
            "agent_name": "Maintenance Agent",
            "generated_at": "2026-02-03T22:00:00"
        }
    }
    
    print(f"\nSending request to: {url}")
    print(f"Format: {format}")
    print(f"Content length: {len(content)} characters")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("\n✓ Document generated successfully!")
                print(f"  Filename: {data.get('filename', 'N/A')}")
                print(f"  Download URL: {data.get('download_url', 'N/A')}")
                print(f"  Size: {data.get('size', 0)} bytes")
                
                return data.get('download_url')
            else:
                print(f"\n✗ Generation failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"\n✗ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n✗ Exception: {str(e)}")
        return None


def test_document_download(download_url):
    """Test document download"""
    
    print("\n" + "="*60)
    print("TEST 3: Document Download")
    print("="*60)
    
    if not download_url:
        print("\n✗ No download URL provided")
        return False
    
    url = f"{BASE_URL}{download_url}"
    
    print(f"\nDownloading from: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"\n✓ Document downloaded successfully!")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"  Content-Length: {len(response.content)} bytes")
            return True
        else:
            print(f"\n✗ Download failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ Exception: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    
    print("\n" + "="*60)
    print("CONVERSATIONAL ORCHESTRATOR - TEST SUITE")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Orchestrator with follow-ups
    content, actions = test_orchestrator_with_follow_ups()
    
    if not content:
        print("\n✗ Orchestrator test failed. Stopping tests.")
        return
    
    # Test 2: PDF Generation
    pdf_url = test_document_generation(content, format="pdf")
    
    # Test 3: Word Generation
    word_url = test_document_generation(content, format="word")
    
    # Test 4: Excel Generation (if content has tables)
    excel_url = test_document_generation(content, format="excel")
    
    # Test 5: Download PDF
    if pdf_url:
        test_document_download(pdf_url)
    
    # Test 6: Download Word
    if word_url:
        test_document_download(word_url)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✓ Orchestrator: {'PASS' if content else 'FAIL'}")
    print(f"✓ PDF Generation: {'PASS' if pdf_url else 'FAIL'}")
    print(f"✓ Word Generation: {'PASS' if word_url else 'FAIL'}")
    print(f"✓ Excel Generation: {'PASS' if excel_url else 'FAIL'}")
    print("="*60)


if __name__ == "__main__":
    print("\nStarting tests...")
    print("Make sure the backend server is running on http://localhost:5000")
    
    input("\nPress Enter to continue...")
    
    run_all_tests()
    
    print("\n\nTests completed!")
