import re
from pathlib import Path


def test_no_custom_runtime_supervisor_files():
    banned = [
        Path("src/ctow/mcp_server.py"),
        Path("src/ctow/adapters/codex.py"),
        Path("src/ctow/service.py"),
    ]
    assert all(not p.exists() for p in banned)


def test_adr_freezes_orca_source_of_truth():
    text = Path("docs/adr/ADR-0001-ORCA-AUTHORITATIVE-RUNTIME.md").read_text(encoding="utf-8")
    assert "single authoritative execution runtime" in text


def test_profile_compiler_does_not_own_process_lifecycle():
    text = Path("src/ctow_guard/runtime.py").read_text(encoding="utf-8")
    assert "subprocess" not in text
    assert re.search(r"(?:^|\W)pty(?:$|\W)", text, flags=re.IGNORECASE) is None
