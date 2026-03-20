"""
MAHER AI — Skill Retriever
==========================
Semantic lookup layer that sits between the user query and the skills
registry.  Instead of injecting every skill schema into the model context
(which would exhaust the 32 K token budget), this retriever embeds the
user query and returns only the top-K most relevant skill schemas.

No LLM call is needed — retrieval is done with a tiny sentence-transformer
model that runs on CPU in ~5 ms.

Fallback:
  If sentence-transformers is not installed, falls back to a simple keyword
  overlap scorer so the system still works without the extra dependency.
"""

from __future__ import annotations

import json
import logging
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional sentence-transformers import
# ---------------------------------------------------------------------------
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _SBERT_AVAILABLE = True
except ImportError:
    _SBERT_AVAILABLE = False
    logger.warning(
        "sentence-transformers not installed. "
        "Skill retriever will use keyword-overlap fallback. "
        "Install with: pip install sentence-transformers"
    )

# Lightweight model — 80 MB, CPU-only, ~5 ms per encode
_DEFAULT_EMBED_MODEL = "all-MiniLM-L6-v2"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tool_schema_text(schema: Dict) -> str:
    """Flatten a tool schema to a single string for embedding."""
    fn = schema.get("function", {})
    parts = [fn.get("name", ""), fn.get("description", "")]
    props = fn.get("parameters", {}).get("properties", {})
    for pname, pdef in props.items():
        parts.append(f"{pname}: {pdef.get('description', '')}")
    return " ".join(filter(None, parts))


def _keyword_score(query: str, text: str) -> float:
    """Simple token-overlap score (0–1) used as fallback."""
    q_tokens = set(re.findall(r"\w+", query.lower()))
    t_tokens = set(re.findall(r"\w+", text.lower()))
    if not q_tokens:
        return 0.0
    return len(q_tokens & t_tokens) / len(q_tokens)


# ---------------------------------------------------------------------------
# SkillRetriever
# ---------------------------------------------------------------------------

