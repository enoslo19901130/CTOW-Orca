from __future__ import annotations

import re
from typing import Literal
from pydantic import BaseModel, Field, model_validator

Risk = Literal["low", "medium", "high", "critical"]
ExecutionProfile = Literal["SMALL", "MEDIUM", "FULL", "SWARM"]
Severity = Literal["low", "medium", "high", "critical"]
DecisionAction = Literal["DECIDE", "REQUEST_TARGETED_EVIDENCE", "REVISE_PLAN", "ESCALATE_HUMAN"]

FINGERPRINT_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+){2,7}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
QUESTION_KEY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+){1,7}$")


def _valid_question_key(value: str) -> str:
    if len(value) < 5 or len(value) > 96 or not QUESTION_KEY_RE.fullmatch(value):
        raise ValueError("decision_question_key must be a stable lowercase semantic slug")
    return value


def _valid_fingerprint(value: str) -> str:
    if len(value) < 8 or len(value) > 96 or not FINGERPRINT_RE.fullmatch(value):
        raise ValueError(
            "issue_fingerprint must be 8..96 chars, lowercase slug form, and contain at least "
            "three semantic segments (domain-conflict-stable-subject)"
        )
    return value


class WorkPackage(BaseModel):
    id: str
    objective: str
    risk: Risk
    recommended_workers: int = Field(ge=1, le=3)
    dependencies: list[str] = Field(default_factory=list)
    acceptance: list[str] = Field(min_length=1)
    independent_review_required: bool = False

    @model_validator(mode="after")
    def enforce_risk_review(self):
        if self.risk in {"high", "critical"} and not self.independent_review_required:
            raise ValueError(f"{self.id}: high/critical risk requires independent review")
        return self


class Plan(BaseModel):
    plan_id: str
    revision: int = Field(ge=1)
    goal: str
    execution_profile: ExecutionProfile
    constraints: list[str] = Field(default_factory=list)
    work_packages: list[WorkPackage] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_wp_ids_and_dependencies(self):
        ids = [wp.id for wp in self.work_packages]
        if len(ids) != len(set(ids)):
            raise ValueError("work package ids must be unique")
        known = set(ids)
        for wp in self.work_packages:
            unknown = set(wp.dependencies) - known
            if unknown:
                raise ValueError(f"{wp.id} has unknown dependencies: {sorted(unknown)}")
            if wp.id in wp.dependencies:
                raise ValueError(f"{wp.id} cannot depend on itself")
        return self


class TaskContract(BaseModel):
    task_id: str
    work_package_id: str
    task_type: Literal["execution", "review", "targeted_validation", "swarm_investigation"] = "execution"
    objective: str
    risk: Risk
    mode: Literal["research", "implement", "test", "review"]
    scope: list[str] = Field(min_length=1)
    write_scope: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    acceptance: list[str] = Field(min_length=1)
    evidence_required: list[str] = Field(default_factory=list)
    independent_review_required: bool = False
    review_of_task_id: str | None = None
    parent_task_id: str | None = None

    @model_validator(mode="after")
    def validate_task_contract(self):
        if self.mode in {"research", "review"} and self.write_scope:
            raise ValueError(f"{self.mode} task must not declare write_scope")
        if self.risk in {"high", "critical"} and self.task_type == "execution" and not self.independent_review_required:
            raise ValueError("high/critical execution task requires independent review")
        if self.task_type == "review":
            if self.mode != "review":
                raise ValueError("review task_type requires mode=review")
            if not self.review_of_task_id:
                raise ValueError("review task requires review_of_task_id")
        elif self.review_of_task_id:
            raise ValueError("review_of_task_id is only valid for review tasks")
        if self.task_type == "targeted_validation" and self.mode not in {"research", "test"}:
            raise ValueError("targeted_validation must use research or test mode")
        if self.task_type == "swarm_investigation" and self.mode != "research":
            raise ValueError("swarm_investigation must use research mode")
        return self


class WorkerReport(BaseModel):
    task_id: str
    dispatch_id: str
    agent_id: str
    session_id: str
    outcome: Literal["succeeded", "failed", "blocked"]
    summary: str
    evidence: list[str] = Field(default_factory=list)
    files_modified: list[str] = Field(default_factory=list)
    tests: list[str] = Field(default_factory=list)
    remaining_risks: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    severity: Severity
    summary: str
    evidence: list[str] = Field(min_length=1)
    recommendation: str | None = None


