# Voila Exam Prep v0.5.7 — owner preview launcher

Milestone: `v0.5.7-owner-preview-launch-script`

This milestone adds a local owner-only launcher for the hidden Exam Prep session
preview page introduced in v0.5.6.

## Launcher

```powershell
scripts/dev/start-owner-session-preview-page.ps1
```

The launcher enables, for the current PowerShell process only:

```text
VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_PAGE=1
VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_ROUTE=1
```

Then it points the owner to:

```text
http://127.0.0.1:8787/owner/exam-prep/session-preview
```

and the JSON route:

```text
http://127.0.0.1:8787/owner/exam-prep/session-preview.json
```

## Usage

Start the hidden owner preview page:

```powershell
scripts/dev/start-owner-session-preview-page.ps1
```

Open the browser automatically:

```powershell
scripts/dev/start-owner-session-preview-page.ps1 -OpenBrowser
```

Dry-run the environment and URLs without starting Voila:

```powershell
scripts/dev/start-owner-session-preview-page.ps1 -NoStart
```

## Safety

This launcher does not add public navigation and does not expose tester UI.

It preserves the v0.5.6 safety model:

- hidden owner/local page
- no public UI link
- no form/input/submit
- no attempt saving
- no session persistence
- no progress update
- no live scoring
- max 5 local-bank questions
- no cloud/API/LLM dependency

The launcher only sets environment variables in the current PowerShell process.

## Validation

Run:

```powershell
scripts/dev/check-local-bank-owner-only-session-preview-launcher.ps1
```

Expected result:

```text
=== v0.5.7 OWNER PREVIEW LAUNCHER CHECK PASS ===
```
