"""
Maintenance Cost Estimator Tool
Estimates maintenance costs including labor, parts, and downtime
"""
from typing import Dict, Any


def estimate_cost(maintenance_type: str, equipment_id: str, duration_hours: float) -> Dict[str, Any]:
    """
    Estimate total maintenance cost

    Args:
        maintenance_type: Type of maintenance (routine, preventive, corrective)
        equipment_id: Equipment ID
        duration_hours: Estimated duration in hours

    Returns:
        Cost breakdown and total estimate
    """
    # Labor rates (per hour)
    labor_rates = {
        "technician": 75.0,
        "specialist": 125.0,
        "engineer": 150.0
    }

    # Determine labor composition based on maintenance type
    labor_composition = {
        "routine": {"technician": 1, "specialist": 0, "engineer": 0},
        "preventive": {"technician": 2, "specialist": 1, "engineer": 0},
        "corrective": {"technician": 2, "specialist": 1, "engineer": 1}
    }

    # Parts multipliers based on maintenance type
    parts_multipliers = {
        "routine": 50,  # Minimal parts - consumables only
        "preventive": 500,  # Standard replacement parts
        "corrective": 2500  # Major components may be needed
    }

    # Downtime cost (lost production per hour)
    equipment_downtime_rates = {
        "PUMP-001": 5000,  # Critical process pump
        "COMP-002": 8000,  # Instrument air - plant-wide impact
        "MOTOR-003": 2000,  # Cooling tower - moderate impact
        "default": 3000
    }

    composition = labor_composition.get(maintenance_type, labor_composition["preventive"])

    # Calculate labor cost
    labor_cost = 0
    labor_breakdown = []

    for role, count in composition.items():
        if count > 0:
            cost = count * labor_rates[role] * duration_hours
            labor_cost += cost
            labor_breakdown.append({
                "role": role,
                "count": count,
                "rate_per_hour": labor_rates[role],
                "hours": duration_hours,
                "total": cost
            })

    # Estimate parts cost
    parts_cost_base = parts_multipliers.get(maintenance_type, parts_multipliers["preventive"])
    # Add variability based on duration
    parts_cost = parts_cost_base * (1 + (duration_hours / 10))

    # Calculate downtime cost
    downtime_rate = equipment_downtime_rates.get(equipment_id, equipment_downtime_rates["default"])
    downtime_cost = downtime_rate * duration_hours

    # Overhead and miscellaneous (15% of labor + parts)
    overhead_cost = (labor_cost + parts_cost) * 0.15

    # Total cost
    total_cost = labor_cost + parts_cost + downtime_cost + overhead_cost

    # Cost confidence level
    confidence = {
        "routine": 0.90,
        "preventive": 0.75,
        "corrective": 0.50
    }.get(maintenance_type, 0.70)

    # Generate cost range
    cost_range = {
        "low": total_cost * (1 - (1 - confidence)),
        "expected": total_cost,
        "high": total_cost * (1 + (1 - confidence))
    }

    return {
        "success": True,
        "equipment_id": equipment_id,
        "maintenance_type": maintenance_type,
        "duration_hours": duration_hours,
        "cost_breakdown": {
            "labor": {
                "total": round(labor_cost, 2),
                "breakdown": labor_breakdown
            },
            "parts": round(parts_cost, 2),
            "downtime": round(downtime_cost, 2),
            "overhead": round(overhead_cost, 2)
        },
        "total_cost": round(total_cost, 2),
        "cost_range": {
            "low": round(cost_range["low"], 2),
            "expected": round(cost_range["expected"], 2),
            "high": round(cost_range["high"], 2)
        },
        "confidence_level": f"{int(confidence * 100)}%",
        "currency": "USD",
        "notes": [
            "Costs are estimates and may vary based on actual conditions",
            "Parts costs assume standard replacements",
            "Downtime costs based on historical production loss data",
            "Does not include emergency overtime premiums"
        ]
    }
