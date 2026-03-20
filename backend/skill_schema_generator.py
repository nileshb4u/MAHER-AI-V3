"""
MAHER AI — Skill Schema Generator
===================================
Uses the active model client to automatically generate an OpenAI
function-calling tool_schema from an agent's wizard data.

Called by AI Studio when a user clicks "Generate Skill Schema".
The returned schema is saved to the Agent.tool_schema column and
immediately picked up by SkillRetriever on next reload.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ── Prompt template ──────────────────────────────────────────────────────────

_SCHEMA_GEN_PROMPT = """
You are a software architect. Your task is to generate a JSON function-calling
schema (OpenAI "tools" format) for an AI skill described below.

SKILL DETAILS:
  Name:              {name}
  Category:          {category}
  Task Definition:   {task_definition}
  Required Expertise:{required_expertise}
  Decision Authority:{decision_authority}

RULES:
1. Output ONLY a valid JSON object — no markdown, no explanation.
2. The schema must follow this exact structure:
   {{
     "type": "function",
     "function": {{
       "name": "<snake_case_name_max_40_chars>",
       "description": "<one clear sentence telling the LLM WHEN to call this skill>",
       "parameters": {{
         "type": "object",
         "properties": {{
           "<param1>": {{"type": "string|number|boolean|array|object", "description": "..."}},
           ...
         }},
         "required": ["<param1>", ...]
       }}
     }}
   }}
3. Function name must be lowercase snake_case, ≤ 40 characters.
4. Description must start with a verb and mention the domain/context.
5. Include 2–5 parameters that make this skill callable and testable.
6. Mark only truly mandatory parameters as required.
7. Do NOT include file paths or system internals as parameters.
""".strip()


# ── Generator ────────────────────────────────────────────────────────────────

def generate_skill_schema(
    model_client,
    name: str,
    category: str,
    task_definition: str,
    required_expertise: str = "",
    decision_authority: str = "",
) -> Dict[str, Any]:
    """
    Generate an OpenAI tool_schema for an agent using the active model client.

    Returns:
        dict with keys:
          success   (bool)
          tool_schema  (dict | None)
          error     (str | None)
    """
    prompt = _SCHEMA_GEN_PROMPT.format(
        name=name,
        category=category,
        task_definition=task_definition or "Not specified",
        required_expertise=required_expertise or "Not specified",
        decision_authority=decision_authority or "Not specified",
    )

    try:
        response = model_client.generate(
            prompt=prompt,
            system_instruction=(
                "You are a JSON schema generator. Output only valid JSON, "
                "no prose, no markdown code fences."
            ),
            temperature=0.1,
            generation_config={"maxOutputTokens": 1024},
            response_mime_type="application/json",
        )

        if not response.success:
            return {"success": False, "tool_schema": None, "error": response.error}

        raw = response.text.strip()

        # Strip any accidental markdown fences
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
        raw = raw.strip()

        schema = json.loads(raw)

        # Validate minimal structure
        if not (
            isinstance(schema, dict)
            and schema.get("type") == "function"
            and "function" in schema
            and "name" in schema["function"]
        ):
            raise ValueError("Generated schema is missing required fields")

        # Sanitize function name
        fn_name = schema["function"]["name"]
        fn_name = re.sub(r"[^a-z0-9_]", "_", fn_name.lower())[:40]
        schema["function"]["name"] = fn_name

        logger.info(f"Generated skill schema for '{name}': {fn_name}")
        return {"success": True, "tool_schema": schema, "error": None}

    except json.JSONDecodeError as exc:
        logger.error(f"Schema generation produced invalid JSON for '{name}': {exc}")
        return {
            "success": False,
            "tool_schema": None,
            "error": f"Model output was not valid JSON: {exc}",
        }
    except Exception as exc:
        logger.error(f"Schema generation failed for '{name}': {exc}")
        return {"success": False, "tool_schema": None, "error": str(exc)}


def build_agent_tool_schema(agent_db_record) -> Optional[Dict]:
    """
    Build the OpenAI tool_schema for a database Agent whose
    implementation_type is 'llm_agent'.  This wraps the agent as a
    callable skill so the OSS model can invoke it via function calling.

    The generated schema treats the agent like a skill with a single
    'query' parameter — the model passes the relevant sub-question and
    the agent's system_prompt provides the expertise.
    """
    import re
    fn_name = re.sub(r"[^a-z0-9_]", "_", agent_db_record.name.lower())[:40]
    fn_name = fn_name.strip("_") or "agent_skill"

    return {
        "type": "function",
        "function": {
            "name": fn_name,
            "description": (
                f"{agent_db_record.description}  "
                f"Use this skill for {agent_db_record.category} tasks related to: "
                f"{(agent_db_record.system_prompt or '')[:120].strip()}"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The specific question or task to send to this AI skill",
                    },
                    "context": {
                        "type": "string",
                        "description": "Any additional context or background information (optional)",
                    },
                },
                "required": ["query"],
            },
        },
    }
