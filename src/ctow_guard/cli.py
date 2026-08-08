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
from .runtime import compile_codex_launch


def validate_config(repo: Path) -> None:
    agents = load_yaml(repo / "config" / "agents.yaml")
    policy = load_yaml(repo / "config" / "policy.yaml")
    for name, cfg in (("agents", agents), ("policy", policy)):
        if cfg.get("version") != __version__:
            raise ValueError(f"config/{name}.yaml version does not match package version")
    profiles = agents.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError("config/agents.yaml profiles must be a mapping")
    expected = {"sol": "max", "terra": "high", "luna": "max"}
    expected_models = {
        "sol": "gpt-5.6-sol",
        "terra": "gpt-5.6-terra",
        "luna": "gpt-5.6-luna",
    }
    for role, effort in expected.items():
        if role not in profiles or not isinstance(profiles[role], dict):
            raise ValueError(f"missing {role} runtime profile")
        profile = profiles[role]
        if profile["reasoning_effort"] != effort:
            raise ValueError(f"{role} reasoning must be {effort}")
        if profile["model"] != expected_models[role]:
            raise ValueError(f"{role} model must be {expected_models[role]}")
        if profile["fast_mode"] is not False:
            raise ValueError(f"{role} fast_mode must be false")
        if profile.get("allow_reasoning_fallback") is not False:
            raise ValueError(f"{role} reasoning fallback must be disabled")
        if profile.get("reasoning_strict") is not True:
            raise ValueError(f"{role} reasoning must be strict")
        # Compile each role during config validation.  This makes missing or
        # malformed permission fields fail before an Orca Run is created.
        compile_codex_launch(profile, role=role)

    runtime_verification = agents.get("runtime_verification")
    if not isinstance(runtime_verification, dict):
        raise ValueError("config/agents.yaml runtime_verification must be a mapping")
    required_receipts = {
        "require_effective_model_receipt",
        "require_effective_effort_receipt",
        "require_effective_fast_mode_receipt",
        "require_effective_sandbox_receipt",
        "require_effective_approval_receipt",
    }
    for field in required_receipts:
        if runtime_verification.get(field) is not True:
            raise ValueError(f"runtime verification requires {field}=true")
    if runtime_verification.get("fail_on_profile_downgrade") is not True:
        raise ValueError("runtime verification must fail on profile downgrade")
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