class ReviewReport(BaseModel):
    review_id: str
    task_id: str
    author_agent: str
    reviewer_agent: str
    author_session: str
    reviewer_session: str
    author_dispatch: str
    reviewer_dispatch: str
    verdict: Literal["PASS", "CONDITIONAL_PASS", "FAIL"]
    findings: list[Finding] = Field(default_factory=list)

    @model_validator(mode="after")
    def reviewer_must_be_independent(self):
        if self.author_agent == self.reviewer_agent:
            raise ValueError("independent reviewer must use a different agent identity")
        if self.author_session == self.reviewer_session:
            raise ValueError("independent reviewer must use a different session")
        if self.author_dispatch == self.reviewer_dispatch:
            raise ValueError("independent reviewer must use a different dispatch")
        return self


class EvidenceDelta(BaseModel):
    kind: Literal[
        "changed_observable",
        "new_failure_mode",
        "invalidated_hypothesis",
        "changed_decision_space",
        "acceptance_failure",
        "targeted_validation_result",
        "new_constraint",
        "new_reproduction_condition",
    ]
    summary: str
    evidence: list[str] = Field(min_length=1)
    decision_impact: str


class IssueIdentityRecord(BaseModel):
    canonical_fingerprint: str
    domain: str
    conflict_class: str
    stable_subject: str
    created_by: Literal["terra"] = "terra"
    aliases: list[str] = Field(default_factory=list)
    prior_fingerprint: str | None = None
    identity_change_reason: str | None = None
    material_identity_difference: str | None = None
    status: Literal["active", "superseded"] = "active"

    @model_validator(mode="after")
    def validate_identity(self):
        for value, label in [
            (self.domain, "domain"),
            (self.conflict_class, "conflict_class"),
            (self.stable_subject, "stable_subject"),
        ]:
            if not SLUG_RE.fullmatch(value):
                raise ValueError(f"{label} must be a lowercase slug")
        expected = f"{self.domain}-{self.conflict_class}-{self.stable_subject}"
        _valid_fingerprint(self.canonical_fingerprint)
        if self.canonical_fingerprint != expected:
            raise ValueError(f"canonical_fingerprint must equal semantic identity {expected}")
        if self.prior_fingerprint:
            _valid_fingerprint(self.prior_fingerprint)
            if not self.identity_change_reason or not self.material_identity_difference:
                raise ValueError(
                    "changing canonical identity requires identity_change_reason and material_identity_difference"
                )
        elif self.identity_change_reason or self.material_identity_difference:
            raise ValueError("identity change metadata requires prior_fingerprint")
        return self


class EscalationReport(BaseModel):
    escalation_id: str
    issue_fingerprint: str
    fingerprint_status: Literal["provisional", "canonical"] = "provisional"
    canonicalized_by: Literal["terra"] | None = None
    previous_fingerprint: str | None = None
    identity_change_reason: str | None = None
    material_identity_difference: str | None = None
    cycle_count: int = Field(default=1, ge=1)
    from_role: Literal["luna", "terra", "sol"]
    to_role: Literal["terra", "sol", "human"]
    severity: Severity
    blocking: bool
    summary: str
    evidence: list[str] = Field(min_length=1)
    attempted_actions: list[str] = Field(default_factory=list)
    failed_hypotheses: list[str] = Field(default_factory=list)
    previous_decision_id: str | None = None
    previous_escalation_id: str | None = None
    material_evidence_delta: list[EvidenceDelta] = Field(default_factory=list)
    decision_required: str
    decision_question_key: str
    options: list[str] = Field(min_length=1)
    recommended_option: str | None = None

    @model_validator(mode="after")
    def validate_escalation(self):
        _valid_fingerprint(self.issue_fingerprint)
        _valid_question_key(self.decision_question_key)
        valid = {("luna", "terra"), ("terra", "sol"), ("sol", "human")}
        if (self.from_role, self.to_role) not in valid:
            raise ValueError("escalation must move exactly one authority level upward")
        if self.to_role in {"sol", "human"}:
            if self.fingerprint_status != "canonical" or self.canonicalized_by != "terra":
                raise ValueError("Terra must canonicalize fingerprint before escalation reaches Sol/Human")
        if self.fingerprint_status == "canonical" and self.canonicalized_by != "terra":
            raise ValueError("canonical fingerprint authority belongs to Terra")
        if self.previous_decision_id and not self.material_evidence_delta:
            raise ValueError("reopening a decided issue requires material evidence delta")
        if self.cycle_count > 1 and not self.previous_escalation_id:
            raise ValueError("cycle_count > 1 requires previous_escalation_id")
        if self.previous_fingerprint:
            _valid_fingerprint(self.previous_fingerprint)
            if self.previous_fingerprint != self.issue_fingerprint:
                if not self.identity_change_reason or not self.material_identity_difference:
                    raise ValueError(
                        "fingerprint change requires identity_change_reason and material_identity_difference"
                    )
        elif self.identity_change_reason or self.material_identity_difference:
            raise ValueError("identity change metadata requires previous_fingerprint")
        return self


