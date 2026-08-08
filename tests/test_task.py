import pytest
from pydantic import ValidationError
from ctow_guard.io import load_yaml
from ctow_guard.models import TaskContract


def test_demo_task_validates():
    TaskContract.model_validate(load_yaml("examples/TASK-WP001.yaml"))


def test_review_task_requires_review_target():
    data = load_yaml("examples/TASK-REVIEW-WP002.yaml")
    data["review_of_task_id"] = None
    with pytest.raises(ValidationError):
        TaskContract.model_validate(data)


def test_high_risk_execution_requires_review():
    data = load_yaml("examples/TASK-WP001.yaml")
    data["risk"] = "high"
    data["independent_review_required"] = False
    with pytest.raises(ValidationError):
        TaskContract.model_validate(data)
