from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path

import yaml

from . import __version__
from .cli import validate_config
from .io import load_yaml
from .models import Plan
from .runtime import RuntimePolicyError, compile_codex_launch, verify_bootstrap_receipt


def _slug(value: str, limit: int = 48) -> str:
    normalized = "-".join(value.lower().split())
    safe = "".join(char for char in normalized if char.isalnum() or char == "-")
    return (safe.strip("-") or "project")[:limit].rstrip("-")


def _repo_root(value: str | Path) -> Path:
    root = Path(value).resolve()
    if not (root / "config" / "policy.yaml").is_file():
        raise ValueError(f"not a CTOW repository: {root}")
    return root


def _sol_prompt(goal: str) -> str:
    return f"""Act as the CTOW Sol Architect for this repository.

Read AGENTS.md, the Sol skill, relevant ADRs and policy, existing .ctow/
governance evidence, and the repository state.

Goal: {goal}

Begin with discovery and planning, not implementation. Define scope, constraints,
risks, acceptance criteria, Work Packages, dependencies, execution profile,
worker demand, and independent-review requirements. Ask the Human only when
missing information would materially change product intent, architecture
boundaries, or acceptance criteria.

Write the approved Plan under .ctow/plans/, validate it with ctow-guard, and hand
the validated Plan to Terra. Orca remains authoritative for execution lifecycle.
"""


def create_plan_request(goal: str, repo: str | Path = ".", output: str | Path | None = None) -> Path:
    goal = goal.strip()
    if not goal:
        raise ValueError("goal must not be empty")
    root = _repo_root(repo)
    created_at = datetime.now(timezone.utc).replace(microsecond=0)
    if output is None:
        name = f"PLAN-REQUEST-{created_at:%Y%m%dT%H%M%SZ}-{_slug(goal)}.yaml"
        target = root / ".ctow" / "requests" / name
    else:
        target = Path(output)
        if not target.is_absolute():
            target = root / target
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"refusing to overwrite existing request: {target}")
    document = {
        "kind": "ctow-plan-request",
        "version": __version__,
        "status": "planning_requested",
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "goal": goal,
        "sol_prompt": _sol_prompt(goal),
    }
    target.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return target


def _validated_plan(path: Path) -> Plan:
    return Plan.model_validate(load_yaml(path))


def resolve_plan(repo: Path, plan_path: str | None, goal: str | None) -> tuple[Path, Plan]:
    if plan_path:
        path = Path(plan_path)
        if not path.is_absolute():
            path = repo / path
        if not path.is_file():
            raise FileNotFoundError(f"plan not found: {path}")
        return path, _validated_plan(path)
    if not goal or not goal.strip():
        raise ValueError("provide --plan <path> or an exact task goal")
    matches: list[tuple[Path, Plan]] = []
    for path in sorted((repo / ".ctow" / "plans").glob("*.yaml")):
        try:
            candidate = _validated_plan(path)
        except Exception:
            continue
        if candidate.goal.casefold() == goal.strip().casefold():
            matches.append((path, candidate))
    if not matches:
        raise ValueError(
            "no validated Plan matches that goal; run ctow-plan first, then have Sol "
            "write an approved Plan under .ctow/plans/"
        )
    if len(matches) > 1:
        paths = ", ".join(str(path) for path, _ in matches)
        raise ValueError(f"multiple Plans match that goal; select one with --plan: {paths}")
    return matches[0]


def _runtime_verification(repo: Path) -> Mapping[str, object]:
    agents = load_yaml(repo / "config" / "agents.yaml")
    verification = agents.get("runtime_verification")
    if not isinstance(verification, Mapping):
        # validate_config normally catches this first; this guard keeps the
        # helper fail-closed when called directly by an integration.
        raise RuntimeError("config/agents.yaml runtime_verification must be a mapping")
    return verification


def _role_launch(repo: Path, role: str) -> dict[str, object]:
    agents = load_yaml(repo / "config" / "agents.yaml")
    profiles = agents.get("profiles")
    if not isinstance(profiles, Mapping):
        raise RuntimeError("config/agents.yaml profiles must be a mapping")
    profile_role = "luna" if role == "reviewer" else role
    profile = profiles.get(profile_role)
    if not isinstance(profile, Mapping):
        raise RuntimeError(f"missing runtime profile for {role}")
    launch = compile_codex_launch(profile, role=role)
    return {
        "argv": list(launch.argv),
        "requested_policy": dict(launch.requested_policy),
        "expected_effective_policy": dict(launch.expected_effective_policy),
        "bootstrap": {
            "authority": "orca",
            "receipt_required": True,
            "verified": False,
            "verification_fields": ["model", "reasoning_effort", "fast_mode", "sandbox", "approval"],
        },
    }


