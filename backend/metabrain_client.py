
import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging specific to this client
logger = logging.getLogger("metabrain_client")
logger.setLevel(logging.DEBUG)

# Endpoints from documentation
AUTH_URL = "https://bl-metabrainv2-beyond-search-keycloak-metabrain-dev.apps.de2.aramco.com.sa/realms/metabrain-sso/protocol/openid-connect/token"
CHAT_URL = "https://dev-metabrain.aramco.com.sa/api/sessions/chats"

class MetaBrainClient:
    """
    Dedicated client for MetaBrain API interaction.
    Implements strictly the documentation provided:
    1. Client Credentials Auth Flow
    2. Session-based Chat API with simplified payload
    """

    def __init__(self, client_id: str = None, client_secret: str = None):
        self.client_id = client_id or os.getenv("METABRAIN_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("METABRAIN_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            logger.warning("MetaBrain credentials missing! Set METABRAIN_CLIENT_ID and METABRAIN_CLIENT_SECRET.")

        # SSL Verification setting (Default to True, but allow False for corporate proxies)
        self.verify_ssl = os.getenv("METABRAIN_VERIFY_SSL", "True").lower() == "true"
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logger.warning("SSL Verification disabled for MetaBrain client!")

        # Token cache
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    def _get_token(self) -> str:
        """
        Acquire or return cached OAuth2 access token.
        Renew if expired or about to expire (< 5 min remaining).
        """
        # Return cached token if still valid (with 5 min buffer)
        if self._access_token and time.time() < (self._token_expires_at - 300):
            return self._access_token

        logger.info(f"Acquiring new MetaBrain token from {AUTH_URL}...")
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Requests automatically encodes dict data as form-urlencoded
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            logger.debug(f"Auth Request Data: grant_type=client_credentials, client_id={self.client_id}")
            # SSL Verification DISABLED by default for this environment
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.post(AUTH_URL, data=data, headers=headers, timeout=30, verify=False)
            
            # Log raw response for debugging 503/4xx errors
            logger.debug(f"Auth Response Status: {response.status_code}")
            logger.debug(f"Auth Response Body: {response.text}")

            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            
            # Set expiration time
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

        # Simplified payload as per documentation
        payload = {
            "question body": question
        }
        if session_id:
            payload["user session id"] = session_id

        logger.info(f"Sending chat request to {CHAT_URL}")
        logger.debug(f"Chat Payload: {json.dumps(payload)}")

        try:
            # SSL Verification DISABLED
            response = requests.post(CHAT_URL, json=payload, headers=headers, timeout=60, verify=False)
            
            # Detailed logging for debugging
            logger.info(f"Chat Response Status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Chat Error Body: {response.text}")
                logger.error(f"Chat Error Headers: {response.headers}")

            if response.status_code == 503:
                return {
                    "success": False,
                    "error": "MetaBrain Service Unavailable (503). Attempting fallback."
                }

            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Chat Response Body: {json.dumps(data)}")

            # Extract fields expected by documentation
            answer = data.get("answer body", "")
            new_session_id = data.get("user session id") or data.get("id") # fallback to id if session id missing

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


class MetaBrainResponse:
    def __init__(self, text, success=True, error=None, raw_response=None):
        self.text = text
        self.success = success
        self.error = error
        self.raw_response = raw_response or {}
        
    def to_gemini_format(self):
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

        # Call the actual chat API
        try:
            # We don't have session persistence in this simple wrapper yet, 
            # so we start a new session or usage one if provided in kwargs
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
            logger.error(f"MetaBrain generate adapter failed: {e}")
            return MetaBrainResponse("", success=False, error=str(e))

    def is_available(self) -> bool:
        """Check if MetaBrain credentials are configured"""
        return bool(self.client_id and self.client_secret)

    def get_provider_name(self) -> str:
        return "metabrain"
