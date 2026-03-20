"""
MAHER AI - Unified Model Client Abstraction

Provides a single interface for all AI model providers:
- MetaBrain (Primary) - Aramco's enterprise AI platform
- Gemini (Fallback) - Google's Gemini API

MetaBrain is NOT a plain LLM API. It is a session-based Q&A service
with OAuth2 authentication (Keycloak). This client handles:
- Token lifecycle (acquisition, caching, refresh)
- MAHER persona injection (MetaBrain must never reveal its identity)
- Response normalization to a common format
- Automatic fallback to Gemini when MetaBrain is unavailable
"""

import os
import json
import time
import logging
import http.client
import urllib.parse
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

import requests

logger = logging.getLogger(__name__)

# MAHER system persona injected into all model calls
MAHER_SYSTEM_PERSONA = (
    "You are MAHER AI, a Virtual Maintenance Assistant developed by Saudi Aramco's "
    "Corporate Maintenance Services Department. You specialize in industrial maintenance, "
    "safety, engineering, and operations support. Be professional, clear, and helpful. "
    "CRITICAL: You must ALWAYS identify yourself as MAHER AI. Never reveal or mention "
    "any underlying AI platform, model name, or service provider. If asked who you are, "
    "respond only as MAHER AI."
)


# ============================================================================
# Common Response Format
# ============================================================================

class ModelResponse:
    """Normalized response from any model provider"""

    def __init__(
        self,
        text: str,
        provider: str,
        model: str,
        success: bool = True,
        usage: Optional[Dict[str, int]] = None,
        raw_response: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        self.text = text
        self.provider = provider
        self.model = model
        self.success = success
        self.usage = usage or {}
        self.raw_response = raw_response or {}
        self.error = error

    def to_gemini_format(self) -> Dict[str, Any]:
        """
        Convert to Gemini-compatible response format.
        This allows existing frontend code to work without changes.
        """
        response = {
            "candidates": [{
                "content": {
                    "parts": [{"text": self.text}],
                    "role": "model"
                },
                "finishReason": "STOP" if self.success else "ERROR",
                "index": 0
            }]
        }
        if self.usage:
            response["usageMetadata"] = self.usage
        return response


# ============================================================================
# Base Model Client
# ============================================================================

class BaseModelClient(ABC):
    """Abstract base class for all model providers"""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        contents: Optional[List[Dict]] = None,
        generation_config: Optional[Dict] = None,
        response_mime_type: Optional[str] = None,
    ) -> ModelResponse:
        """
        Generate a response from the model.

        Args:
            prompt: The user's question/prompt text
            system_instruction: Optional system instruction to prepend
            temperature: Sampling temperature (0.0 - 1.0)
            contents: Optional full conversation history (Gemini format)
            generation_config: Optional generation parameters
            response_mime_type: Optional response format (e.g. 'application/json')

        Returns:
            ModelResponse with normalized output
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is currently available"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name for logging"""
        pass


# ============================================================================
# MetaBrain Client
# ============================================================================

# Import the robust MetaBrainClient
from metabrain_client import MetaBrainClient


# ============================================================================
# Gemini Client
# ============================================================================

