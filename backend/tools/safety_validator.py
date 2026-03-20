"""
Safety Procedure Validator Tool
Validates maintenance procedures against safety standards
"""
from typing import Dict, Any, List


def validate_procedure(procedure_text: str, equipment_type: str) -> Dict[str, Any]:
    """
    Validate maintenance procedure for safety compliance

    Args:
        procedure_text: The procedure text to validate
        equipment_type: Type of equipment

    Returns:
        Validation results with safety recommendations
    """
    # Safety keywords that MUST be present
    required_safety_items = {
        "general": ["lock out", "tag out", "ppe", "personal protective equipment"],
        "electrical": ["de-energize", "voltage test", "ground", "arc flash"],
        "pressure": ["depressurize", "pressure relief", "vent"],
        "mechanical": ["support", "secure", "guard"]
    }

    # Determine equipment category
    equipment_category = "general"
    if any(word in equipment_type.lower() for word in ["motor", "electrical", "transformer"]):
        equipment_category = "electrical"
    elif any(word in equipment_type.lower() for word in ["pump", "compressor", "vessel"]):
        equipment_category = "pressure"
    elif any(word in equipment_type.lower() for word in ["conveyor", "lift", "crane"]):
        equipment_category = "mechanical"

    procedure_lower = procedure_text.lower()

    # Check for required safety items
    missing_items = []
    found_items = []

    # Check general safety items (always required)
    for item in required_safety_items["general"]:
        if item in procedure_lower:
            found_items.append(item)
        else:
            missing_items.append(f"General Safety: {item}")

    # Check category-specific items
    if equipment_category in required_safety_items:
        for item in required_safety_items[equipment_category]:
            if item in procedure_lower:
                found_items.append(item)
            else:
                missing_items.append(f"{equipment_category.title()} Safety: {item}")

    # Check for hazard warnings
    has_hazard_warning = any(word in procedure_lower for word in ["warning", "caution", "danger", "hazard"])

    # Check for permit requirements
    has_permit_reference = any(word in procedure_lower for word in ["permit", "authorization", "approval"])

    # Determine compliance level
    total_checks = len(required_safety_items["general"]) + len(required_safety_items.get(equipment_category, []))
    compliance_percentage = ((total_checks - len(missing_items)) / total_checks * 100) if total_checks > 0 else 0

    if compliance_percentage >= 90:
        compliance_level = "excellent"
        status = "approved"
    elif compliance_percentage >= 70:
        compliance_level = "good"
        status = "approved_with_recommendations"
    elif compliance_percentage >= 50:
        compliance_level = "fair"
        status = "requires_revision"
    else:
        compliance_level = "poor"
        status = "rejected"

    # Generate recommendations
    recommendations = []

    if missing_items:
        recommendations.append({
            "priority": "high",
            "category": "Missing Safety Items",
            "items": missing_items
        })

    if not has_hazard_warning:
        recommendations.append({
            "priority": "high",
            "category": "Documentation",
            "items": ["Add hazard warnings and safety notices"]
        })

    if not has_permit_reference:
        recommendations.append({
            "priority": "medium",
            "category": "Compliance",
            "items": ["Include work permit requirements"]
        })

    # Additional recommendations based on equipment type
    if equipment_category == "electrical":
        recommendations.append({
            "priority": "high",
            "category": "Electrical Safety",
            "items": [
                "Include arc flash boundary calculations",
                "Specify required PPE category",
                "Reference electrical safety standards"
            ]
        })

    return {
        "success": True,
        "validation_status": status,
        "compliance_level": compliance_level,
        "compliance_percentage": round(compliance_percentage, 1),
        "equipment_type": equipment_type,
        "equipment_category": equipment_category,
        "safety_items_found": len(found_items),
        "safety_items_missing": len(missing_items),
        "has_hazard_warnings": has_hazard_warning,
        "has_permit_reference": has_permit_reference,
        "missing_items": missing_items,
        "recommendations": recommendations,
        "next_steps": {
            "approved": "Procedure can be used as-is",
            "approved_with_recommendations": "Procedure acceptable but improvements recommended",
            "requires_revision": "Procedure must be revised before use",
            "rejected": "Procedure does not meet safety requirements - complete rewrite needed"
        }[status]
    }