class SkillRetriever:
    """
    Retrieves the most relevant skill tool-schemas for a user query.

    Usage:
        retriever = SkillRetriever(registry_path="registry.json")
        tools = retriever.retrieve("generate a maintenance report for pump P-101")
        # → list of up to 5 OpenAI-format tool dicts
    """

    def __init__(
        self,
        registry_path: str,
        embed_model: str = _DEFAULT_EMBED_MODEL,
        default_top_k: int = 5,
        similarity_threshold: float = 0.20,
    ):
        self.registry_path = Path(registry_path)
        self.default_top_k = default_top_k
        self.similarity_threshold = similarity_threshold

        # Load and index skills
        self._skills: List[Dict]   = []          # full registry entries
        self._schemas: List[Dict]  = []          # OpenAI tool-schema dicts
        self._texts: List[str]     = []          # text representation for embed
        self._embeddings = None                   # np.ndarray once computed

        self._load_registry()

        if _SBERT_AVAILABLE and self._schemas:
            try:
                self._encoder = SentenceTransformer(embed_model)
                self._build_embeddings()
                logger.info(
                    f"SkillRetriever: loaded {len(self._schemas)} skills "
                    f"with SBERT embeddings ({embed_model})"
                )
            except Exception as exc:
                logger.warning(f"SkillRetriever: SBERT init failed ({exc}), using keyword fallback")
                self._encoder = None
        else:
            self._encoder = None
            logger.info(
                f"SkillRetriever: loaded {len(self._schemas)} skills "
                f"with keyword-overlap fallback"
            )

    # ------------------------------------------------------------------
    # Registry loading
    # ------------------------------------------------------------------

    def _load_registry(self) -> None:
        """Parse registry.json and collect every entry that has a tool_schema."""
        if not self.registry_path.exists():
            logger.error(f"SkillRetriever: registry not found at {self.registry_path}")
            return

        try:
            with open(self.registry_path) as f:
                registry = json.load(f)
        except Exception as exc:
            logger.error(f"SkillRetriever: failed to parse registry: {exc}")
            return

        resources = registry.get("resources", {})

        for category in ("tools", "workflows", "ai_agents"):
            for entry in resources.get(category, []):
                schema = entry.get("tool_schema")
                # Only include published entries that have a tool_schema
                if schema and entry.get("status", "published") == "published":
                    self._skills.append(entry)
                    self._schemas.append(schema)
                    self._texts.append(_tool_schema_text(schema))

        # Also load from the skills/ folder (Markdown files with YAML frontmatter)
        skills_dir = self.registry_path.parent / "skills"
        if skills_dir.is_dir():
            self._load_skill_files(skills_dir)

    def _load_skill_files(self, skills_dir: Path) -> None:
        """
        Scan *skills_dir* for *.md files, parse YAML frontmatter, and
        register any entry that contains a ``tool_schema`` block.

        File format
        -----------
        ---
        id: agent-1
        name: Schematic Analyst
        description: ...
        category: maintenance
        icon_color: "#2563eb"
        status: available          # published | available | draft
        implementation_type: llm_agent
        tool_schema:
          type: function
          function:
            name: schematic_analyst
            description: ...
            parameters: ...
        ---

        The markdown body (below the closing ---) becomes the system_prompt.
        """
        if not _YAML_AVAILABLE:
            logger.warning(
                "SkillRetriever: PyYAML not available — cannot load .md skill files. "
                "Install with: pip install pyyaml"
            )
            return

        loaded = 0
        for md_file in sorted(skills_dir.glob("*.md")):
            try:
                raw = md_file.read_text(encoding="utf-8")

                # Split frontmatter from body
                # Supports --- delimited YAML at the top of the file
                fm_match = re.match(
                    r"^\s*---\s*\n(.*?)\n---\s*\n?(.*)",
                    raw,
                    re.DOTALL,
                )
                if not fm_match:
                    logger.debug(
                        f"SkillRetriever: {md_file.name} has no YAML frontmatter, skipping"
                    )
                    continue

                fm_text, body = fm_match.group(1), fm_match.group(2).strip()
                meta = yaml.safe_load(fm_text)

                if not isinstance(meta, dict):
                    continue

                # Skip drafts
                status = str(meta.get("status", "available")).lower()
                if status == "draft":
                    continue

                schema = meta.get("tool_schema")
                if not schema:
                    logger.debug(
                        f"SkillRetriever: {md_file.name} has no tool_schema, skipping"
                    )
                    continue

                entry = {
                    "id":                  meta.get("id", md_file.stem),
                    "name":                meta.get("name", md_file.stem),
                    "description":         meta.get("description", ""),
                    "category":            meta.get("category", "other"),
                    "icon_color":          meta.get("icon_color", "#4f46e5"),
                    "status":              status,
                    "implementation_type": meta.get("implementation_type", "llm_agent"),
                    "skill_version":       str(meta.get("version", "1.0.0")),
                    "system_prompt":       body,
                    "source":              "skill_file",
                    "file":                str(md_file),
                    "tool_schema":         schema,
                    # Skill execution: llm_agent skills are dispatched by the
                    # orchestrator itself (no module_path needed).
                    "module_path":         meta.get("module_path"),
                    "function":            meta.get("function"),
                }

                self._skills.append(entry)
                self._schemas.append(schema)
                self._texts.append(_tool_schema_text(schema))
                loaded += 1

            except Exception as exc:
                logger.warning(
                    f"SkillRetriever: failed to load {md_file.name}: {exc}"
                )

        if loaded:
            logger.info(
                f"SkillRetriever: loaded {loaded} skills from {skills_dir}"
            )

    def _build_embeddings(self) -> None:
        if self._texts:
            self._embeddings = self._encoder.encode(
                self._texts,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> List[Dict]:
        """
        Return the top-K OpenAI tool-schema dicts most relevant to *query*.

        Args:
            query:     User message / intent description
            top_k:     Override default_top_k
            threshold: Override similarity_threshold

        Returns:
            List of OpenAI-format tool dicts (may be empty if nothing matches)
        """
        if not self._schemas:
            return []

        k     = top_k     if top_k     is not None else self.default_top_k
        thr   = threshold if threshold is not None else self.similarity_threshold

        if self._encoder is not None and self._embeddings is not None:
            scores = self._sbert_scores(query)
        else:
            scores = self._keyword_scores(query)

        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        result = []
        for idx, score in ranked[:k]:
            if score >= thr:
                result.append(self._schemas[idx])

        logger.debug(
            f"SkillRetriever: query='{query[:60]}' → "
            f"{len(result)} tools (top score={ranked[0][1]:.3f} if ranked else 0)"
        )
        return result

    def _sbert_scores(self, query: str):
        q_emb = self._encoder.encode([query], normalize_embeddings=True)
        return (q_emb @ self._embeddings.T)[0].tolist()

    def _keyword_scores(self, query: str):
        return [_keyword_score(query, t) for t in self._texts]

    # ------------------------------------------------------------------
    # Skill execution helper (used by the orchestrator)
    # ------------------------------------------------------------------

    def get_skill_meta(self, tool_name: str) -> Optional[Dict]:
        """Return the full registry entry for a skill by its function name."""
        for entry in self._skills:
            fn_name = entry.get("tool_schema", {}).get("function", {}).get("name", "")
            if fn_name == tool_name:
                return entry
        return None

    def execute(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Dynamically import and call the skill implementation.

        For ``llm_agent`` skills loaded from .md files there is no Python
        module — the orchestrator handles them via a model call using the
        skill's ``system_prompt``.  In that case we return the metadata so
        the caller can dispatch appropriately.

        Falls back to an informative error dict on any failure.
        """
        import importlib

        meta = self.get_skill_meta(tool_name)
        if not meta:
            return {"error": f"Skill '{tool_name}' not found in registry"}

        # LLM-agent skills (from .md files) have no module_path
        impl_type = meta.get("implementation_type", "llm_agent")
        if impl_type == "llm_agent" and not meta.get("module_path"):
            return {
                "__type__":     "llm_agent",
                "system_prompt": meta.get("system_prompt", ""),
                "args":          args,
                "skill_name":    tool_name,
            }

        module_path   = meta.get("module_path")
        function_name = meta.get("function")

        if not module_path or not function_name:
            return {"error": f"Skill '{tool_name}' has no implementation pointer"}

        try:
            module = importlib.import_module(module_path)
            func   = getattr(module, function_name)
            return func(**args)
        except ImportError as exc:
            logger.error(f"SkillRetriever: cannot import {module_path}: {exc}")
            return {"error": f"Module '{module_path}' not available: {exc}"}
        except TypeError as exc:
            logger.error(f"SkillRetriever: bad args for {tool_name}: {exc}")
            return {"error": f"Invalid arguments for skill '{tool_name}': {exc}"}
        except Exception as exc:
            logger.error(f"SkillRetriever: execution error in {tool_name}: {exc}")
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Hot-reload (call after AI Studio publishes a new skill)
    # ------------------------------------------------------------------

    def reload(self) -> None:
        """Re-read registry and re-build embeddings (no restart required)."""
        self._skills.clear()
        self._schemas.clear()
        self._texts.clear()
        self._embeddings = None
        self._load_registry()
        if self._encoder and self._texts:
            self._build_embeddings()
        logger.info(f"SkillRetriever: reloaded {len(self._schemas)} skills")
