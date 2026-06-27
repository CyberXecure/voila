# Local bank preview internal panel — v0.4.51

Status: protected/internal read-only JSON diagnostics panel.

## Purpose

This milestone adds a minimal internal JSON diagnostics panel for the local-bank read-only study preview.

The panel is disabled by default and has no public UI link.

## Added route

```text
GET /exam-prep/local-bank-study-preview/panel
```

Enable locally with:

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE=1
```

## Safety constraints

The panel does not:

```text
save attempts
update progress
score answers
modify Exam Prep UI
modify weak review
replace live study sessions
replace the legacy generator
enable live consumption
require cloud/API
```

The route includes `noindex,nofollow` and is intended for internal diagnostics only.

## Added check

```text
scripts/dev/check-local-bank-preview-internal-panel.ps1
```

The check:

1. generates local pedagogy output
2. starts Voila with the protected flag enabled
3. calls the internal panel route
4. verifies read-only safety markers
5. verifies local source and selected skill preview markers

## Non-goals

This milestone does not:

- add a public link in the UI
- change live study sessions
- save or score answers
- update progress
- change weak review
- replace legacy quiz/question data
- add OpenAI, Mathpix, Ollama, LM Studio, or API costs

## Recommended next milestone

v0.4.52 — Local bank controlled consumption flag scaffold.

Suggested scope:

- introduce an explicit disabled-by-default consumption flag
- keep legacy fallback
- do not update progress yet
- do not score attempts yet
