"""
Action Suggester for MAHER AI Orchestrator

Generates suggested actions based on agent response content and category.
Actions include document generation (PDF, Word, Excel) and contextual workflows.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def generate_suggested_actions(
    content: str,
    agent_category: str,
    agent_name: str = "Agent"
) -> List[Dict[str, Any]]:
    """
    Generate suggested actions based on response content and agent category
    
    Args:
        content: Agent's response text
        agent_category: Category/expertise of the agent
        agent_name: Name of the agent for context
    
    Returns:
        List of action dictionaries with id, label, type, format, endpoint, description
    """
    
    actions = []
    
    # Always offer PDF and Word downloads
    actions.extend([
        {
            "id": "generate_pdf",
            "label": "📄 Download as PDF",
            "type": "document",
            "format": "pdf",
            "endpoint": "/api/documents/generate",
            "description": "Download this response as a professional PDF document"
        },
        {
            "id": "generate_word",
            "label": "📝 Download as Word",
            "type": "document",
            "format": "word",
            "endpoint": "/api/documents/generate",
            "description": "Download this response as a Word document (.docx)"
        }
    ])
    
    # Add Excel if content has tables or structured data
    if has_tabular_data(content):
        actions.append({
            "id": "generate_excel",
            "label": "📊 Export to Excel",
            "type": "document",
            "format": "excel",
            "endpoint": "/api/documents/generate",
            "description": "Export data tables to Excel spreadsheet (.xlsx)"
        })
    
    # Add contextual actions based on agent category
    category_lower = agent_category.lower() if agent_category else ""
    
    if "maintenance" in category_lower:
        actions.extend([
            {
                "id": "create_schedule",
                "label": "📅 Create Maintenance Schedule",
                "type": "workflow",
                "endpoint": "/api/orchestrator/process",
                "prompt": "Create a detailed maintenance schedule based on the previous recommendations",
                "description": "Generate a comprehensive maintenance schedule"
            },
            {
                "id": "troubleshooting_guide",
                "label": "🔧 Generate Troubleshooting Guide",
                "type": "workflow",
                "endpoint": "/api/orchestrator/process",
                "prompt": "Create a troubleshooting guide for common issues",
                "description": "Create step-by-step troubleshooting procedures"
            }
        ])
    
    elif "safety" in category_lower:
        actions.extend([
            {
                "id": "safety_checklist",
                "label": "✅ Create Safety Checklist",
                "type": "workflow",
                "endpoint": "/api/orchestrator/process",
                "prompt": "Create a detailed safety checklist based on the procedures mentioned",
                "description": "Generate a comprehensive safety checklist"
            },
            {
                "id": "emergency_procedures",
                "label": "🚨 Emergency Response Procedures",
                "type": "workflow",
                "endpoint": "/api/orchestrator/process",
                "prompt": "Create emergency response procedures for this scenario",
                "description": "Generate emergency response protocols"
            }
        ])
    
    elif "planning" in category_lower or "schedule" in category_lower:
        actions.append({
            "id": "detailed_timeline",
            "label": "📊 Create Detailed Timeline",
            "type": "workflow",
            "endpoint": "/api/orchestrator/process",
            "prompt": "Create a detailed project timeline with milestones",
            "description": "Generate a comprehensive project timeline"
        })
    
    elif "analysis" in category_lower or "report" in category_lower:
        actions.append({
            "id": "executive_summary",
            "label": "📋 Generate Executive Summary",
            "type": "workflow",
            "endpoint": "/api/orchestrator/process",
            "prompt": "Create an executive summary of the analysis",
            "description": "Generate a concise executive summary"
        })
    
    # Add email draft action if content looks like it could be communicated
    if is_shareable_content(content):
        actions.append({
            "id": "draft_email",
            "label": "✉️ Draft Email",
            "type": "workflow",
            "endpoint": "/api/orchestrator/process",
            "prompt": "Draft a professional email to share this information",
            "description": "Create an email draft to share this information"
        })
    
    return actions


def has_tabular_data(content: str) -> bool:
    """
    Detect if content contains tables or structured data
    
    Args:
        content: Text content to analyze
    
    Returns:
        True if tabular data is detected
    """
    
    # Check for markdown tables (| column | column |)
    if '|' in content:
        lines = content.split('\n')
        table_lines = [line for line in lines if '|' in line]
        if len(table_lines) >= 3:  # At least header + separator + one row
            return True
    
    # Check for numbered lists with data patterns (1. Item: Value)
    if re.search(r'\d+\.\s+\w+:\s+[\d,]+', content):
        return True
    
    # Check for CSV-like patterns
    if re.search(r'(\w+,\s*){3,}', content):
        return True
    
    # Check for data patterns with multiple columns
    lines = content.split('\n')
    data_lines = 0
    for line in lines:
        # Look for lines with multiple tab-separated or space-separated values
        if re.search(r'\w+\s+\d+\s+\d+', line):
            data_lines += 1
    
    if data_lines >= 3:
        return True
    
    return False


def is_shareable_content(content: str) -> bool:
    """
    Detect if content is suitable for sharing via email
    
    Args:
        content: Text content to analyze
    
    Returns:
        True if content appears shareable
    """
    
    # Content should be substantial (not just a greeting)
    if len(content) < 100:
        return False
    
    # Check for informational content patterns
    informational_patterns = [
        r'(procedure|process|step|guideline|recommendation)',
        r'(checklist|requirement|specification)',
        r'(analysis|report|summary|finding)',
        r'(schedule|timeline|plan)'
    ]
    
    for pattern in informational_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    
    return False


def get_action_by_id(actions: List[Dict[str, Any]], action_id: str) -> Dict[str, Any]:
    """
    Get a specific action by its ID
    
    Args:
        actions: List of action dictionaries
        action_id: ID of the action to retrieve
    
    Returns:
        Action dictionary or None if not found
    """
    
    for action in actions:
        if action.get('id') == action_id:
            return action
    
    return None


def filter_actions_by_type(actions: List[Dict[str, Any]], action_type: str) -> List[Dict[str, Any]]:
    """
    Filter actions by type
    
    Args:
        actions: List of action dictionaries
        action_type: Type to filter by ('document', 'workflow', etc.)
    
    Returns:
        Filtered list of actions
    """
    
    return [action for action in actions if action.get('type') == action_type]
