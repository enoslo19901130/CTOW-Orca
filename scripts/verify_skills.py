from pathlib import Path

EXPECTED = {
    "ctow-sol-architect",
    "ctow-terra-commander",
    "ctow-luna-worker",
    "ctow-luna-independent-reviewer",
    "ctow-operator",
}
root = Path(__file__).resolve().parents[1] / ".agents" / "skills"
missing = [name for name in sorted(EXPECTED) if not (root / name / "SKILL.md").is_file()]
if missing:
    raise SystemExit(f"Missing skills: {', '.join(missing)}")
print("OK: CTOW skills present")
