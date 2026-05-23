from app.baseline import greedy_nearest_source
from app.optimizer import optimize_procurement
from app.seed_data import demo_scenario


def test_greedy_baseline_is_incomplete_for_demo():
    scenario = demo_scenario()

    result = greedy_nearest_source(scenario.case, scenario.sources)

    assert result.strategy == "nearest_source_baseline"
    assert result.feasible is False
    assert result.missing_items


def test_optimizer_completes_demo_kit():
    scenario = demo_scenario()

    result = optimize_procurement(scenario.case, scenario.sources, scenario.couriers)

    assert result.strategy == "qiskit_optimized_procurement"
    assert result.feasible is True
    assert result.complete_kit_eta_minutes is not None
    assert result.complete_kit_eta_minutes <= scenario.case.target_minutes
    assert not result.missing_items
    assert len({action.source_id for action in result.actions}) > 1
    assert "binary_variables" in result.solver_metadata
