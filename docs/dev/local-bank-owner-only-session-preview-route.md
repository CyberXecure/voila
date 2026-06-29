# Voila Exam Prep v0.5.5 — hidden owner-only session preview route

Milestone: `v0.5.5-hidden-owner-session-preview-route`

This milestone introduces the first browser-reachable owner-only JSON route for
the Exam Prep session preview.

## Route

```text
/owner/exam-prep/session-preview.json
```

The route is hidden and excluded from OpenAPI schema.

It is disabled by default and returns 404 unless explicitly enabled with:

```text
VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_ROUTE=1
```

The route also requires a local owner request.

## Scope

The route returns the v0.5.4 polished session preview JSON:

- 5 sanitized prompts
- answers hidden
- explanations hidden
- no submit support
- no attempt saving
- no progress update
- no live scoring
- rollback remains available through the underlying delivery layer

## Safety

This milestone intentionally does not add:

- public navigation
- public UI
- tester UI
- session persistence
- attempt persistence
- progress persistence
- live scoring persistence
- cloud/API/LLM dependency

Temporary `.tmp` route data is cleaned after each route call.

## Validation

Run:

```powershell
scripts/dev/check-local-bank-owner-only-session-preview-route.ps1
```

Expected result:

```text
=== v0.5.5 HIDDEN OWNER ROUTE CHECK PASS ===
```
