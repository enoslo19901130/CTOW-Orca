from __future__ import annotations

import json
import shutil
import subprocess
import sys


def run(cmd: list[str]):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return {"ok": p.returncode == 0, "code": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    tools = {name: shutil.which(name) for name in ("git", "codex", "orca")}
    checks = {
        "tools": tools,
        "git": run(["git", "--version"]) if tools["git"] else {"ok": False},
        "codex": run(["codex", "--version"]) if tools["codex"] else {"ok": False},
        "orca_status": run(["orca", "status", "--json"]) if tools["orca"] else {"ok": False},
        "orca_orchestration": run(["orca", "orchestration", "run-list", "--json"]) if tools["orca"] else {"ok": False},
    }
    print(json.dumps(checks, indent=2, ensure_ascii=False))
    required = checks["git"].get("ok") and checks["codex"].get("ok") and checks["orca_status"].get("ok") and checks["orca_orchestration"].get("ok")
    return 0 if required else 2


if __name__ == "__main__":
    raise SystemExit(main())
