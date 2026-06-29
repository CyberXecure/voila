# Voila Exam Prep v0.5.1 — owner-only real-course local-bank delivery smoke

Milestone: `v0.5.1-owner-only-real-course-local-bank-delivery-smoke`

This milestone validates the v0.5.0 owner-only real-delivery module against an
existing real Voila course artifact.

## Scope

The smoke check:

- selects an existing real course from `data/output`
- derives a temporary `exercise_bank.local.json` under `.tmp`
- validates that the local-bank adapter can read 5 questions
- runs owner-only real delivery with maximum 5 questions
- uses the v0.4.94 readiness guard context separately from the real-course delivery context
- verifies rollback to `legacy_fallback`
- removes the temporary `.tmp` smoke data
- does not modify `web_app.py`
- does not add public UI
- does not persist attempts, sessions, progress, or live scoring data
- does not use cloud/API/LLM dependencies

## Validation

Run:

```powershell
scripts/dev/check-local-bank-owner-only-real-course-delivery-smoke.ps1
```

Expected result:

```text
=== v0.5.1 REAL-COURSE DELIVERY SMOKE PASS ===
```

## Note

No real course library data is committed or modified by this milestone. The
temporary bank is generated only under `.tmp` and cleaned after validation.
