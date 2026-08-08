import json
from pathlib import Path
from ctow_guard.models import (
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


def test_json_schemas_match_pydantic_models():
    models = {
        "plan.schema.json": Plan,
        "task-contract.schema.json": TaskContract,
        "worker-report.schema.json": WorkerReport,
        "review-report.schema.json": ReviewReport,
        "issue-identity.schema.json": IssueIdentityRecord,
        "escalation-report.schema.json": EscalationReport,
        "decision-record.schema.json": DecisionRecord,
        "decision-progress.schema.json": DecisionProgressRecord,
        "break-glass.schema.json": BreakGlassRecord,
        "human-decision.schema.json": HumanDecisionRecord,
    }
    for filename, model in models.items():
        on_disk = json.loads(Path("schemas", filename).read_text())
        assert on_disk == model.model_json_schema(), filename
