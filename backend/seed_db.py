"""
Database seeding script for MAHER AI
Initializes database with system agents loaded from backend/skills/*.md files.

Each .md file must have YAML frontmatter with at minimum:
  id, name, description, category
The markdown body becomes the system_prompt.
"""

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Load agent data from skills/*.md files
# ---------------------------------------------------------------------------

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False
    logger.warning("PyYAML not available. Falling back to hardcoded system agents.")


def _load_agents_from_skills_dir() -> list:
    """
    Parse every *.md file in the skills/ directory that lives next to this
    script and return a list of agent dicts ready for DB insertion.
    """
    if not _YAML_AVAILABLE:
        return []

    skills_dir = Path(__file__).parent / "skills"
    if not skills_dir.is_dir():
        logger.warning(f"skills/ directory not found at {skills_dir}")
        return []

    agents = []
    for md_file in sorted(skills_dir.glob("*.md")):
        try:
            raw = md_file.read_text(encoding="utf-8")
            fm_match = re.match(
                r"^\s*---\s*\n(.*?)\n---\s*\n?(.*)",
                raw,
                re.DOTALL,
            )
            if not fm_match:
                continue

            fm_text, body = fm_match.group(1), fm_match.group(2).strip()
            meta = yaml.safe_load(fm_text)

            if not isinstance(meta, dict):
                continue

            agent_id = meta.get("id") or md_file.stem
            tool_schema = meta.get("tool_schema")

            agents.append({
                "agent_id":              str(agent_id),
                "name":                  meta.get("name", md_file.stem),
                "description":           meta.get("description", ""),
                "system_prompt":         body,
                "category":              meta.get("category", "other"),
                "icon_svg":              meta.get("icon_svg"),
                "icon_background_color": meta.get("icon_color", "#4f46e5"),
                "default_provider":      "MAHER AI Engine",
                "display_provider_name": "Powered by MAHER AI",
                "implementation_type":   meta.get("implementation_type", "llm_agent"),
                "skill_version":         str(meta.get("version", "1.0.0")),
                "tool_schema":           json.dumps(tool_schema) if tool_schema else None,
            })
        except Exception as exc:
            logger.warning(f"seed_db: failed to parse {md_file.name}: {exc}")

    return agents


# ---------------------------------------------------------------------------
# Fallback: hardcoded agents (used only when PyYAML is unavailable)
# ---------------------------------------------------------------------------

_FALLBACK_AGENTS = [
    {
        'agent_id': 'agent-1',
        'name': 'Schematic Analyst',
        'description': 'Interprets and answers questions about technical drawings, P&IDs, and electrical diagrams.',
        'system_prompt': 'You are an expert in interpreting technical schematics, P&IDs, and electrical diagrams. When a user uploads a schematic and asks a question, analyze the visual information to provide a precise and accurate answer.',
        'category': 'maintenance',
        'icon_background_color': '#2563eb',
        'default_provider': 'MAHER AI Engine',
        'display_provider_name': 'Powered by MAHER AI',
        'implementation_type': 'llm_agent',
        'skill_version': '1.0.0',
    },
    {
        'agent_id': 'agent-2',
        'name': 'Procedure Writer',
        'description': 'Generates step-by-step Standard Operating Procedures (SOPs) or maintenance routines.',
        'system_prompt': "You are a technical writer specializing in creating Standard Operating Procedures (SOPs) for industrial maintenance.",
        'category': 'maintenance',
        'icon_background_color': '#db2777',
        'default_provider': 'MAHER AI Engine',
        'display_provider_name': 'Powered by MAHER AI',
        'implementation_type': 'llm_agent',
        'skill_version': '1.0.0',
    },
    {
        'agent_id': 'agent-3',
        'name': 'Incident Report Analyzer',
        'description': 'Summarizes incident reports, identifies root causes, and suggests corrective actions.',
        'system_prompt': 'You are an AI assistant for safety officers and reliability engineers. Your task is to analyze incident reports using 5-Whys and propose CAPAs.',
        'category': 'safety',
        'icon_background_color': '#ca8a04',
        'default_provider': 'MAHER AI Engine',
        'display_provider_name': 'Powered by MAHER AI',
        'implementation_type': 'llm_agent',
        'skill_version': '1.0.0',
    },
    {
        'agent_id': 'agent-4',
        'name': 'Contracts Assistant',
        'description': 'Reviews commercial contracts, highlights key clauses, and identifies risks.',
        'system_prompt': 'You are a commercial contract analysis assistant. Review documents, summarize key clauses, and highlight risks. Include a disclaimer that your analysis is not legal advice.',
        'category': 'contracts',
        'icon_background_color': '#4f46e5',
        'default_provider': 'MAHER AI Engine',
        'display_provider_name': 'Powered by MAHER AI',
        'implementation_type': 'llm_agent',
        'skill_version': '1.0.0',
    },
    {
        'agent_id': 'agent-5',
        'name': 'Operations Copilot',
        'description': 'Provides real-time support for plant operators to troubleshoot alarms.',
        'system_prompt': 'You are an operations support copilot for industrial plant operators. Provide clear, prioritized troubleshooting steps when an operator describes an alarm or process deviation. Always prioritize safety.',
        'category': 'operations',
        'icon_background_color': '#059669',
        'default_provider': 'MAHER AI Engine',
        'display_provider_name': 'Powered by MAHER AI',
        'implementation_type': 'llm_agent',
        'skill_version': '1.0.0',
    },
    {
        'agent_id': 'agent-6',
        'name': 'Project Planner',
        'description': 'Assists in creating project plans and timelines for maintenance turnarounds.',
        'system_prompt': 'You are a project management assistant specializing in industrial maintenance turnarounds. Create high-level project plans with WBS, Gantt timelines, and resource lists.',
        'category': 'projects',
        'icon_background_color': '#6d28d9',
        'default_provider': 'MAHER AI Engine',
        'display_provider_name': 'Powered by MAHER AI',
        'implementation_type': 'llm_agent',
        'skill_version': '1.0.0',
    },
]


def _get_system_agents() -> list:
    agents = _load_agents_from_skills_dir()
    if agents:
        print(f"  Loaded {len(agents)} system agents from skills/ directory")
        return agents
    print("  WARNING: Falling back to hardcoded system agents (install pyyaml to use .md files)")
    return _FALLBACK_AGENTS


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

from models import init_db, SessionLocal, Agent, AgentStatus


def seed_system_agents():
    """Seed database with system agents loaded from skills/*.md files."""
    db = SessionLocal()

    try:
        print("Seeding system agents...")

        system_agents = _get_system_agents()

        for agent_data in system_agents:
            existing = db.query(Agent).filter(
                Agent.agent_id == agent_data['agent_id']
            ).first()

            if existing:
                print(f"  ⚠️  Agent '{agent_data['name']}' already exists, skipping...")
                continue

            agent = Agent(
                agent_id=agent_data['agent_id'],
                name=agent_data['name'],
                description=agent_data['description'],
                system_prompt=agent_data['system_prompt'],
                category=agent_data['category'],
                icon_svg=agent_data.get('icon_svg'),
                icon_background_color=agent_data.get('icon_background_color', '#4f46e5'),
                default_provider=agent_data.get('default_provider', 'MAHER AI Engine'),
                display_provider_name=agent_data.get('display_provider_name', 'Powered by MAHER AI'),
                status=AgentStatus.PUBLISHED,
                is_system=True,
                created_by='system',
                implementation_type=agent_data.get('implementation_type', 'llm_agent'),
                skill_version=agent_data.get('skill_version', '1.0.0'),
                tool_schema=agent_data.get('tool_schema'),
            )

            db.add(agent)
            print(f"  ✓ Added system agent: {agent_data['name']}")

        db.commit()
        print("\n✓ System agents seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"\n✗ Error seeding system agents: {e}")
        raise
    finally:
        db.close()


def main():
    print("=" * 60)
    print("MAHER AI - Database Initialization")
    print("=" * 60)
    print()

    print("Initializing database...")
    init_db()
    print("✓ Database tables created\n")

    seed_system_agents()

    print()
    print("=" * 60)
    print("Database setup complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
