from ctow_guard.io import load_yaml
from ctow_guard.models import BreakGlassRecord, HumanDecisionRecord


def test_demo_audits_validate():
    BreakGlassRecord.model_validate(load_yaml("examples/BREAKGLASS-DEMO.yaml"))
    HumanDecisionRecord.model_validate(load_yaml("examples/HUMAN-DECISION-DEMO.yaml"))
