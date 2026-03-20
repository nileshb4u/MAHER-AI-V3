"""
MAHER AI — Skills Orchestrator
===============================
Replaces the 1300-line hybrid_orchestrator for GPT-OSS / Qwen 3 deployments.

Design principles
-----------------
* Zero extra LLM routing calls  — the OSS model selects skills via native
  function-calling (tool_choice="auto").
* 32 K token budget respected   — SkillRetriever injects only 3–7 relevant
  schemas per query; TokenAwareMessageBuilder trims history.
* Streaming final answer         — tool-call loops run non-streamed; the
  final text answer is streamed back to the caller via a generator.
* Provider-agnostic fallback     — if GPT-OSS is unavailable the orchestrator
  falls back to whatever MAHERModelClient has configured (MetaBrain/Gemini).

Endpoints added to app.py
--------------------------
  POST /api/skills-orchestrator/process
  POST /api/skills-orchestrator/reload          (admin, hot-reload registry)
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, Generator, List, Optional

logger = logging.getLogger(__name__)


class SkillsOrchestrator:
    """
    Thin orchestration layer that wires SkillRetriever + GptOSSClient.

    Args:
        model_client: MAHERModelClient singleton (already initialised by app.py)
        registry_path: Absolute path to registry.json
    """

    def __init__(self, model_client, registry_path: str):
        from skill_retriever import SkillRetriever

        self.model_client = model_client
        self.retriever    = SkillRetriever(registry_path=registry_path)

        # The OSS client exposes the full ReAct loop
        self._oss = getattr(model_client, "gpt_oss", None)
        if self._oss is None:
            logger.warning(
                "SkillsOrchestrator: GPT-OSS client is not configured. "
                "Set VLLM_SERVER_URL and MODEL_PROVIDER=gpt-oss in .env. "
                "Falling back to MAHERModelClient for plain generation."
            )

    # ------------------------------------------------------------------
    # Main entry point (used by Flask endpoint)
    # ------------------------------------------------------------------

    def process(
        self,
        user_message: str,
        conversation_history: List[Dict],
        system_prompt: str = "",
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Synchronous process — returns a response dict compatible with the
        existing /api/hybrid-orchestrator/process response shape.

        When *stream* is True the dict contains a 'stream_generator' key
        that the Flask endpoint should iterate over via server-sent events.
        """
        start = time.time()

        # 1. Retrieve relevant skills for this specific query
        relevant_tools = self.retriever.retrieve(user_message, top_k=5)
        skill_names    = [t["function"]["name"] for t in relevant_tools]
        logger.info(
            f"SkillsOrchestrator: retrieved {len(relevant_tools)} skills "
            f"for query '{user_message[:60]}': {skill_names}"
        )

        # 2. Route to OSS client if available, else plain fallback
        if self._oss and self._oss.is_available():
            answer = self._oss.generate_with_tools(
                user_message=user_message,
                system_prompt=system_prompt,
                history=conversation_history,
                tools=relevant_tools,
                execute_skill_fn=self.retriever.execute,
            )
        else:
            # Graceful fallback — no tool calling, plain generation
            logger.info("SkillsOrchestrator: using fallback provider (no tool calls)")
            response = self.model_client.generate(
                prompt=user_message,
                system_instruction=system_prompt,
                contents=self._to_gemini_history(conversation_history),
            )
            answer = response.text

        elapsed = round(time.time() - start, 2)

        return {
            "success":       True,
            "response":      answer,
            "skills_used":   skill_names,
            "provider":      self._oss.get_provider_name() if self._oss else "fallback",
            "elapsed_sec":   elapsed,
        }

    # ------------------------------------------------------------------
    # Streaming variant (generator-based, for SSE endpoints)
    # ------------------------------------------------------------------

    def process_stream(
        self,
        user_message: str,
        conversation_history: List[Dict],
        system_prompt: str = "",
    ) -> Generator[str, None, None]:
        """
        Yields SSE-formatted chunks for streaming responses.

        Tool-call loops run synchronously (non-streamed) first; only the
        final answer text is streamed to the client.
        """
        if not (self._oss and self._oss.is_available()):
            # Fallback: generate full answer and yield in one chunk
            result = self.process(user_message, conversation_history, system_prompt)
            yield f"data: {json.dumps({'text': result['response']})}\n\n"
            yield "data: [DONE]\n\n"
            return

        relevant_tools = self.retriever.retrieve(user_message, top_k=5)

        import httpx
        from openai import OpenAI

        http_client = httpx.Client(verify=self._oss.verify_ssl)
        client      = OpenAI(
            base_url=self._oss.base_url,
            api_key=self._oss.api_key,
            http_client=http_client,
        )

        from model_client import MAHER_SYSTEM_PERSONA
        combined_system = (
            f"{MAHER_SYSTEM_PERSONA}\n\n{system_prompt}" if system_prompt
            else MAHER_SYSTEM_PERSONA
        )

        # Run the ReAct loop non-streamed (tool calls must be non-streamed)
        messages = self._oss._build_messages(
            combined_system, conversation_history, user_message, relevant_tools
        )

        for _ in range(self._oss.__class__.__dict__.get("_MAX_LOOPS", 5)):
            resp = client.chat.completions.create(
                model=self._oss.model_path,
                messages=messages,
                tools=relevant_tools if relevant_tools else None,
                tool_choice="auto" if relevant_tools else None,
                temperature=0.1,
                max_tokens=4096,
                stream=False,
            )
            choice = resp.choices[0]

            if not choice.message.tool_calls:
                # Final answer — stream it
                final_text = choice.message.content or ""
                chunk_size = 80   # characters per SSE chunk
                for i in range(0, len(final_text), chunk_size):
                    yield f"data: {json.dumps({'text': final_text[i:i+chunk_size]})}\n\n"
                yield "data: [DONE]\n\n"
                return

            # Execute tool calls and append results
            messages.append({
                "role":       "assistant",
                "content":    choice.message.content or "",
                "tool_calls": [
                    {
                        "id":       tc.id,
                        "type":     "function",
                        "function": {
                            "name":      tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in choice.message.tool_calls
                ],
            })

            for tc in choice.message.tool_calls:
                try:
                    args   = json.loads(tc.function.arguments)
                    result = self.retriever.execute(tc.function.name, args)
                except Exception as exc:
                    result = {"error": str(exc)}

                result_str = json.dumps(result)
                if self._oss._estimate_tokens(result_str) > 1_500:
                    result_str = " ".join(result_str.split()[:1_000]) + " …[truncated]"

                messages.append({
                    "role":         "tool",
                    "tool_call_id": tc.id,
                    "content":      result_str,
                })

            messages = self._oss._enforce_budget(messages, combined_system, relevant_tools)

        yield f"data: {json.dumps({'text': 'Maximum reasoning steps reached.'})}\n\n"
        yield "data: [DONE]\n\n"

    # ------------------------------------------------------------------
    # Hot-reload (called by admin endpoint after AI Studio publishes skill)
    # ------------------------------------------------------------------

    def reload_skills(self) -> Dict[str, Any]:
        self.retriever.reload()
        return {
            "success":      True,
            "skills_count": len(self.retriever._schemas),
        }

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _to_gemini_history(history: List[Dict]) -> List[Dict]:
        """Convert OpenAI-format history to Gemini contents format for fallback."""
        result = []
        for msg in history:
            role = "model" if msg.get("role") == "assistant" else "user"
            result.append({
                "role":  role,
                "parts": [{"text": msg.get("content", "")}],
            })
        return result
