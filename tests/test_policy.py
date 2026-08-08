import pytest
from ctow_guard.policy import can_delegate, validate_worker_count, validate_reasoning


def test_hierarchy():
    assert can_delegate("human", "sol")
    assert can_delegate("sol", "terra")
    assert can_delegate("terra", "luna")
    assert not can_delegate("sol", "luna")
    assert not can_delegate("luna", "luna")


def test_execution_capacity():
    validate_worker_count("FULL", 3)
    with pytest.raises(ValueError):
        validate_worker_count("SMALL", 2)


def test_reasoning_profiles_are_strict():
    validate_reasoning("sol", "max")
    validate_reasoning("terra", "high")
    validate_reasoning("luna", "max")
    with pytest.raises(ValueError):
        validate_reasoning("sol", "xhigh")
