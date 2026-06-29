# Voila Exam Prep v0.5.8 — owner preview visual/copy polish

Milestone: `v0.5.8-owner-preview-visual-copy-polish`

This milestone polishes the hidden owner-only browser preview page introduced in
v0.5.6 and launched through v0.5.7.

## Scope

The page remains:

```text
/owner/exam-prep/session-preview
```

The route remains disabled by default and requires:

```text
VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_PAGE=1
```

This milestone improves only the hidden owner page display:

- Romanian title and policy copy
- Romanian question labels
- Romanian question type and difficulty labels
- display-side diacritics for the owner preview page
- display-side `L'Hôpital` cleanup
- exact 5-card page check

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

The page still displays a read-only preview only.

## Validation

Run:

```powershell
scripts/dev/check-local-bank-owner-only-session-preview-page-polish.ps1
```

Expected result:

```text
=== v0.5.8 OWNER PREVIEW VISUAL/COPY POLISH CHECK PASS ===
```
