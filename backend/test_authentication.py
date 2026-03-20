"""
Test script for User Authentication System

Tests:
1. Guest session creation
2. Admin login (correct password)
3. Admin login (wrong password)
4. Session verification
5. Analytics dashboard (admin only)
6. Agent creation (admin only)
7. Agent creation (guest - should fail)
8. Logout
"""

import requests
import json

BASE_URL = "http://localhost:5000"


def test_guest_session():
    """Test 1: Create guest session"""
    print("\n" + "="*60)
    print("TEST 1: Guest Session Creation")
    print("="*60)
    
    url = f"{BASE_URL}/api/auth/session"
    
    try:
        response = requests.post(url, json={}, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Guest session created!")
            print(f"  Session ID: {data.get('session_id', 'N/A')[:16]}...")
            print(f"  Role: {data.get('role', 'N/A')}")
            return data.get('session_id')
        else:
            print(f"✗ Failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return None


def test_admin_login_correct():
    """Test 2: Admin login with correct password"""
    print("\n" + "="*60)
    print("TEST 2: Admin Login (Correct Password)")
    print("="*60)
    
    url = f"{BASE_URL}/api/auth/login"
    payload = {"password": "maher_admin_2026"}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Admin login successful!")
            print(f"  Session ID: {data.get('session_id', 'N/A')[:16]}...")
            print(f"  Role: {data.get('role', 'N/A')}")
            return data.get('session_id')
        else:
            print(f"✗ Failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return None


def test_admin_login_wrong():
    """Test 3: Admin login with wrong password"""
    print("\n" + "="*60)
    print("TEST 3: Admin Login (Wrong Password)")
    print("="*60)
    
    url = f"{BASE_URL}/api/auth/login"
    payload = {"password": "wrong_password"}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print(f"✓ Correctly rejected wrong password!")
            return True
        else:
            print(f"✗ Unexpected response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False


def test_session_verification(session_id, expected_role):
    """Test 4: Verify session"""
    print("\n" + "="*60)
    print(f"TEST 4: Session Verification ({expected_role})")
    print("="*60)
    
    url = f"{BASE_URL}/api/auth/verify"
    payload = {"session_id": session_id}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Session verified!")
            print(f"  Valid: {data.get('valid', False)}")
            print(f"  Role: {data.get('role', 'N/A')}")
            return data.get('role') == expected_role
        else:
            print(f"✗ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False


def test_analytics_admin(admin_session_id):
    """Test 5: Access analytics dashboard (admin)"""
    print("\n" + "="*60)
    print("TEST 5: Analytics Dashboard (Admin)")
    print("="*60)
    
    url = f"{BASE_URL}/api/admin/analytics"
    headers = {"X-Session-ID": admin_session_id}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Analytics accessed successfully!")
            print(f"  Total Visits: {data.get('total_visits', 0)}")
            print(f"  Total Chats: {data.get('total_chats', 0)}")
            print(f"  Total Agents: {data.get('total_agents', 0)}")
            print(f"  Active Users: {data.get('active_users', 0)}")
            return True
        else:
            print(f"✗ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False


def test_analytics_guest(guest_session_id):
    """Test 6: Access analytics dashboard (guest - should fail)"""
    print("\n" + "="*60)
    print("TEST 6: Analytics Dashboard (Guest - Should Fail)")
    print("="*60)
    
    url = f"{BASE_URL}/api/admin/analytics"
    headers = {"X-Session-ID": guest_session_id}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 403:
            print(f"✓ Correctly blocked guest access!")
            return True
        else:
            print(f"✗ Unexpected response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False


def test_create_agent_admin(admin_session_id):
    """Test 7: Create agent as admin"""
    print("\n" + "="*60)
    print("TEST 7: Create Agent (Admin)")
    print("="*60)
    
    url = f"{BASE_URL}/api/agents"
    headers = {"X-Session-ID": admin_session_id}
    payload = {
        "name": "Test Agent",
        "description": "Test agent for authentication testing",
        "systemPrompt": "You are a test agent.",
        "category": "other",
        "status": "draft"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Agent created successfully!")
            print(f"  Agent ID: {data.get('agent', {}).get('id', 'N/A')}")
            return data.get('agent', {}).get('id')
        else:
            print(f"✗ Failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return None


def test_create_agent_guest(guest_session_id):
    """Test 8: Create agent as guest (should fail)"""
    print("\n" + "="*60)
    print("TEST 8: Create Agent (Guest - Should Fail)")
    print("="*60)
    
    url = f"{BASE_URL}/api/agents"
    headers = {"X-Session-ID": guest_session_id}
    payload = {
        "name": "Test Agent",
        "description": "Test agent",
        "systemPrompt": "Test",
        "category": "other"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 403:
            print(f"✓ Correctly blocked guest from creating agent!")
            return True
        else:
            print(f"✗ Unexpected response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False


def test_logout(session_id):
    """Test 9: Logout"""
    print("\n" + "="*60)
    print("TEST 9: Logout")
    print("="*60)
    
    url = f"{BASE_URL}/api/auth/logout"
    payload = {"session_id": session_id}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✓ Logout successful!")
            return True
        else:
            print(f"✗ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False


def run_all_tests():
    """Run all authentication tests"""
    print("\n" + "="*60)
    print("AUTHENTICATION SYSTEM - TEST SUITE")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    
    results = {}
    
    # Test 1: Guest session
    guest_session = test_guest_session()
    results['guest_session'] = guest_session is not None
    
    # Test 2: Admin login (correct)
    admin_session = test_admin_login_correct()
    results['admin_login_correct'] = admin_session is not None
    
    # Test 3: Admin login (wrong)
    results['admin_login_wrong'] = test_admin_login_wrong()
    
    # Test 4: Session verification
    if admin_session:
        results['session_verify_admin'] = test_session_verification(admin_session, 'admin')
    if guest_session:
        results['session_verify_guest'] = test_session_verification(guest_session, 'guest')
    
    # Test 5: Analytics (admin)
    if admin_session:
        results['analytics_admin'] = test_analytics_admin(admin_session)
    
    # Test 6: Analytics (guest - should fail)
    if guest_session:
        results['analytics_guest_blocked'] = test_analytics_guest(guest_session)
    
    # Test 7: Create agent (admin)
    if admin_session:
        agent_id = test_create_agent_admin(admin_session)
        results['create_agent_admin'] = agent_id is not None
    
    # Test 8: Create agent (guest - should fail)
    if guest_session:
        results['create_agent_guest_blocked'] = test_create_agent_guest(guest_session)
    
    # Test 9: Logout
    if admin_session:
        results['logout'] = test_logout(admin_session)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    print("\nStarting authentication system tests...")
    print("Make sure the backend server is running on http://localhost:5000")
    
    input("\nPress Enter to continue...")
    
    success = run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
