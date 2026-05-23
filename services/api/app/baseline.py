from __future__ import annotations

from .compatibility import is_compatible
from .models import EmergencyCase, OptimizationResult, ProcurementAction, ProcurementSource, ProductRequest


def _missing_after_actions(case: EmergencyCase, actions: list[ProcurementAction]) -> list[ProductRequest]:
    missing: list[ProductRequest] = []
    for req in case.required_products:
        supplied = sum(
            action.units
            for action in actions
            if action.product_type == req.product_type
            and (req.blood_group is None or action.blood_group == req.blood_group)
        )
        if supplied < req.units:
            missing.append(req.model_copy(update={"units": req.units - supplied}))
    return missing


def greedy_nearest_source(case: EmergencyCase, sources: list[ProcurementSource]) -> OptimizationResult:
    """Naive baseline: try the nearest source first and do not split across sources."""
    nearest = min(sources, key=lambda source: source.eta_minutes)
    actions: list[ProcurementAction] = []
    priority = 1

    for req in case.required_products:
        remaining = req.units
        for item in nearest.inventory:
            if remaining <= 0:
                break
            if not is_compatible(req, item):
                continue
            units = min(remaining, item.units_available)
            if units <= 0:
                continue
            actions.append(
                ProcurementAction(
                    source_id=nearest.id,
                    source_name=nearest.name,
                    product_type=req.product_type,
                    blood_group=item.blood_group or req.blood_group,
                    units=units,
                    eta_minutes=nearest.eta_minutes,
                    priority_order=priority,
                    reason="Nearest-source baseline selected the closest tied-up source.",
                )
            )
            priority += 1
            remaining -= units

    missing = _missing_after_actions(case, actions)
    feasible = not missing
    eta = nearest.eta_minutes if feasible and actions else None
    objective = (eta or 999) + len(missing) * 100
    return OptimizationResult(
        strategy="nearest_source_baseline",
        feasible=feasible,
        complete_kit_eta_minutes=eta,
        missing_items=missing,
        actions=actions,
        objective_value=float(objective),
        solver_metadata={"source_count": len(sources), "baseline_rule": "single nearest source, no splitting"},
        improvement_summary=None,
    )
