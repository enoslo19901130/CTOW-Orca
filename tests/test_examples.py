from ctow_guard.io import load_yaml
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


def test_all_yaml_examples_validate():
    cases = [
        ("examples/PLAN-DEMO.yaml", Plan),
        ("examples/TASK-WP001.yaml", TaskContract),
        ("examples/TASK-REVIEW-WP002.yaml", TaskContract),
        ("examples/WORKER-REPORT-DEMO.yaml", WorkerReport),
        ("examples/REVIEW-DEMO.yaml", ReviewReport),
        ("examples/ISSUE-IDENTITY-DEMO.yaml", IssueIdentityRecord),
        ("examples/ESCALATION-DEMO.yaml", EscalationReport),
        ("examples/DECISION-DEMO.yaml", DecisionRecord),
        ("examples/DECISION-PROGRESS-DEMO.yaml", DecisionProgressRecord),
        ("examples/DECISION-PROGRESS-STAGNATION-DEMO.yaml", DecisionProgressRecord),
        ("examples/BREAKGLASS-DEMO.yaml", BreakGlassRecord),
        ("examples/HUMAN-DECISION-DEMO.yaml", HumanDecisionRecord),
    ]
    for path, model in cases:
        model.model_validate(load_yaml(path))
