# Local bank protected preview route — v0.4.50

Status: protected read-only route checkpoint.

## Purpose

This milestone exposes the local-bank read-only study preview through an internal/protected backend route.

The route is disabled by default and is meant for diagnostics only.

## Added route

```text
GET /exam-prep/local-bank-study-preview
```

Required for enabled diagnostics:

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE=1
```

Query parameters:

```text
root
course_id
skill_id
limit
```

## Safety constraints

The route explicitly does not:

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

## Added check

```text
scripts/dev/check-local-bank-protected-preview-route.ps1
```

The check:

1. generates local pedagogy output
2. starts Voila with the route flag enabled
3. calls the protected preview route
4. verifies read-only preview output
5. verifies no progress/scoring/attempt/live-session behavior is enabled

## Non-goals

This milestone does not:

- link the route from the UI
- expose it as a public user feature
- change the live study session source
- save attempts
- update progress
- score answers
- replace legacy quiz/question data
- add OpenAI, Mathpix, Ollama, LM Studio, or API costs

## Recommended next milestone

v0.4.51 — Local bank preview UI marker or internal panel.

Suggested scope:

- show route/status diagnostics only when explicitly enabled
- keep live study unchanged
- keep progress untouched
- keep fallback to legacy

