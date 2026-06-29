# Voila Exam Prep v0.5.4 — session preview encoding/copy polish

Milestone: `v0.5.4-session-preview-copy-polish`

This milestone polishes the owner-only session preview copy before any hidden
owner route or browser-facing preview is introduced.

## Scope

The patch updates the v0.5.3 session preview helper to:

- normalize common PDF/OCR/console mojibake in displayed prompts
- normalize ligatures and non-printing control characters
- convert generic English smoke prompts into Romanian owner-preview copy
- keep prompts capped to a short preview length
- keep answers and explanations hidden
- keep stdout JSON safe for PowerShell logs

## Safety

No public UI is added.

`web_app.py` is not patched.

The preview remains:

- owner-only
- JSON-only
- no submit
- no attempt saving
- no session persistence
- no progress update
- no live scoring
- no cloud/API/LLM dependency

## Validation

Run:

```powershell
scripts/dev/check-local-bank-owner-only-session-preview-copy-polish.ps1
```

Expected result:

```text
=== v0.5.4 SESSION PREVIEW COPY POLISH CHECK PASS ===
```
