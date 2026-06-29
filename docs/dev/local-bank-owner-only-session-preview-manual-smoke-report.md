# Voila Exam Prep v0.5.9 — owner manual smoke screenshot/report

Milestone: `v0.5.9-owner-manual-smoke-report`

This milestone records the owner-only manual browser smoke criteria for the
hidden Exam Prep preview page.

## Scope

Adds:

```text
scripts/dev/build-owner-session-preview-manual-smoke-report.py
scripts/dev/check-owner-session-preview-manual-smoke-report.ps1
docs/dev/local-bank-owner-only-session-preview-manual-smoke-report.md
```

The report validates the hidden owner preview page and JSON route without adding
new product behavior.

## Manual browser smoke

Start the owner preview:

```powershell
scripts/dev/start-owner-session-preview-page.ps1 -OpenBrowser
```

Expected URL:

```text
http://127.0.0.1:8787/owner/exam-prep/session-preview
```

Capture a local screenshot showing:

- the Romanian page title
- owner-only hidden preview badge
- at least the first three question cards
- no form, input, or submit button
- policy text saying answers/explanations are hidden
- policy text saying no attempts/progress/scoring are saved

Do not commit screenshots by default. Keep the screenshot local unless a future
milestone explicitly defines a sanitized artifact policy.

## Safety

This milestone does not add:

- public navigation
- public UI link
- tester UI
- form
- input
- submit button
- attempt persistence
- session persistence
- progress persistence
- live scoring persistence
- cloud/API/LLM dependency

## Validation

Run:

```powershell
scripts/dev/check-owner-session-preview-manual-smoke-report.ps1
```

Expected result:

```text
=== v0.5.9 OWNER MANUAL SMOKE REPORT CHECK PASS ===
```
