
import logging
import os
import sys

# Add current directory to path so we can import metabrain_client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from metabrain_client import MetaBrainClient
from dotenv import load_dotenv

# Load env from parent directory or current
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Setup console logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test_script")

def test_connection():
    print("----------------------------------------------------------------")
    print("MAHER AI - MetaBrain Connection Test")
    print("----------------------------------------------------------------")
    
    client_id = os.getenv("METABRAIN_CLIENT_ID")
    client_secret = os.getenv("METABRAIN_CLIENT_SECRET")
    
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {'*' * 5 if client_secret else 'NOT SET'}")
    
    if not client_id or not client_secret:
        print("ERROR: Credentials missing in .env file!")
        return

    client = MetaBrainClient()
    
    print("\n1. Testing Authentication...")
    try:
        token = client._get_token()
        print(f"SUCCESS: Token acquired. Length: {len(token)}")
        print(f"Token Sample: {token[:20]}...")
    except Exception as e:
        print(f"FAIL: Auth failed. Error: {e}")
        return

    print("\n2. Testing Chat (Hello)...")
    try:
        response = client.chat("Hello, are you online?")
        if response.get("success"):
            print("SUCCESS: Chat response received.")
            print(f"Answer: {response.get('text')}")
            print(f"Session ID: {response.get('session_id')}")
        else:
            print(f"FAIL: Chat failed. Error: {response.get('error')}")
    except Exception as e:
        print(f"FAIL: Chat exception. Error: {e}")

if __name__ == "__main__":
    test_connection()
