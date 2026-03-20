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

try:
    import httpx
    from openai import OpenAI
    _OSS_AVAILABLE = True
except ImportError:
    _OSS_AVAILABLE = False

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
# GPT-OSS / vLLM Client  (OpenAI-compatible, self-hosted)
# ============================================================================

class GptOSSClient(BaseModelClient):
    """
    Client for self-hosted GPT-OSS / Qwen 3 served via vLLM.

    Exposes two call modes through the same generate() interface:
      - Plain generation  : no tools passed → streaming text response
      - Tool-calling      : tools injected  → ReAct loop handled by caller

    Tool calling is NOT streamed (vLLM returns tool_calls in a single
    non-streamed delta).  Final text answers ARE streamed.

    Environment variables:
        VLLM_SERVER_URL   : e.g. http://localhost:8000/v1
        VLLM_MODEL_PATH   : e.g. /home/cdsw/gpt-oss
        VLLM_API_KEY      : default "badr"
        VLLM_VERIFY_SSL   : "false" to disable SSL verification (default false)
    """

    # Token budget constants (tuned for 32 K context window)
    CONTEXT_LIMIT   = 32_000   # hard model limit
    RESPONSE_RESERVE = 4_096   # tokens kept for model output
    MAX_TOOL_TOKENS  = 2_000   # max tokens spent on injected schemas
    MAX_HIST_TOKENS  = 8_000   # rolling window for conversation history

    def __init__(
        self,
        base_url: str = None,
        model_path: str = None,
        api_key: str = None,
        verify_ssl: bool = None,
    ):
        if not _OSS_AVAILABLE:
            raise ImportError("openai and httpx packages are required for GptOSSClient")

        self.base_url   = base_url   or os.getenv("VLLM_SERVER_URL",  "http://localhost:8000/v1")
        self.model_path = model_path or os.getenv("VLLM_MODEL_PATH",  "/home/cdsw/gpt-oss")
        self.api_key    = api_key    or os.getenv("VLLM_API_KEY",     "badr")

        # SSL: default OFF because vLLM is typically on a private corporate network
        _env_verify = os.getenv("VLLM_VERIFY_SSL", "false").lower()
        self.verify_ssl = verify_ssl if verify_ssl is not None else (_env_verify == "true")

        self._http_client = httpx.Client(verify=self.verify_ssl)
        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            http_client=self._http_client,
        )
        logger.info(
            f"GptOSSClient initialised: url={self.base_url} "
            f"model={self.model_path} ssl_verify={self.verify_ssl}"
        )

    # ------------------------------------------------------------------
    # Token estimation (no tiktoken dependency required)
    # ------------------------------------------------------------------

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Fast word-based token estimate (~1.33 tokens/word)."""
        return max(1, len(str(text).split()) * 4 // 3)

    def _estimate_messages_tokens(self, messages: list) -> int:
        return sum(self._estimate_tokens(m.get("content") or "") for m in messages)

    def _estimate_tools_tokens(self, tools: list) -> int:
        return self._estimate_tokens(json.dumps(tools)) if tools else 0

    # ------------------------------------------------------------------
    # Conversation history trimmer (rolling window)
    # ------------------------------------------------------------------

    def _trim_history(
        self,
        history: List[Dict],
        budget: int,
    ) -> List[Dict]:
        """Keep the most recent turns that fit inside *budget* tokens."""
        kept, used = [], 0
        for msg in reversed(history[-30:]):          # never look back > 30 turns
            cost = self._estimate_tokens(msg.get("content") or "")
            if used + cost > budget:
                break
            kept.insert(0, msg)
            used += cost
        return kept

    # ------------------------------------------------------------------
    # Build a token-safe message list
    # ------------------------------------------------------------------

    def _build_messages(
        self,
        system: str,
        history: List[Dict],
        user_prompt: str,
        tools: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        """
        Assemble messages that fit within CONTEXT_LIMIT - RESPONSE_RESERVE.
        Priority: system > user_prompt > tools > recent history
        """
        available = self.CONTEXT_LIMIT - self.RESPONSE_RESERVE

        sys_tokens   = self._estimate_tokens(system)
        user_tokens  = self._estimate_tokens(user_prompt)
        tool_tokens  = min(self._estimate_tools_tokens(tools), self.MAX_TOOL_TOKENS)

        available -= sys_tokens + user_tokens + tool_tokens

        trimmed_history = self._trim_history(
            history,
            budget=min(available, self.MAX_HIST_TOKENS),
        )

        return (
            [{"role": "system", "content": system}]
            + trimmed_history
            + [{"role": "user", "content": user_prompt}]
        )

    # ------------------------------------------------------------------
    # Core generate() — satisfies BaseModelClient contract
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.3,
        contents: Optional[List[Dict]] = None,   # Gemini-style history (ignored here)
        generation_config: Optional[Dict] = None,
        response_mime_type: Optional[str] = None,
        # Extended kwargs for tool-aware callers
        tools: Optional[List[Dict]] = None,
        history: Optional[List[Dict]] = None,
    ) -> "ModelResponse":
        """
        Generate a response from GPT-OSS.

        - When *tools* is None  → plain streaming text call (your original schema).
        - When *tools* is set   → non-streamed call so tool_calls can be inspected.
          Callers that need the full ReAct loop should use generate_with_tools().
        """
        combined_system = MAHER_SYSTEM_PERSONA
        if system_instruction:
            combined_system = f"{MAHER_SYSTEM_PERSONA}\n\n{system_instruction}"

        gen_cfg   = generation_config or {}
        temp      = gen_cfg.get("temperature", temperature)
        max_tok   = gen_cfg.get("maxOutputTokens", 4096)   # sane default, NOT 32 K

        hist = history or []
        messages = self._build_messages(combined_system, hist, prompt, tools)

        try:
            if tools:
                # ── Tool-calling path (non-streamed) ──────────────────────
                response = self._client.chat.completions.create(
                    model=self.model_path,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=temp,
                    max_tokens=max_tok,
                    stream=False,
                )
                choice = response.choices[0]
                # Return raw tool_calls in raw_response for the orchestrator
                return ModelResponse(
                    text=choice.message.content or "",
                    provider="gpt-oss",
                    model=self.model_path,
                    success=True,
                    raw_response={
                        "tool_calls": [
                            {
                                "id":   tc.id,
                                "name": tc.function.name,
                                "args": tc.function.arguments,  # JSON string
                            }
                            for tc in (choice.message.tool_calls or [])
                        ],
                        "finish_reason": choice.finish_reason,
                    },
                )

            else:
                # ── Plain streaming path (your original schema) ───────────
                stream = self._client.chat.completions.create(
                    model=self.model_path,
                    messages=messages,
                    temperature=temp,
                    max_tokens=max_tok,
                    stream=True,
                )
                full_response = ""
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta

                return ModelResponse(
                    text=full_response,
                    provider="gpt-oss",
                    model=self.model_path,
                    success=True,
                )

        except Exception as e:
            logger.error(f"GptOSSClient.generate failed: {e}")
            return ModelResponse(
                text="",
                provider="gpt-oss",
                model=self.model_path,
                success=False,
                error=str(e),
            )

    # ------------------------------------------------------------------
    # generate_with_tools() — ReAct loop for the skills orchestrator
    # ------------------------------------------------------------------

    def generate_with_tools(
        self,
        user_message: str,
        system_prompt: str,
        history: List[Dict],
        tools: List[Dict],
        execute_skill_fn,          # callable(name: str, args: dict) -> dict
        max_loops: int = 5,
    ) -> str:
        """
        Full ReAct loop: Reason → Act (call skill) → Observe → repeat.

        *execute_skill_fn* is injected by the orchestrator so this client
        stays decoupled from the skills registry.

        Returns the final plain-text answer.
        """
        combined_system = f"{MAHER_SYSTEM_PERSONA}\n\n{system_prompt}"
        messages = self._build_messages(combined_system, history, user_message, tools)

        for loop in range(max_loops):
            response = self._client.chat.completions.create(
                model=self.model_path,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                temperature=0.1,      # low temp → deterministic tool selection
                max_tokens=4096,
                stream=False,
            )
            choice = response.choices[0]
            assistant_msg = choice.message

            # ── Final answer ──────────────────────────────────────────────
            if not assistant_msg.tool_calls:
                return assistant_msg.content or ""

            # ── Tool calls → execute each skill ──────────────────────────
            # Append assistant turn (with tool_calls) to history
            messages.append({
                "role":       "assistant",
                "content":    assistant_msg.content or "",
                "tool_calls": [
                    {
                        "id":       tc.id,
                        "type":     "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in assistant_msg.tool_calls
                ],
            })

            for tc in assistant_msg.tool_calls:
                try:
                    args   = json.loads(tc.function.arguments)
                    result = execute_skill_fn(tc.function.name, args)
                except Exception as exc:
                    result = {"error": str(exc)}

                # Truncate oversized tool results to protect token budget
                result_str = json.dumps(result)
                if self._estimate_tokens(result_str) > 1_500:
                    words      = result_str.split()
                    result_str = " ".join(words[:1_000]) + "  …[truncated]"

                messages.append({
                    "role":         "tool",
                    "tool_call_id": tc.id,
                    "content":      result_str,
                })

            # Re-trim messages to stay inside budget before next loop
            messages = self._enforce_budget(messages, combined_system, tools)

        logger.warning("GptOSSClient: max_loops reached without final answer")
        return "Maximum reasoning steps reached. Please refine your request."

    # ------------------------------------------------------------------
    # Post-loop budget enforcer (keeps messages list safe)
    # ------------------------------------------------------------------

    def _enforce_budget(
        self,
        messages: List[Dict],
        system: str,
        tools: Optional[List[Dict]],
    ) -> List[Dict]:
        """Trim middle turns if total token count is approaching the limit."""
        budget = self.CONTEXT_LIMIT - self.RESPONSE_RESERVE
        budget -= self._estimate_tokens(system)
        budget -= self._estimate_tools_tokens(tools)

        # Always keep system (index 0) and last user turn
        sys_msg   = messages[:1]
        rest      = messages[1:]
        kept, used = [], 0

        for msg in reversed(rest):
            cost = self._estimate_tokens(msg.get("content") or "")
            if used + cost > budget:
                break
            kept.insert(0, msg)
            used += cost

        return sys_msg + kept

    # ------------------------------------------------------------------
    # BaseModelClient interface
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        return _OSS_AVAILABLE and bool(self.base_url)

    def get_provider_name(self) -> str:
        return "gpt-oss"


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
        vllm_server_url: str = None,
        vllm_model_path: str = None,
    ):
        self.primary_provider = primary_provider or os.getenv("MODEL_PROVIDER", "metabrain")

        # Initialize clients
        self._metabrain = MetaBrainClient(
            client_id=metabrain_client_id,
            client_secret=metabrain_client_secret,
        )
        self._gemini = GeminiClient(api_key=gemini_api_key)

        # GPT-OSS client (optional — only if vLLM URL is configured)
        _vllm_url = vllm_server_url or os.getenv("VLLM_SERVER_URL", "")
        if _OSS_AVAILABLE and _vllm_url:
            self._gpt_oss = GptOSSClient(
                base_url=_vllm_url,
                model_path=vllm_model_path,
            )
        else:
            self._gpt_oss = None

        # Set 3-tier chain: primary → secondary → last_resort
        # Default: gpt-oss → metabrain → gemini
        if self.primary_provider == "gpt-oss" and self._gpt_oss:
            self._primary      = self._gpt_oss
            self._secondary    = self._metabrain
            self._last_resort  = self._gemini
        elif self.primary_provider == "gemini":
            self._primary      = self._gemini
            self._secondary    = self._metabrain
            self._last_resort  = self._gpt_oss or self._metabrain
        elif self.primary_provider == "metabrain":
            self._primary      = self._metabrain
            self._secondary    = self._gemini
            self._last_resort  = self._gpt_oss or self._gemini
        else:
            # Fallback default: gpt-oss → metabrain → gemini
            self._primary      = self._gpt_oss or self._metabrain
            self._secondary    = self._metabrain
            self._last_resort  = self._gemini

        # Keep _fallback as alias for secondary (backwards compatibility)
        self._fallback = self._secondary

        # Log configuration
        logger.info(
            f"Model client initialized: "
            f"primary={self._primary.get_provider_name()} (available={self._primary.is_available()}), "
            f"secondary={self._secondary.get_provider_name()} (available={self._secondary.is_available()}), "
            f"last_resort={self._last_resort.get_provider_name()} (available={self._last_resort.is_available()})"
        )

        if not any(p.is_available() for p in [self._primary, self._secondary, self._last_resort]):
            logger.warning(
                "WARNING: No model provider is configured! "
                "Set VLLM_SERVER_URL, METABRAIN_CLIENT_ID/SECRET, or GEMINI_API_KEY in .env"
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
        providers = [
            (self._primary,     "primary"),
            (self._secondary,   "secondary"),
            (self._last_resort, "last_resort"),
        ]

        for provider, tier in providers:
            if not provider.is_available():
                continue
            logger.debug(f"Generating with {tier}: {provider.get_provider_name()}")
            result = provider.generate(
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
                f"{tier} provider ({provider.get_provider_name()}) failed: "
                f"{result.error}. Trying next..."
            )

        # All three failed
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
    def metabrain(self) -> "MetaBrainClient":
        """Direct access to MetaBrain client"""
        return self._metabrain

    @property
    def gpt_oss(self) -> Optional["GptOSSClient"]:
        """Direct access to GPT-OSS client for tool-calling / skills orchestration"""
        return self._gpt_oss

    def get_active_provider(self) -> str:
        """Return which provider would be used for the next call"""
        for provider in [self._primary, self._secondary, self._last_resort]:
            if provider.is_available():
                return provider.get_provider_name()
        return "none"

    def get_status(self) -> Dict[str, Any]:
        """Return status of all providers for health endpoint"""
        status = {
            "primary": {
                "provider":  self._primary.get_provider_name(),
                "available": self._primary.is_available(),
            },
            "secondary": {
                "provider":  self._secondary.get_provider_name(),
                "available": self._secondary.is_available(),
            },
            "last_resort": {
                "provider":  self._last_resort.get_provider_name(),
                "available": self._last_resort.is_available(),
            },
            "active_provider": self.get_active_provider(),
        }
        if self._gpt_oss:
            status["gpt_oss"] = {
                "provider":  "gpt-oss",
                "available": self._gpt_oss.is_available(),
                "url":       self._gpt_oss.base_url,
                "model":     self._gpt_oss.model_path,
            }
        return status


# ============================================================================
# Singleton Factory
# ============================================================================

_client_instance: Optional[MAHERModelClient] = None


def get_model_client(
    gemini_api_key: str = None,
    metabrain_client_id: str = None,
    metabrain_client_secret: str = None,
    vllm_server_url: str = None,
    vllm_model_path: str = None,
) -> MAHERModelClient:
    """
    Get or create the singleton model client.

    Call this once at app startup or whenever needed.
    The singleton ensures token caching and connection reuse.

    Set MODEL_PROVIDER=gpt-oss and VLLM_SERVER_URL in .env to activate
    the self-hosted GPT-OSS / Qwen 3 provider.
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = MAHERModelClient(
            gemini_api_key=gemini_api_key,
            metabrain_client_id=metabrain_client_id,
            metabrain_client_secret=metabrain_client_secret,
            vllm_server_url=vllm_server_url,
            vllm_model_path=vllm_model_path,
        )
    return _client_instance


def reset_model_client():
    """Reset the singleton (for testing)"""
    global _client_instance
    _client_instance = None
