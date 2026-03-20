"""
Equipment Maintenance Scheduler Workflow
Creates optimized maintenance schedules
"""
import asyncio
from typing import Dict, List, Any
from datetime import datetime, timedelta


async def create_schedule(equipment_list: List[Dict[str, Any]], time_horizon_days: int = 30) -> Dict[str, Any]:
    """
    Create maintenance schedule for equipment list

    Args:
        equipment_list: List of equipment with maintenance requirements
        time_horizon_days: Planning horizon in days

    Returns:
        Optimized maintenance schedule
    """
    await asyncio.sleep(0.5)

    # Define maintenance frequencies (in days)
    maintenance_frequencies = {
        "critical": 7,
        "high": 14,
        "medium": 30,
        "low": 90
    }

    # Generate schedule
    schedule = []
    start_date = datetime.now()

    for equipment in equipment_list:
        equipment_id = equipment.get("id", "UNKNOWN")
        equipment_name = equipment.get("name", "Unknown Equipment")
        criticality = equipment.get("criticality", "medium").lower()
        last_maintenance = equipment.get("last_maintenance_date")

        # Determine frequency
        frequency_days = maintenance_frequencies.get(criticality, 30)

        # Calculate next maintenance date
        if last_maintenance:
            try:
                last_date = datetime.fromisoformat(last_maintenance)
                next_date = last_date + timedelta(days=frequency_days)
            except:
                next_date = start_date + timedelta(days=frequency_days)
        else:
            # No previous maintenance - schedule based on criticality
            if criticality == "critical":
                next_date = start_date + timedelta(days=2)
            elif criticality == "high":
                next_date = start_date + timedelta(days=5)
            else:
                next_date = start_date + timedelta(days=10)

        # Only include if within planning horizon
        if next_date <= start_date + timedelta(days=time_horizon_days):
            schedule.append({
                "equipment_id": equipment_id,
                "equipment_name": equipment_name,
                "criticality": criticality,
                "scheduled_date": next_date.isoformat(),
                "maintenance_type": "preventive",
                "estimated_duration_hours": {
                    "critical": 4.0,
                    "high": 3.0,
                    "medium": 2.0,
                    "low": 1.0
                }.get(criticality, 2.0),
                "priority_score": {
                    "critical": 100,
                    "high": 75,
                    "medium": 50,
                    "low": 25
                }.get(criticality, 50)
            })

    # Sort by scheduled date and priority
    schedule.sort(key=lambda x: (datetime.fromisoformat(x["scheduled_date"]), -x["priority_score"]))

    # Resource allocation recommendations
    resource_allocation = {
        "total_maintenance_events": len(schedule),
        "estimated_total_hours": sum(item["estimated_duration_hours"] for item in schedule),
        "recommended_team_size": max(2, len(schedule) // 5),
        "peak_days": []
    }

    # Identify peak days
    day_counts = {}
    for item in schedule:
        date_str = datetime.fromisoformat(item["scheduled_date"]).strftime("%Y-%m-%d")
        day_counts[date_str] = day_counts.get(date_str, 0) + 1

    peak_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    resource_allocation["peak_days"] = [
        {"date": date, "events": count} for date, count in peak_days
    ]

    return {
        "success": True,
        "planning_horizon_days": time_horizon_days,
        "schedule_start_date": start_date.isoformat(),
        "schedule_end_date": (start_date + timedelta(days=time_horizon_days)).isoformat(),
        "maintenance_schedule": schedule,
        "resource_allocation": resource_allocation,
        "summary": {
            "total_equipment": len(equipment_list),
            "scheduled_maintenance": len(schedule),
            "critical_items": len([s for s in schedule if s["criticality"] == "critical"]),
            "high_priority_items": len([s for s in schedule if s["criticality"] == "high"])
        }
    }
