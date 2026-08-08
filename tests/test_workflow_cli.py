from pathlib import Path

import pytest
import yaml

from ctow_guard import workflow_cli
from ctow_guard.workflow_cli import collect_status, create_plan_request, resolve_plan, start_plan


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "config").mkdir()
    source = Path(__file__).parents[1]
    for name in ("policy.yaml", "agents.yaml"):
        (tmp_path / "config" / name).write_text(
            (source / "config" / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    return tmp_path


def test_create_plan_request_contains_goal_and_sol_prompt(tmp_path: Path):
    repo = _repo(tmp_path)
    path = create_plan_request("Add API key management", repo)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert path.parent == repo / ".ctow" / "requests"
    assert data["status"] == "planning_requested"
    assert data["goal"] == "Add API key management"
    assert "CTOW Sol Architect" in data["sol_prompt"]


def test_create_plan_request_refuses_overwrite(tmp_path: Path):
    repo = _repo(tmp_path)
    target = repo / "request.yaml"
    target.write_text("existing", encoding="utf-8")
    with pytest.raises(FileExistsError):
        create_plan_request("Goal", repo, target)


def test_resolve_plan_by_exact_goal(tmp_path: Path):
    repo = _repo(tmp_path)
    plans = repo / ".ctow" / "plans"
    plans.mkdir(parents=True)
    source_plan = Path(__file__).parents[1] / "examples" / "PLAN-DEMO.yaml"
    target = plans / "PLAN-DEMO.yaml"
    target.write_text(source_plan.read_text(encoding="utf-8"), encoding="utf-8")
    path, plan = resolve_plan(repo, None, "Refactor authentication state handling without changing public protocol behavior.")
    assert path == target
    assert plan.plan_id == "PLAN-DEMO-001"


def test_start_dry_run_does_not_call_orca(tmp_path: Path):
    repo = _repo(tmp_path)
    plan = Path(__file__).parents[1] / "examples" / "PLAN-DEMO.yaml"
    result = start_plan(str(plan), None, repo, dry_run=True)
    assert result["dry_run"] is True
    assert result["plan_id"] == "PLAN-DEMO-001"
    assert result["command"][:3] == ["orca", "orchestration", "run-create"]


def test_start_goal_requires_approved_plan(tmp_path: Path):
    repo = _repo(tmp_path)
    with pytest.raises(ValueError, match="no validated Plan matches"):
        start_plan(None, "Unknown goal", repo, dry_run=True)


def test_collect_status_combines_orca_and_governance(tmp_path: Path, monkeypatch):
    repo = _repo(tmp_path)
    plans = repo / ".ctow" / "plans"
    plans.mkdir(parents=True)
    source_plan = Path(__file__).parents[1] / "examples" / "PLAN-DEMO.yaml"
    (plans / "PLAN-DEMO.yaml").write_text(source_plan.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(workflow_cli.shutil, "which", lambda _: "orca")
    monkeypatch.setattr(workflow_cli, "_orca_json", lambda args: {"ok": True, "command": args})
    status = collect_status(repo)
    assert status["ok"] is True
    assert status["governance"]["approved_plans"][0]["plan_id"] == "PLAN-DEMO-001"
    assert status["current_run"]["command"] == ["orchestration", "run-current"]
