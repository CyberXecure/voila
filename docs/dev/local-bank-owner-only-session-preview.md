# Voila Exam Prep v0.5.3 — owner-only session preview JSON

Milestone: `v0.5.3-owner-only-session-preview-json`

This milestone adds a JSON-only owner session preview for the first real-course
local-bank Exam Prep delivery flow.

## Scope

The preview includes:

- selected real course path
- temporary local-bank path and exercise count
- delivery target course and skill
- readiness guard course and skill
- delivery rollup
- rollback rollup
- session preview ID
- 5 sanitized question prompts
- choices when available
- no answers or explanations
- no submission support
- no attempt saving
- no progress update
- no live scoring

## Safety

The preview does not add public UI and does not patch `web_app.py`.

It does not persist:

- sessions
- attempts
- progress
- answers
- live scores

This is a local owner-only JSON preview, not a tester-facing UI.

## Validation

Run:

```powershell
scripts/dev/check-local-bank-owner-only-session-preview.ps1
```

Expected result:

```text
=== v0.5.3 SESSION PREVIEW CHECK PASS ===
```

