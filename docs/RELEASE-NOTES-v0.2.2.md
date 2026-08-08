# CTOW v0.2.2 Release Notes

Theme: **Governance hardening against semantic loop evasion.**

The release keeps Orca as the authoritative execution runtime and strengthens only CTOW governance:

- Terra-owned canonical issue identity;
- stable semantic decision-question keys;
- typed material evidence delta;
- decision cycle/stagnation ledger;
- schema-enforced stop conditions;
- richer Task Contract semantics;
- generated JSON Schemas with drift tests;
- explicit real-Orca verification checklist/baseline.

## Release validation

The package must pass:

```bash
python -m pytest -q
PYTHONPATH=src python -m ctow_guard.cli validate-config --repo .
python scripts/verify_skills.py
```

Real Orca E2E validation remains a separate operational milestone. See `ORCA-E2E-PROOF.md`.
