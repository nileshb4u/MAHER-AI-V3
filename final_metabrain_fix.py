
import os

# ==============================================================================
# CORRECT METABRAIN CLIENT CODE
# Includes:
# 1. Dynamic Auth URL (from user's golden script logic)
# 2. CHAT_URL definition
# 3. SSL Verification DISABLED
# 4. MetaBrainResponse helper class (fixes to_gemini_format error)
# 5. Correct payload key "question_body"
# ==============================================================================
FULL_CODE = r'''
import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import urllib3

# Configure logging specific to this client
logger = logging.getLogger("metabrain_client")
logger.setLevel(logging.DEBUG)

# Endpoints - Dynamic to match user environment
# Defaulting to values seen in user logs/script
AUTH_DOMAIN = os.getenv("METABRAIN_AUTH_DOMAIN", "bl-metabrainv2-beyond-search-keycloak-metabrain-dev.apps.d02.aramco.com.sa")
TENANT_ID = os.getenv("METABRAIN_TENANT_ID", "metabrain-sso")
AUTH_URL = f"https://{AUTH_DOMAIN}/realms/{TENANT_ID}/protocol/openid-connect/token"

CHAT_URL = "https://dev-metabrain.aramco.com.sa/api/sessions/chats"

# Disable SSL Warnings globally for this module
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MetaBrainResponse:
    """Helper class to mock ModelResponse and provide to_gemini_format"""
    def __init__(self, text, success=True, error=None, raw_response=None):
        self.text = text
        self.success = success
        self.error = error
        self.raw_response = raw_response or {}
        
    def to_gemini_format(self):
        """Convert response to the format expected by frontend"""
        return {
            "candidates": [{
                "content": {
                    "parts": [{"text": self.text}],
                    "role": "model"
                },
                "finishReason": "STOP" if self.success else "ERROR",
                "index": 0
            }]
        }

class MetaBrainClient:
    """
    Dedicated client for MetaBrain API interaction.
    """

    def __init__(self, client_id: str = None, client_secret: str = None):
        self.client_id = client_id or os.getenv("METABRAIN_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("METABRAIN_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            logger.warning("MetaBrain credentials missing! Set METABRAIN_CLIENT_ID and METABRAIN_CLIENT_SECRET.")

        # Token cache
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    def _get_token(self) -> str:
        """
        Acquire or return cached OAuth2 access token.
        """
        # Return cached token if still valid (with 5 min buffer)
        if self._access_token and time.time() < (self._token_expires_at - 300):
            return self._access_token

        logger.info(f"Acquiring new MetaBrain token from {AUTH_URL}...")
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            logger.debug(f"Auth Request Data: grant_type=client_credentials, client_id={self.client_id}")
            
            # FORCE VERIFY=FALSE
            response = requests.post(AUTH_URL, data=data, headers=headers, timeout=30, verify=False)
            
            logger.debug(f"Auth Response Status: {response.status_code}")

            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            
            self._token_expires_at = time.time() + expires_in
            
            logger.info("MetaBrain token acquired successfully.")
            return self._access_token

        except Exception as e:
            logger.error(f"Failed to acquire MetaBrain token: {str(e)}")
            raise

    def chat(self, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a chat message to MetaBrain.
        """
        try:
            token = self._get_token()
        except Exception as e:
            return {
                "success": False,
                "error": f"Authentication failed: {str(e)}"
            }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # FIXED PAYLOAD KEY (Underscore instead of space)
        payload = {
            "question_body": question
        }
        if session_id:
            payload["user session id"] = session_id

        logger.info(f"Sending chat request to {CHAT_URL}")
        logger.debug(f"Chat Payload: {json.dumps(payload)}")

        try:
            # FORCE VERIFY=FALSE
            response = requests.post(CHAT_URL, json=payload, headers=headers, timeout=60, verify=False)
            
            logger.info(f"Chat Response Status: {response.status_code}")
            
            if response.status_code == 503:
                 return {
                    "success": False,
                    "error": "MetaBrain Service Unavailable (503)."
                }

            response.raise_for_status()
            
            data = response.json()
            # Extract fields expected by documentation
            answer = data.get("answer body", "") # Check for answer_body too if needed?
            if not answer:
                 answer = data.get("answer_body", "")

            new_session_id = data.get("user session id") or data.get("id")

            return {
                "success": True,
                "text": answer,
                "session_id": new_session_id,
                "raw": data
            }

        except Exception as e:
            logger.error(f"MetaBrain chat failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def generate(self, prompt: str, system_instruction: str = None, contents: List[Dict] = None, **kwargs) -> Any:
        """
        Adapter for the generate interface expected by MAHERModelClient.
        """
        # Use prompt if provided, otherwise extract from contents (Gemini format)
        final_prompt = prompt
        if not final_prompt and contents:
             for content in reversed(contents):
                if content.get('role') == 'user':
                    for part in content.get('parts', []):
                        final_prompt += part.get('text', '')
                    break
        
        if not final_prompt:
             return MetaBrainResponse("", success=False, error="No prompt provided")

        try:
            session_id = kwargs.get('session_id')
            
            # Prepend system instruction if available
            if system_instruction:
                final_prompt = f"System: {system_instruction}\n\nUser: {final_prompt}"

            result = self.chat(final_prompt, session_id)
            
            if result['success']:
                return MetaBrainResponse(result['text'], success=True, raw_response=result)
            else:
                return MetaBrainResponse("", success=False, error=result.get('error', 'Unknown error'))

        except Exception as e:
            logger.error(f"MetaBrain generate adapter failed: {str(e)}")
            return MetaBrainResponse("", success=False, error=str(e))

    def is_available(self) -> bool:
        """Check if MetaBrain credentials are configured"""
        return bool(self.client_id and self.client_secret)

    def get_provider_name(self) -> str:
        return "metabrain"
'''

def overwrite_metabrain_client():
    # Determine the path
    current_dir = os.getcwd()
    target_file = os.path.join(current_dir, "app", "backend", "metabrain_client.py")
    
    print(f"Overwriting file at: {target_file}")
    
    if not os.path.exists(os.path.dirname(target_file)):
         # Try logic for if running inside runtime folder
         target_file = os.path.join(current_dir, "..", "app", "backend", "metabrain_client.py")
         if not os.path.exists(os.path.dirname(target_file)):
             print("ERROR: app/backend folder not found.")
             return

    try:
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(FULL_CODE)
            
        print("SUCCESS: metabrain_client.py has been completely updated with all fixes.")
        print("1. SSL Verification Disabled")
        print("2. Correct 'question_body' payload")
        print("3. Response Helper Class added")
        print("Please restart the application.")

    except Exception as e:
        print(f"ERROR: Could not write file: {e}")

if __name__ == "__main__":
    overwrite_metabrain_client()
