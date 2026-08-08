from __future__ import annotations

import argparse
from pathlib import Path
import sys

from . import __version__
from .io import load_yaml
from .models import (
    BreakGlassRecord,
    DecisionProgressRecord,
    DecisionRecord,
    EscalationReport,
    HumanDecisionRecord,
    IssueIdentityRecord,
    Plan,
    ReviewReport,
    TaskContract,
    WorkerReport,
)


def validate_config(repo: Path) -> None:
    agents = load_yaml(repo / "config" / "agents.yaml")
    policy = load_yaml(repo / "config" / "policy.yaml")
    for name, cfg in (("agents", agents), ("policy", policy)):
        if cfg.get("version") != __version__:
            raise ValueError(f"config/{name}.yaml version does not match package version")
    profiles = agents["profiles"]
    expected = {"sol": "max", "terra": "high", "luna": "max"}
    for role, effort in expected.items():
        profile = profiles[role]
        if profile["reasoning_effort"] != effort:
            raise ValueError(f"{role} reasoning must be {effort}")
        if profile["fast_mode"] is not False:
            raise ValueError(f"{role} fast_mode must be false")
        if profile.get("allow_reasoning_fallback") is not False:
            raise ValueError(f"{role} reasoning fallback must be disabled")
    if policy["orchestration"]["source_of_truth"] != "orca":
        raise ValueError("Orca must remain the execution source of truth")
    d = policy["decision_efficiency"]
    if not d["require_material_evidence_delta_to_reopen"]:
        raise ValueError("decision loop prevention requires evidence delta to reopen")
    if d["same_issue_sol_revalidation_limit"] != 1:
        raise ValueError("Sol same-issue revalidation limit must be exactly 1")
    if d["fingerprint"]["canonical_owner"] != "terra":
        raise ValueError("Terra must remain canonical fingerprint owner")
    if d["stagnation_threshold_cycles"] != 2:
        raise ValueError("stagnation threshold must remain 2 cycles")
    if not d["decision_progress_ledger_required"]:
        raise ValueError("decision progress ledger must be required")
    if policy["review"]["high_risk_requires_independent_review"] is not True:
        raise ValueError("high/critical risk must require independent review")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ctow-guard")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_cfg = sub.add_parser("validate-config"); p_cfg.add_argument("--repo", default=".")
    for name in [
        "plan", "task", "worker-report", "review", "issue-identity", "escalation",
        "decision", "decision-progress", "breakglass", "human-decision"
    ]:
        p = sub.add_parser(f"validate-{name}"); p.add_argument("path")
    args = parser.parse_args(argv)
    validators = {
        "validate-plan": Plan,
        "validate-task": TaskContract,
        "validate-worker-report": WorkerReport,
        "validate-review": ReviewReport,
        "validate-issue-identity": IssueIdentityRecord,
        "validate-escalation": EscalationReport,
        "validate-decision": DecisionRecord,
        "validate-decision-progress": DecisionProgressRecord,
        "validate-breakglass": BreakGlassRecord,
        "validate-human-decision": HumanDecisionRecord,
    }
    try:
        if args.cmd == "validate-config":
            validate_config(Path(args.repo))
        else:
            validators[args.cmd].model_validate(load_yaml(args.path))
        print("OK")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
