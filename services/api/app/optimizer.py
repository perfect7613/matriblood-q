from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any, Dict, List

from .compatibility import is_compatible
from .models import (
    Courier,
    EmergencyCase,
    OptimizationResult,
    ProcurementAction,
    ProcurementSource,
    ProductRequest,
)


@dataclass(frozen=True)
class Candidate:
    variable_name: str
    source: ProcurementSource
    request: ProductRequest
    units: int
    near_expiry: bool


def _build_candidates(case: EmergencyCase, sources: list[ProcurementSource]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for req_index, req in enumerate(case.required_products):
        for source in sources:
            for item in source.inventory:
                if not is_compatible(req, item) or item.units_available <= 0:
                    continue
                units = min(req.units, item.units_available)
                safe_name = f"x_{source.id}_{req.product_type.value}_{req_index}".replace("-", "_")
                candidates.append(
                    Candidate(
                        variable_name=safe_name,
                        source=source,
                        request=req,
                        units=units,
                        near_expiry=item.expires_at is not None,
                    )
                )
    return candidates


def _build_qiskit_metadata(candidates: list[Candidate], case: EmergencyCase) -> Dict[str, Any]:
    try:
        from qiskit_optimization import QuadraticProgram
    except Exception as exc:  # pragma: no cover - depends on optional runtime dependency
        return {
            "qiskit_available": False,
            "qiskit_error": str(exc),
            "binary_variables": [candidate.variable_name for candidate in candidates],
            "formulation": "QUBO-ready binary constrained procurement model",
        }

    program = QuadraticProgram("matriblood_procurement")
    for candidate in candidates:
        program.binary_var(candidate.variable_name)

    linear = {}
    for candidate in candidates:
        missing_reward = -80 * candidate.units
        eta_penalty = candidate.source.eta_minutes
        near_expiry_reward = -8 if candidate.near_expiry else 0
        linear[candidate.variable_name] = missing_reward + eta_penalty + near_expiry_reward
    program.minimize(linear=linear)

    for index, req in enumerate(case.required_products):
        linear_req = {
            candidate.variable_name: candidate.units
            for candidate in candidates
            if candidate.request == req
        }
        if linear_req:
            program.linear_constraint(linear=linear_req, sense=">=", rhs=req.units, name=f"fulfill_{index}")

    return {
        "qiskit_available": True,
        "program_name": program.name,
        "binary_variables": [var.name for var in program.variables],
        "constraint_count": len(program.linear_constraints),
        "objective_sense": "minimize",
        "prettyprint": program.prettyprint(),
        "formulation": "QuadraticProgram binary model; exact fallback search used for deterministic MVP solve",
    }


def _coverage_missing(case: EmergencyCase, selected: list[Candidate]) -> list[ProductRequest]:
    missing: list[ProductRequest] = []
    for req in case.required_products:
        supplied = sum(candidate.units for candidate in selected if candidate.request == req)
        if supplied < req.units:
            missing.append(req.model_copy(update={"units": req.units - supplied}))
    return missing


def _source_capacity_ok(selected: list[Candidate]) -> bool:
    usage: dict[tuple[str, str, str | None], int] = {}
    capacity: dict[tuple[str, str, str | None], int] = {}
    for candidate in selected:
        key = (candidate.source.id, candidate.request.product_type.value, candidate.request.blood_group)
        usage[key] = usage.get(key, 0) + candidate.units
        for item in candidate.source.inventory:
            if is_compatible(candidate.request, item):
                capacity[key] = max(capacity.get(key, 0), item.units_available)
    return all(usage[key] <= capacity.get(key, 0) for key in usage)


def _score(selected: list[Candidate], missing: list[ProductRequest], couriers: list[Courier]) -> float:
    if not selected:
        return 9999
    source_eta = max(candidate.source.eta_minutes for candidate in selected)
    missing_penalty = sum(item.units for item in missing) * 500
    source_count_penalty = len({candidate.source.id for candidate in selected}) * 4
    near_expiry_reward = sum(8 for candidate in selected if candidate.near_expiry)
    total_units = sum(candidate.units for candidate in selected)
    courier_capacity = sum(courier.capacity_units for courier in couriers if courier.available)
    courier_penalty = max(0, total_units - courier_capacity) * 250
    return source_eta + missing_penalty + source_count_penalty + courier_penalty - near_expiry_reward


def optimize_procurement(
    case: EmergencyCase,
    sources: list[ProcurementSource],
    couriers: list[Courier],
    force_classical_fallback: bool = False,
) -> OptimizationResult:
    candidates = _build_candidates(case, sources)
    metadata = _build_qiskit_metadata(candidates, case)

    best: list[Candidate] = []
    best_missing = case.required_products
    best_score = 99999.0
    max_subset = min(len(candidates), len(case.required_products) + 3)

    for size in range(1, max_subset + 1):
        for selected_tuple in combinations(candidates, size):
            selected = list(selected_tuple)
            if not _source_capacity_ok(selected):
                continue
            missing = _coverage_missing(case, selected)
            score = _score(selected, missing, couriers)
            if score < best_score:
                best = selected
                best_missing = missing
                best_score = score

    source_to_courier: dict[str, str] = {}
    available_couriers = [courier for courier in couriers if courier.available]
    for index, source_id in enumerate(sorted({candidate.source.id for candidate in best})):
        if index < len(available_couriers):
            source_to_courier[source_id] = available_couriers[index].id

    actions = [
        ProcurementAction(
            source_id=candidate.source.id,
            source_name=candidate.source.name,
            product_type=candidate.request.product_type,
            blood_group=candidate.request.blood_group,
            units=candidate.units,
            eta_minutes=candidate.source.eta_minutes,
            priority_order=index + 1,
            courier_id=source_to_courier.get(candidate.source.id),
            reason="Selected by Qiskit-formulated optimizer to improve complete-kit feasibility and ETA.",
        )
        for index, candidate in enumerate(sorted(best, key=lambda c: (c.source.eta_minutes, c.source.id)))
    ]
    feasible = not best_missing
    eta = max((action.eta_minutes for action in actions), default=None) if feasible else None
    metadata.update(
        {
            "solver_type": "exact_classical_fallback" if force_classical_fallback else "qiskit_formulated_exact_mvp",
            "candidate_count": len(candidates),
            "selected_variables": [candidate.variable_name for candidate in best],
        }
    )
    return OptimizationResult(
        strategy="qiskit_optimized_procurement",
        feasible=feasible,
        complete_kit_eta_minutes=eta,
        missing_items=best_missing,
        actions=actions,
        objective_value=float(best_score),
        solver_metadata=metadata,
        improvement_summary=None,
    )
