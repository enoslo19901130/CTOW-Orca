from __future__ import annotations

ALLOWED_DECISION_CHILD = {
    "human": "sol",
    "sol": "terra",
    "terra": "luna",
    "luna": None,
}

PROFILE_CAPACITY = {
    "SMALL": 1,
    "MEDIUM": 2,
    "FULL": 3,
    "SWARM": 3,
}

EXPECTED_REASONING = {
    "sol": "max",
    "terra": "high",
    "luna": "max",
}

PROGRESS_ACTIONS = {"DECIDE", "REQUEST_TARGETED_EVIDENCE", "REVISE_PLAN", "ESCALATE_HUMAN"}
STAGNATION_ACTIONS = {"DECIDE", "REVISE_PLAN", "ESCALATE_HUMAN"}


def can_delegate(parent: str, child: str) -> bool:
    return ALLOWED_DECISION_CHILD.get(parent) == child


def validate_worker_count(profile: str, count: int) -> None:
    limit = PROFILE_CAPACITY[profile]
    if count < 1 or count > limit:
        raise ValueError(f"{profile} allows 1..{limit} Luna workers, got {count}")


def validate_reasoning(role: str, effective_effort: str) -> None:
    expected = EXPECTED_REASONING[role]
    if effective_effort != expected:
        raise ValueError(f"{role} requires reasoning={expected}, got {effective_effort}")


def validate_revalidation_budget(cycles: int, limit: int = 1) -> None:
    if cycles > limit:
        raise ValueError(
            f"same issue may be revalidated at Sol at most {limit} time(s) without a new material evidence path"
        )


def validate_progress_action(action: str, *, stagnating: bool = False) -> None:
    allowed = STAGNATION_ACTIONS if stagnating else PROGRESS_ACTIONS
    if action not in allowed:
        raise ValueError(f"action {action!r} is not allowed in this decision state")
