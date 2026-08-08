from ctow_guard.io import load_yaml
from ctow_guard.models import Plan


def test_demo_plan_validates():
    plan = Plan.model_validate(load_yaml("examples/PLAN-DEMO.yaml"))
    assert plan.execution_profile == "FULL"
    assert any(wp.independent_review_required for wp in plan.work_packages)