class TargetedValidation(BaseModel):
    hypothesis: str
    method: str
    success_criterion: str
    failure_criterion: str
    expected_decision_impact: str
    max_attempts: int = Field(default=1, ge=1, le=1)


class DecisionRecord(BaseModel):
    decision_id: str
    issue_fingerprint: str
    source_escalation_id: str
    cycle_count: int = Field(default=1, ge=1)
    previous_decision_id: str | None = None
    actor: Literal["sol", "human"]
    action: DecisionAction
    decision: str
    decision_question: str
    decision_question_key: str
    rationale: str
    evidence_basis: list[str] = Field(min_length=1)
    new_information: list[EvidenceDelta] = Field(default_factory=list)
    unchanged_information: list[str] = Field(default_factory=list)
    targeted_validation: TargetedValidation | None = None
    material_evidence_delta_required_to_reopen: bool = True

    @model_validator(mode="after")
    def validate_decision(self):
        _valid_fingerprint(self.issue_fingerprint)
        _valid_question_key(self.decision_question_key)
        if self.action == "REQUEST_TARGETED_EVIDENCE" and self.targeted_validation is None:
            raise ValueError("REQUEST_TARGETED_EVIDENCE requires one bounded targeted_validation")
        if self.action != "REQUEST_TARGETED_EVIDENCE" and self.targeted_validation is not None:
            raise ValueError("targeted_validation is only valid for REQUEST_TARGETED_EVIDENCE")
        if self.action == "ESCALATE_HUMAN" and self.actor != "sol":
            raise ValueError("only Sol escalates an AI decision to Human")
        if self.cycle_count > 1 and not self.previous_decision_id:
            raise ValueError("decision cycle_count > 1 requires previous_decision_id")
        return self


class DecisionProgressRecord(BaseModel):
    progress_id: str
    issue_fingerprint: str
    cycle_count: int = Field(ge=1)
    current_escalation_id: str
    previous_escalation_id: str | None = None
    previous_decision_id: str | None = None
    decision_question: str
    decision_question_key: str
    previous_decision_question: str | None = None
    previous_decision_question_key: str | None = None
    unchanged_facts: list[str] = Field(default_factory=list)
    material_evidence_delta: list[EvidenceDelta] = Field(default_factory=list)
    stagnation_detected: bool = False
    allowed_next_actions: list[DecisionAction] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_progress(self):
        _valid_fingerprint(self.issue_fingerprint)
        _valid_question_key(self.decision_question_key)
        if self.previous_decision_question_key:
            _valid_question_key(self.previous_decision_question_key)
        if self.cycle_count > 1 and not self.previous_escalation_id:
            raise ValueError("cycle_count > 1 requires previous_escalation_id")
        same_question = (
            self.previous_decision_question_key is not None
            and self.previous_decision_question_key == self.decision_question_key
        )
        should_stagnate = self.cycle_count >= 2 and same_question and not self.material_evidence_delta
        if should_stagnate and not self.stagnation_detected:
            raise ValueError("same question + no material evidence delta at cycle >=2 must mark stagnation")
        if self.stagnation_detected:
            allowed = {"DECIDE", "REVISE_PLAN", "ESCALATE_HUMAN"}
            if not set(self.allowed_next_actions).issubset(allowed):
                raise ValueError("stagnation forbids REQUEST_TARGETED_EVIDENCE and other revalidation")
        return self


class BreakGlassRecord(BaseModel):
    audit_id: str
    actor: Literal["sol", "terra"]
    reason: Literal[
        "critical_production_fix",
        "security_containment",
        "worker_fleet_unavailable",
        "blocking_integration_repair",
    ]
    scope: list[str] = Field(min_length=1)
    files_modified: list[str] = Field(default_factory=list)
    normal_authority_bypassed: str
    validation_performed: list[str] = Field(min_length=1)
    post_review_required: bool = True

    @model_validator(mode="after")
    def post_review_is_mandatory(self):
        if not self.post_review_required:
            raise ValueError("break-glass always requires post-action review")
        return self


class HumanDecisionRecord(BaseModel):
    decision_id: str
    requested_by: Literal["sol"]
    question: str
    options: list[str] = Field(min_length=2)
    recommendation: str | None = None
    blocking: bool = True
    decision: str | None = None
    status: Literal["pending", "resolved"]

    @model_validator(mode="after")
    def resolved_requires_decision(self):
        if self.status == "resolved" and not self.decision:
            raise ValueError("resolved human decision requires decision")
        return self
