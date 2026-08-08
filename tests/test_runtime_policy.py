from pathlib import Path

import pytest

from ctow_guard.io import load_yaml
from ctow_guard.runtime import (
    BootstrapVerificationError,
    MissingEffectivePolicyError,
    PolicyMismatchError,
    ProfileCompilationError,
    compile_codex_launch,
    compile_codex_argv,
    verify_bootstrap_receipt,
    verify_effective_policy,
)


def _profiles() -> dict:
    return load_yaml(Path(__file__).parents[1] / "config" / "agents.yaml")["profiles"]


@pytest.mark.parametrize(
    ("role", "model", "effort"),
    [
        ("sol", "gpt-5.6-sol", "max"),
        ("terra", "gpt-5.6-terra", "high"),
        ("luna", "gpt-5.6-luna", "max"),
        ("reviewer", "gpt-5.6-luna", "max"),
    ],
)
def test_compile_codex_launch_maps_all_roles(role: str, model: str, effort: str):
    profile = _profiles()["luna" if role == "reviewer" else role]
    launch = compile_codex_launch(profile, role=role)

    assert launch.argv == [
        "codex",
        "--model",
        model,
        "-c",
        f"model_reasoning_effort={effort}",
        "--sandbox",
        "danger-full-access",
        "--ask-for-approval",
        "never",
    ]
    assert launch.requested_policy["role"] == role
    assert launch.expected_effective_policy["full_access"] is True
    assert launch.expected_effective_policy["auto_approve"] is True


def test_false_permissions_compile_to_safe_non_elevated_values():
    profile = dict(_profiles()["luna"])
    profile.update(full_access=False, auto_approve=False)
    launch = compile_codex_launch(profile, role="luna")

    assert "danger-full-access" not in launch.argv
    assert "never" not in launch.argv
    assert launch.requested_policy["sandbox"] == "workspace-write"
    assert launch.requested_policy["approval"] == "on-request"
    assert compile_codex_argv(profile, role="luna") == launch.argv


def test_fast_mode_must_be_explicitly_off_before_launch():
    profile = dict(_profiles()["terra"])
    profile["fast_mode"] = True

    with pytest.raises(ProfileCompilationError):
        compile_codex_launch(profile, role="terra")


def test_requested_policy_without_fast_mode_does_not_assume_fast_off():
    launch = compile_codex_launch(_profiles()["terra"], role="terra")
    requested = dict(launch.expected_effective_policy)
    requested.pop("fast_mode")

    with pytest.raises(ProfileCompilationError):
        verify_effective_policy(requested, {"effective_policy": launch.expected_effective_policy}, role="terra")


def test_conflicting_false_permission_is_rejected_before_launch():
    profile = dict(_profiles()["luna"])
    profile.update(full_access=False, sandbox="danger-full-access")

    with pytest.raises(ProfileCompilationError):
        compile_codex_launch(profile, role="luna")


def test_false_permissions_cannot_verify_as_elevated_effective_policy():
    profile = dict(_profiles()["luna"])
    profile.update(full_access=False, auto_approve=False)
    launch = compile_codex_launch(profile, role="luna")
    effective = dict(launch.expected_effective_policy)
    effective.update(sandbox="danger-full-access", approval="never")

    with pytest.raises(PolicyMismatchError):
        verify_effective_policy(launch, {"effective_policy": effective}, role="luna")


def test_missing_effective_policy_fails_closed():
    launch = compile_codex_launch(_profiles()["terra"], role="terra")

    with pytest.raises(MissingEffectivePolicyError) as raised:
        verify_effective_policy(launch, {"run_id": "run-1"}, role="terra")

    assert raised.value.code == "effective_policy_missing"
    assert set(raised.value.details["missing_fields"]) == {
        "model",
        "reasoning_effort",
        "fast_mode",
        "sandbox",
        "approval",
    }


