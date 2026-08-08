from pathlib import Path
from ctow_guard.cli import validate_config


def test_config_consistency():
    validate_config(Path('.'))
