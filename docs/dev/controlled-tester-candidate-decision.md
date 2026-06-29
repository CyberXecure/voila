# Voila Exam Prep v0.6.0 — controlled tester candidate decision

Milestone: `v0.6.0-controlled-tester-candidate-decision`

This milestone records the decision that the owner-only Exam Prep preview flow is
ready for a **separate controlled tester package dry-run milestone**.

It does **not** activate testers.

It does **not** create or distribute a tester package.

## Decision

Allowed next steps:

```text
STOP
v0.6.1-controlled-tester-package-dry-run-no-distribution
```

Blocked in this milestone:

- direct tester activation
- public UI link
- public release
- package distribution
- session persistence
- attempt persistence
- progress persistence
- live scoring persistence
- cloud/API/LLM requirement

## Evidence

The decision is based on the owner-only chain through v0.5.9:

- hidden JSON route validated
- hidden HTML preview page validated
- Romanian visual/copy polish validated
- manual smoke report validated
- 5 questions only
- `effective_source=local_bank`
- `rollback_source=legacy_fallback`
- no form/input/submit
- no persistence
- no live scoring
- no public UI/navigation

## Validation

Run:

```powershell
scripts/dev/check-controlled-tester-candidate-decision.ps1
```

Expected result:

```text
=== v0.6.0 CONTROLLED TESTER CANDIDATE DECISION CHECK PASS ===
```
