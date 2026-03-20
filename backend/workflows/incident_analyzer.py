"""
Incident Report Analyzer Workflow
Analyzes incident reports and extracts key information
"""
import asyncio
from typing import Dict, Any
from datetime import datetime


async def analyze_incident(incident_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze incident report and extract structured information

    Args:
        incident_data: Dictionary containing incident details

    Returns:
        Structured analysis with root cause, severity, and recommendations
    """
    await asyncio.sleep(0.3)

    # Extract fields from incident data
    description = incident_data.get("description", "")
    equipment = incident_data.get("equipment", "Unknown")
    location = incident_data.get("location", "Unknown")
    severity = incident_data.get("severity", "medium")

    # Analyze based on keywords
    root_causes = []
    if any(word in description.lower() for word in ["leak", "leaking", "spill"]):
        root_causes.append("Seal or gasket failure")
    if any(word in description.lower() for word in ["overheat", "hot", "temperature"]):
        root_causes.append("Thermal management issue")
    if any(word in description.lower() for word in ["vibration", "noise", "shake"]):
        root_causes.append("Mechanical imbalance or misalignment")
    if any(word in description.lower() for word in ["electrical", "spark", "short"]):
        root_causes.append("Electrical system failure")
    if any(word in description.lower() for word in ["wear", "worn", "eroded"]):
        root_causes.append("Component wear beyond acceptable limits")

    if not root_causes:
        root_causes.append("Requires detailed investigation")

    # Generate recommendations
    recommendations = [
        {
            "priority": "immediate",
            "action": "Isolate affected equipment and secure the area",
            "responsible": "Operations Team"
        },
        {
            "priority": "high",
            "action": "Conduct detailed root cause analysis",
            "responsible": "Maintenance Engineering"
        },
        {
            "priority": "medium",
            "action": "Review and update maintenance procedures",
            "responsible": "Maintenance Planning"
        }
    ]

    # Add specific recommendations based on root cause
    if "Seal or gasket failure" in root_causes:
        recommendations.append({
            "priority": "high",
            "action": "Inspect all similar equipment for seal condition",
            "responsible": "Maintenance Team"
        })

    if "Electrical system failure" in root_causes:
        recommendations.append({
            "priority": "immediate",
            "action": "Electrical safety inspection of affected circuit",
            "responsible": "Electrical Team"
        })

    # Determine severity level
    severity_levels = {
        "low": {
            "impact": "Minor operational disruption",
            "response_time": "24-48 hours",
            "escalation": False
        },
        "medium": {
            "impact": "Moderate equipment damage or production impact",
            "response_time": "4-8 hours",
            "escalation": True
        },
        "high": {
            "impact": "Significant safety risk or major equipment damage",
            "response_time": "Immediate",
            "escalation": True
        },
        "critical": {
            "impact": "Severe safety hazard or catastrophic failure",
            "response_time": "Immediate emergency response",
            "escalation": True
        }
    }

    severity_info = severity_levels.get(severity.lower(), severity_levels["medium"])

    return {
        "success": True,
        "incident_id": incident_data.get("id", f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
        "equipment": equipment,
        "location": location,
        "severity": severity,
        "severity_details": severity_info,
        "identified_root_causes": root_causes,
        "recommendations": recommendations,
        "requires_escalation": severity_info["escalation"],
        "analysis_timestamp": datetime.now().isoformat()
    }
