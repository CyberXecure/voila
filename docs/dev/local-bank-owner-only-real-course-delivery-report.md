# Voila Exam Prep v0.5.2 — owner-only real-course delivery report JSON

Milestone: `v0.5.2-owner-only-real-course-delivery-report-json`

This milestone adds a JSON-only owner report for the v0.5.1 real-course local-bank
delivery smoke.

## Scope

The report captures:

- selected real course path
- temporary local-bank path
- temporary bank exercise count
- delivery target course and skill
- readiness guard course and skill
- default disabled result
- owner-only delivery result
- rollback result
- safety confirmations

## Safety

The report does not add public UI and does not patch `web_app.py`.

It does not persist:

- attempts
- sessions
- progress
- live scoring data
- user answers

The report contains delivered question IDs and counts, but not answers,
explanations, source excerpts, or raw local-bank records.

## Validation

Run:

```powershell
scripts/dev/check-local-bank-owner-only-real-course-delivery-report.ps1
```

Expected result:

```text
=== v0.5.2 REPORT CHECK PASS ===
```

