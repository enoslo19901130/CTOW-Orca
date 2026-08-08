from pathlib import Path
import yaml
from ctow_guard import __version__


def test_versions_are_unified():
    assert __version__ == "0.2.2"
    for filename in ("config/agents.yaml", "config/policy.yaml"):
        data = yaml.safe_load(Path(filename).read_text(encoding="utf-8"))
        assert data["version"] == __version__
