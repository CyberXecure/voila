# Voila Exam Prep v0.5.6 — hidden owner-only session preview page

Milestone: `v0.5.6-hidden-owner-session-preview-page`

This milestone introduces the first browser-readable owner-only HTML page for
the Exam Prep session preview.

## Route

```text
/owner/exam-prep/session-preview
```

The route is hidden and excluded from OpenAPI schema.

It is disabled by default and returns 404 unless explicitly enabled with:

```text
VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_PAGE=1
```

The route also requires a local owner request.

## Scope

The page renders the v0.5.4 polished session preview:

- 5 sanitized prompts
- answers hidden
- explanations hidden
- no form
- no input
- no submit button
- no attempt saving
- no progress update
- no live scoring

## Safety

This milestone intentionally does not add:

- public navigation
- public UI link
- tester UI
- session persistence
- attempt persistence
- progress persistence
- live scoring persistence
- cloud/API/LLM dependency

Temporary `.tmp` page data is cleaned after each page call.

## Validation

Run:

```powershell
scripts/dev/check-local-bank-owner-only-session-preview-page.ps1
```

Expected result:

```text
=== v0.5.6 HIDDEN OWNER PAGE CHECK PASS ===
```