def start_plan(
    plan_path: str | None,
    goal: str | None,
    repo: str | Path = ".",
    dry_run: bool = False,
) -> dict[str, object]:
    root = _repo_root(repo)
    validate_config(root)
    path, plan = resolve_plan(root, plan_path, goal)
    terra_launch = _role_launch(root, "terra")
    command = ["orca", "orchestration", "run-create", "--objective", plan.goal, "--json"]
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "execution_started": False,
            "plan": str(path),
            "plan_id": plan.plan_id,
            "command": command,
            "terra_launch": terra_launch,
            "runtime_verification": {
                "required": True,
                "authority": "orca",
                "fields": ["model", "reasoning_effort", "fast_mode", "sandbox", "approval"],
                "status": "pending_orca_bootstrap",
            },
        }
    if shutil.which("orca") is None:
        raise RuntimeError("Orca CLI is not available on PATH")
    status = subprocess.run(["orca", "status", "--json"], capture_output=True, text=True, check=False)
    if status.returncode != 0:
        raise RuntimeError(f"Orca runtime is not ready: {status.stderr.strip() or status.stdout.strip()}")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Orca run-create failed: {result.stderr.strip() or result.stdout.strip()}")
    try:
        receipt = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Orca returned a non-JSON run-create receipt") from exc
    try:
        verified_bootstrap = verify_bootstrap_receipt(
            terra_launch,
            receipt,
            role="terra",
            runtime_verification=_runtime_verification(root),
        )
    except RuntimePolicyError as exc:
        # A Run may already exist in Orca, but this command must not claim
        # execution started until Terra bootstrap is verifiably effective.
        exc.details.setdefault("run_created", True)
        exc.details.setdefault("execution_started", False)
        exc.details.setdefault("terra_launch", terra_launch)
        exc.details.setdefault("orca", receipt)
        raise
    return {
        "ok": True,
        "execution_started": True,
        "plan": str(path),
        "plan_id": plan.plan_id,
        "orca": receipt,
        "terra_launch": {
            **terra_launch,
            "bootstrap": {
                **dict(terra_launch["bootstrap"]),
                "verified": True,
            },
            "verification": verified_bootstrap,
        },
        "next": "Terra creates the Task DAG and supervised Luna Dispatches in this Run.",
    }


def _orca_json(arguments: list[str]) -> dict[str, object]:
    result = subprocess.run(["orca", *arguments, "--json"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return {"ok": False, "error": result.stderr.strip() or result.stdout.strip(), "command": arguments}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "Orca returned non-JSON output", "command": arguments}


def collect_status(repo: str | Path = ".") -> dict[str, object]:
    root = _repo_root(repo)
    if shutil.which("orca") is None:
        raise RuntimeError("Orca CLI is not available on PATH")
    plans: list[dict[str, str]] = []
    invalid_plans: list[dict[str, str]] = []
    for path in sorted((root / ".ctow" / "plans").glob("*.yaml")):
        try:
            plan = _validated_plan(path)
            plans.append({"plan_id": plan.plan_id, "goal": plan.goal, "path": str(path)})
        except Exception as exc:
            invalid_plans.append({"path": str(path), "error": str(exc)})
    requests = sorted(str(path) for path in (root / ".ctow" / "requests").glob("*.yaml"))
    runtime = _orca_json(["status"])
    return {
        "ok": bool(runtime.get("ok")),
        "repository": str(root),
        "runtime": runtime,
        "current_run": _orca_json(["orchestration", "run-current"]),
        "runs": _orca_json(["orchestration", "run-list"]),
        "governance": {
            "planning_requests": requests,
            "approved_plans": plans,
            "invalid_plans": invalid_plans,
        },
    }


def _add_plan_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("goal", help="Project or task goal for Sol to plan")
    parser.add_argument("--repo", default=".", help="CTOW repository root")
    parser.add_argument("--output", help="Request output path relative to the repository")


def _add_start_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("goal", nargs="?", help="Exact goal of an approved Plan")
    parser.add_argument("--plan", help="Approved Plan YAML path")
    parser.add_argument("--repo", default=".", help="CTOW repository root")
    parser.add_argument("--dry-run", action="store_true", help="Validate and show the Orca action only")


def _add_status_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", default=".", help="CTOW repository root")


def _run_plan(args: argparse.Namespace) -> int:
    try:
        path = create_plan_request(args.goal, args.repo, args.output)
        print(json.dumps({"ok": True, "request": str(path), "next": "Give sol_prompt to Sol."}, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def _run_start(args: argparse.Namespace) -> int:
    try:
        print(json.dumps(start_plan(args.plan, args.goal, args.repo, args.dry_run), ensure_ascii=False))
        return 0
    except RuntimePolicyError as exc:
        print(json.dumps({"ok": False, "execution_started": False, "error": exc.as_dict()}, ensure_ascii=False), file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def _run_status(args: argparse.Namespace) -> int:
    try:
        status = collect_status(args.repo)
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return 0 if status["ok"] else 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ctow")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    plan_parser = sub.add_parser("plan", help="Create a Sol planning request")
    _add_plan_arguments(plan_parser)
    start_parser = sub.add_parser("start", help="Validate a Plan and create its Orca Run")
    _add_start_arguments(start_parser)
    status_parser = sub.add_parser("status", help="Show Orca and CTOW governance status")
    _add_status_arguments(status_parser)
    args = parser.parse_args(argv)
    if args.command == "plan":
        return _run_plan(args)
    if args.command == "start":
        return _run_start(args)
    return _run_status(args)


def plan_entry(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ctow-plan")
    parser.add_argument("--version", action="version", version=__version__)
    _add_plan_arguments(parser)
    return _run_plan(parser.parse_args(argv))


def start_entry(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ctow-start")
    parser.add_argument("--version", action="version", version=__version__)
    _add_start_arguments(parser)
    return _run_start(parser.parse_args(argv))


def status_entry(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ctow-status")
    parser.add_argument("--version", action="version", version=__version__)
    _add_status_arguments(parser)
    return _run_status(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