class GeminiClient(BaseModelClient):
    """
    Client for Google's Gemini API.
    Refactored from the original hardcoded calls throughout the codebase.
    """

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        self.api_base = os.getenv(
            "GEMINI_API_BASE",
            "https://generativelanguage.googleapis.com/v1beta"
        )

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        contents: Optional[List[Dict]] = None,
        generation_config: Optional[Dict] = None,
        response_mime_type: Optional[str] = None,
    ) -> ModelResponse:
        """Generate using Gemini API with full feature support"""
        try:
            url = f"{self.api_base}/models/{self.model}:generateContent"

            # Build contents - use provided history or create from prompt
            if contents:
                payload_contents = contents
            else:
                payload_contents = [{
                    "role": "user",
                    "parts": [{"text": prompt}]
                }]

            payload: Dict[str, Any] = {"contents": payload_contents}

            # System instruction - always include MAHER persona
            combined_instruction = MAHER_SYSTEM_PERSONA
            if system_instruction:
                combined_instruction = f"{MAHER_SYSTEM_PERSONA}\n\n{system_instruction}"

            payload["systemInstruction"] = {
                "parts": [{"text": combined_instruction}]
            }

            # Generation config
            gen_config = generation_config.copy() if generation_config else {}
            if "temperature" not in gen_config:
                gen_config["temperature"] = temperature
            if response_mime_type:
                gen_config["responseMimeType"] = response_mime_type
            if gen_config:
                payload["generationConfig"] = gen_config

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            }

            response = requests.post(url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()

            response_data = response.json()
            text = (
                response_data
                .get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )

            usage = response_data.get("usageMetadata", {})

            return ModelResponse(
                text=text,
                provider="gemini",
                model=self.model,
                success=True,
                usage=usage,
                raw_response=response_data,
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request failed: {e}")
            status_code = getattr(getattr(e, "response", None), "status_code", None)
            error_msg = f"Gemini API error (HTTP {status_code})" if status_code else str(e)
            return ModelResponse(
                text="",
                provider="gemini",
                model=self.model,
                success=False,
                error=error_msg,
            )
        except Exception as e:
            logger.error(f"Gemini generate failed: {e}")
            return ModelResponse(
                text="",
                provider="gemini",
                model=self.model,
                success=False,
                error=str(e),
            )

    def generate_raw(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Pass-through method for the chat proxy endpoint.
        Takes a pre-built Gemini payload and returns the raw API response.
        Used by /api/chat/generate to preserve full Gemini format for frontend.
        """
        url = f"{self.api_base}/models/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        return response.json()

    def stream_raw(self, payload: Dict[str, Any]):
        """
        Streaming pass-through for the chat stream endpoint.
        Returns a requests Response object for chunked streaming.
        """
        url = f"{self.api_base}/models/{self.model}:streamGenerateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        return requests.post(
            url, json=payload, headers=headers, stream=True, timeout=120
        )

    def is_available(self) -> bool:
        """Check if Gemini API key is configured"""
        return bool(self.api_key and self.api_key != "your_gemini_api_key_here")

    def get_provider_name(self) -> str:
        return "gemini"


# ============================================================================
# Model Client Factory with Fallback
# ============================================================================

class MAHERModelClient:
    """
    Unified model client with automatic fallback.

    Priority order (configurable via MODEL_PROVIDER env var):
    1. MetaBrain (primary in sandbox environment)
    2. Gemini (fallback)

    If the primary provider fails, automatically falls back to the secondary.
    """

    def __init__(
        self,
        primary_provider: str = None,
        gemini_api_key: str = None,
        metabrain_client_id: str = None,
        metabrain_client_secret: str = None,
    ):
        self.primary_provider = primary_provider or os.getenv("MODEL_PROVIDER", "metabrain")

        # Initialize clients
        self._metabrain = MetaBrainClient(
            client_id=metabrain_client_id,
            client_secret=metabrain_client_secret,
        )
        self._gemini = GeminiClient(api_key=gemini_api_key)

        # Set primary and fallback based on config
        if self.primary_provider == "gemini":
            self._primary = self._gemini
            self._fallback = self._metabrain
        else:
            self._primary = self._metabrain
            self._fallback = self._gemini

        # Log configuration
        primary_name = self._primary.get_provider_name()
        fallback_name = self._fallback.get_provider_name()
        primary_available = self._primary.is_available()
        fallback_available = self._fallback.is_available()

        logger.info(
            f"Model client initialized: primary={primary_name} "
            f"(available={primary_available}), "
            f"fallback={fallback_name} (available={fallback_available})"
        )

        if not primary_available and not fallback_available:
            logger.warning(
                "WARNING: No model provider is configured! "
                "Set METABRAIN_CLIENT_ID/SECRET or GEMINI_API_KEY in .env"
            )

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        contents: Optional[List[Dict]] = None,
        generation_config: Optional[Dict] = None,
        response_mime_type: Optional[str] = None,
    ) -> ModelResponse:
        """
        Generate a response using primary provider with automatic fallback.

        Args:
            prompt: User question/prompt
            system_instruction: Optional system context
            temperature: Sampling temperature
            contents: Optional conversation history
            generation_config: Optional Gemini-style generation config
            response_mime_type: Optional response format

        Returns:
            ModelResponse from whichever provider succeeded
        """
        # Try primary provider
        if self._primary.is_available():
            logger.debug(f"Generating with primary: {self._primary.get_provider_name()}")
            result = self._primary.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                contents=contents,
                generation_config=generation_config,
                response_mime_type=response_mime_type,
            )
            if result.success:
                return result
            logger.warning(
                f"Primary provider ({self._primary.get_provider_name()}) failed: "
                f"{result.error}. Falling back..."
            )

        # Try fallback provider
        if self._fallback.is_available():
            logger.info(f"Using fallback provider: {self._fallback.get_provider_name()}")
            result = self._fallback.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                contents=contents,
                generation_config=generation_config,
                response_mime_type=response_mime_type,
            )
            if result.success:
                return result
            logger.error(
                f"Fallback provider ({self._fallback.get_provider_name()}) also failed: "
                f"{result.error}"
            )

        # Both failed
        return ModelResponse(
            text="I apologize, but I'm currently unable to process your request. "
                 "The AI services are temporarily unavailable. Please try again shortly.",
            provider="none",
            model="none",
            success=False,
            error="All model providers unavailable",
        )

    @property
    def gemini(self) -> GeminiClient:
        """Direct access to Gemini client (for raw proxy endpoints)"""
        return self._gemini

    @property
    def metabrain(self) -> MetaBrainClient:
        """Direct access to MetaBrain client"""
        return self._metabrain

    def get_active_provider(self) -> str:
        """Return which provider would be used for the next call"""
        if self._primary.is_available():
            return self._primary.get_provider_name()
        if self._fallback.is_available():
            return self._fallback.get_provider_name()
        return "none"

    def get_status(self) -> Dict[str, Any]:
        """Return status of all providers for health endpoint"""
        return {
            "primary": {
                "provider": self._primary.get_provider_name(),
                "available": self._primary.is_available(),
            },
            "fallback": {
                "provider": self._fallback.get_provider_name(),
                "available": self._fallback.is_available(),
            },
            "active_provider": self.get_active_provider(),
        }


# ============================================================================
# Singleton Factory
# ============================================================================

_client_instance: Optional[MAHERModelClient] = None


def get_model_client(
    gemini_api_key: str = None,
    metabrain_client_id: str = None,
    metabrain_client_secret: str = None,
) -> MAHERModelClient:
    """
    Get or create the singleton model client.

    Call this once at app startup or whenever needed.
    The singleton ensures token caching and connection reuse.
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = MAHERModelClient(
            gemini_api_key=gemini_api_key,
            metabrain_client_id=metabrain_client_id,
            metabrain_client_secret=metabrain_client_secret,
        )
    return _client_instance


def reset_model_client():
    """Reset the singleton (for testing)"""
    global _client_instance
    _client_instance = None
