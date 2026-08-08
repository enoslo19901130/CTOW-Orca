import pytest
from pydantic import ValidationError
from ctow_guard.io import load_yaml
from ctow_guard.models import (
    DecisionProgressRecord,
    DecisionRecord,
    EscalationReport,
    IssueIdentityRecord,
)
from ctow_guard.policy import validate_revalidation_budget


def test_demo_governance_chain_validates():
    IssueIdentityRecord.model_validate(load_yaml("examples/ISSUE-IDENTITY-DEMO.yaml"))
    EscalationReport.model_validate(load_yaml("examples/ESCALATION-DEMO.yaml"))
    DecisionRecord.model_validate(load_yaml("examples/DECISION-DEMO.yaml"))
    DecisionProgressRecord.model_validate(load_yaml("examples/DECISION-PROGRESS-DEMO.yaml"))
    DecisionProgressRecord.model_validate(load_yaml("examples/DECISION-PROGRESS-STAGNATION-DEMO.yaml"))


def test_terra_must_canonicalize_before_sol():
    data = load_yaml("examples/ESCALATION-DEMO.yaml")
    data["fingerprint_status"] = "provisional"
    data["canonicalized_by"] = None
    with pytest.raises(ValidationError):
        EscalationReport.model_validate(data)


def test_reopen_requires_material_evidence_delta():
    data = load_yaml("examples/ESCALATION-DEMO.yaml")
    data["previous_decision_id"] = "DEC-OLD"
    data["material_evidence_delta"] = []
    with pytest.raises(ValidationError):
        EscalationReport.model_validate(data)


def test_weak_evidence_kind_is_not_schema_valid():
    data = load_yaml("examples/ESCALATION-DEMO.yaml")
    data["material_evidence_delta"][0]["kind"] = "another_worker_agrees"
    with pytest.raises(ValidationError):
        EscalationReport.model_validate(data)


def test_fingerprint_change_requires_material_identity_explanation():
    data = load_yaml("examples/ESCALATION-DEMO.yaml")
    data["previous_fingerprint"] = "auth-contract-sessionstate"
    with pytest.raises(ValidationError):
        EscalationReport.model_validate(data)


def test_issue_identity_semantics_must_match_fingerprint():
    data = load_yaml("examples/ISSUE-IDENTITY-DEMO.yaml")
    data["stable_subject"] = "sessionstate"
    with pytest.raises(ValidationError):
        IssueIdentityRecord.model_validate(data)


def test_targeted_validation_is_bounded_to_one_attempt():
    data = load_yaml("examples/DECISION-DEMO.yaml")
    data["targeted_validation"]["max_attempts"] = 2
    with pytest.raises(ValidationError):
        DecisionRecord.model_validate(data)


def test_stagnation_must_be_marked_when_same_question_no_delta_cycle_two():
    data = load_yaml("examples/DECISION-PROGRESS-STAGNATION-DEMO.yaml")
    data["stagnation_detected"] = False
    with pytest.raises(ValidationError):
        DecisionProgressRecord.model_validate(data)


def test_stagnation_forbids_more_targeted_validation():
    data = load_yaml("examples/DECISION-PROGRESS-STAGNATION-DEMO.yaml")
    data["allowed_next_actions"].append("REQUEST_TARGETED_EVIDENCE")
    with pytest.raises(ValidationError):
        DecisionProgressRecord.model_validate(data)


def test_cycle_two_requires_previous_escalation():
    data = load_yaml("examples/DECISION-PROGRESS-DEMO.yaml")
    data["previous_escalation_id"] = None
    with pytest.raises(ValidationError):
        DecisionProgressRecord.model_validate(data)


def test_sol_same_issue_revalidation_budget_is_one():
    validate_revalidation_budget(1)
    with pytest.raises(ValueError):
        validate_revalidation_budget(2)


def test_rephrased_question_cannot_evade_stagnation_when_key_is_same():
    data = load_yaml("examples/DECISION-PROGRESS-STAGNATION-DEMO.yaml")
    data["previous_decision_question"] = "Do we need to redesign SessionManager ownership now?"
    data["decision_question"] = "Should SessionManager ownership be revised?"
    data["stagnation_detected"] = False
    # Text changed, but Terra's stable semantic question key is unchanged.
    with pytest.raises(ValidationError):
        DecisionProgressRecord.model_validate(data)