def test_boolean_permission_receipt_cannot_stand_in_for_concrete_policy_fields():
    launch = compile_codex_launch(_profiles()["terra"], role="terra")
    effective = {
        "model": "gpt-5.6-terra",
        "reasoning_effort": "high",
        "full_access": True,
        "auto_approve": True,
    }

    with pytest.raises(MissingEffectivePolicyError) as raised:
        verify_effective_policy(launch, {"effective_policy": effective}, role="terra")

    assert set(raised.value.details["missing_fields"]) == {"fast_mode", "sandbox", "approval"}


def test_mismatched_effective_policy_fails_closed():
    launch = compile_codex_launch(_profiles()["terra"], role="terra")
    effective = dict(launch.expected_effective_policy)
    effective["sandbox"] = "workspace-write"
    effective["full_access"] = False

    with pytest.raises(PolicyMismatchError) as raised:
        verify_effective_policy(launch, {"effective_policy": effective}, role="terra")

    assert raised.value.code == "effective_policy_mismatch"
    assert "sandbox" in raised.value.details["mismatches"]


def test_fast_on_effective_receipt_fails_closed():
    launch = compile_codex_launch(_profiles()["terra"], role="terra")
    effective = dict(launch.expected_effective_policy)
    effective["fast_mode"] = True

    with pytest.raises(PolicyMismatchError) as raised:
        verify_effective_policy(launch, {"effective_policy": effective}, role="terra")

    assert "fast_mode" in raised.value.details["mismatches"]


def test_bootstrap_receipt_requires_verifiable_effective_values():
    launch = compile_codex_launch(_profiles()["terra"], role="terra")
    effective = {"effective_policy": launch.expected_effective_policy}

    verified = verify_bootstrap_receipt(launch, effective, role="terra")

    assert verified["verified"] is True
    assert verified["bootstrap_verified"] is True

    with pytest.raises(BootstrapVerificationError):
        verify_bootstrap_receipt(launch, None, role="terra")

    with pytest.raises(BootstrapVerificationError) as raised:
        verify_bootstrap_receipt(launch, ["not", "a", "receipt"], role="terra")
    assert raised.value.code == "bootstrap_verification_failed"


def test_effective_receipt_accepts_nested_permissions_and_codex_effort_setting():
    launch = compile_codex_launch(_profiles()["terra"], role="terra")
    receipt = {
        "effective": {
            "model": "gpt-5.6-terra",
            "model_reasoning_effort": 'model_reasoning_effort="high"',
            "fast_mode": False,
            "permissions": {
                "sandbox": "danger-full-access",
                "approval_policy": "never",
            },
        }
    }

    assert verify_effective_policy(launch, receipt, role="terra")["verified"] is True


def test_effective_receipt_prefers_orca_launch_effective_over_requested():
    launch = compile_codex_launch(_profiles()["terra"], role="terra")
    receipt = {
        "ok": True,
        "result": {
            "launch": {
                "requested": {"model": "wrong-requested-model"},
                "effective": {
                    "model": "gpt-5.6-terra",
                    "effort": "high",
                    "fast_mode": False,
                    "sandbox": "danger-full-access",
                    "approval": "never",
                },
            }
        },
    }

    assert verify_effective_policy(launch, receipt, role="terra")["verified"] is True


def test_effective_receipt_does_not_merge_requested_or_sibling_policy_fields():
    launch = compile_codex_launch(_profiles()["terra"], role="terra")
    receipt = {
        "requested": dict(launch.expected_effective_policy),
        "effective": {
            "model": "gpt-5.6-terra",
            "reasoning_effort": "high",
            "fast_mode": False,
        },
        "permissions": {
            "sandbox": "danger-full-access",
            "approval": "never",
        },
    }

    with pytest.raises(MissingEffectivePolicyError) as raised:
        verify_effective_policy(launch, receipt, role="terra")

    assert set(raised.value.details["missing_fields"]) == {"sandbox", "approval"}
