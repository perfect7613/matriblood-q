from __future__ import annotations

import os
from typing import Any, Optional

from supabase import Client, create_client

from .models import CompareResponse, EmergencyCase, ScenarioState


def get_supabase() -> Optional[Client]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def persist_case(client: Client, case: EmergencyCase) -> None:
    client.table("emergency_cases").upsert(
        {
            "id": case.id,
            "transcript": case.transcript,
            "case_type": case.case_type,
            "patient_status": case.patient_status,
            "target_minutes": case.target_minutes,
            "urgency_score": case.urgency_score,
            "required_products": [item.model_dump(mode="json") for item in case.required_products],
            "missing_fields": case.missing_fields,
            "parser_confidence": case.parser_confidence,
            "status": "parsed",
        }
    ).execute()


def persist_scenario(client: Client, scenario: ScenarioState) -> None:
    for source in scenario.sources:
        client.table("blood_banks").upsert(
            {
                "id": source.id,
                "name": source.name,
                "source_type": source.source_type.value,
                "eta_minutes": source.eta_minutes,
                "phone": source.phone,
                "is_tie_up_partner": source.is_tie_up_partner,
            }
        ).execute()
        client.table("blood_inventory").delete().eq("source_id", source.id).execute()
        for item in source.inventory:
            client.table("blood_inventory").insert(
                {
                    "source_id": source.id,
                    "product_type": item.product_type.value,
                    "blood_group": item.blood_group,
                    "units_available": item.units_available,
                    "expires_at": item.expires_at.isoformat() if item.expires_at else None,
                    "notes": item.notes,
                }
            ).execute()

    for courier in scenario.couriers:
        client.table("couriers").upsert(
            {
                "id": courier.id,
                "name": courier.name,
                "capacity_units": courier.capacity_units,
                "available": courier.available,
            }
        ).execute()

    persist_case(client, scenario.case)


def persist_comparison(client: Client, comparison: CompareResponse) -> dict[str, Any]:
    payload = {
        "emergency_case_id": comparison.case.id,
        "baseline_result_json": comparison.baseline.model_dump(mode="json"),
        "qiskit_result_json": comparison.optimized.model_dump(mode="json"),
        "solver_type": str(comparison.optimized.solver_metadata.get("solver_type", "unknown")),
        "objective_value": comparison.optimized.objective_value,
        "improvement_summary": comparison.optimized.improvement_summary,
    }
    result = client.table("optimization_runs").insert(payload).execute()
    row = result.data[0]
    run_id = row["id"]
    for action in comparison.optimized.actions:
        client.table("procurement_actions").insert(
            {
                "optimization_run_id": run_id,
                "source_id": action.source_id,
                "product_type": action.product_type.value,
                "blood_group": action.blood_group,
                "units_requested": action.units,
                "eta_minutes": action.eta_minutes,
                "priority_order": action.priority_order,
                "courier_id": action.courier_id,
                "reason": action.reason,
                "action_status": "pending",
            }
        ).execute()
    return row
