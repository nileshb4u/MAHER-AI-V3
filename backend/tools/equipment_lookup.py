"""
Equipment Database Lookup Tool
Retrieves equipment specifications and technical data
"""
from typing import Dict, Any


def lookup_equipment(equipment_id: str, include_manuals: bool = False) -> Dict[str, Any]:
    """
    Look up equipment in database

    Args:
        equipment_id: Equipment identification number
        include_manuals: Whether to include manual references

    Returns:
        Equipment details and specifications
    """
    # Sample equipment database (in production, this would query actual database)
    equipment_db = {
        "PUMP-001": {
            "name": "Centrifugal Pump - Main Process",
            "manufacturer": "Flowserve",
            "model": "3196 MTX",
            "specifications": {
                "flow_rate_gpm": 500,
                "head_ft": 150,
                "motor_hp": 50,
                "rpm": 1750,
                "impeller_diameter_in": 12
            },
            "installation_date": "2020-05-15",
            "last_maintenance": "2025-10-01",
            "criticality": "high",
            "location": "Building A - Process Area 1"
        },
        "COMP-002": {
            "name": "Air Compressor - Instrument Air",
            "manufacturer": "Atlas Copco",
            "model": "GA 75 VSD",
            "specifications": {
                "capacity_cfm": 425,
                "pressure_psig": 125,
                "motor_hp": 100,
                "drive_type": "VSD"
            },
            "installation_date": "2019-03-10",
            "last_maintenance": "2025-09-15",
            "criticality": "critical",
            "location": "Compressor Room - Building B"
        },
        "MOTOR-003": {
            "name": "Electric Motor - Cooling Tower Fan",
            "manufacturer": "WEG",
            "model": "W22",
            "specifications": {
                "hp": 25,
                "voltage": 480,
                "phase": 3,
                "rpm": 1800,
                "frame": "284T"
            },
            "installation_date": "2021-07-20",
            "last_maintenance": "2025-08-10",
            "criticality": "medium",
            "location": "Cooling Tower - Roof"
        }
    }

    # Manuals reference
    manuals = {
        "PUMP-001": [
            {"type": "Installation Manual", "doc_id": "DOC-PUMP-001-INST"},
            {"type": "Operation Manual", "doc_id": "DOC-PUMP-001-OPER"},
            {"type": "Maintenance Manual", "doc_id": "DOC-PUMP-001-MAINT"}
        ],
        "COMP-002": [
            {"type": "Service Manual", "doc_id": "DOC-COMP-002-SERVICE"},
            {"type": "Parts Catalog", "doc_id": "DOC-COMP-002-PARTS"}
        ],
        "MOTOR-003": [
            {"type": "Technical Manual", "doc_id": "DOC-MOTOR-003-TECH"}
        ]
    }

    equipment = equipment_db.get(equipment_id)

    if not equipment:
        return {
            "success": False,
            "error": f"Equipment {equipment_id} not found in database",
            "suggestions": list(equipment_db.keys())[:3]
        }

    result = {
        "success": True,
        "equipment_id": equipment_id,
        **equipment
    }

    if include_manuals:
        result["available_manuals"] = manuals.get(equipment_id, [])

    return result
