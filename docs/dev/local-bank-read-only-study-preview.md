# Local bank read-only study preview — v0.4.49

Status: read-only study preview checkpoint.

## Purpose

This milestone previews local-bank questions for a selected skill without changing live Exam Prep behavior.

It follows:

```text
v0.4.44 — Local Pedagogy Engine scaffold
v0.4.45 — Local exercise bank discovery
v0.4.46 — Exam Prep local bank preview
v0.4.47 — Local bank source adapter
v0.4.48 — Exam Prep local bank diagnostics
```

## Added module

```text
services/api/exam_prep_local_bank_study_preview.py
```

The module returns a read-only study preview containing:

```text
selected_skill_id
active_source
available_skill_counts
preview_question_count
questions[]
legacy_fallback_available
```

Each preview question contains:

```text
question_id
skill_id
question_type
difficulty
question
choices
correct_answer
explanation
source
ready_for_read_only_study_preview
```

## Safety constraints

v0.4.49 explicitly does not:

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

## Fallback behavior

When no valid local bank is available, the preview reports:

```text
active_source = legacy_fallback
preview_question_count = 0
legacy_fallback_available = true
```

## Added check

```text
scripts/dev/check-local-bank-study-preview.ps1
```

The check verifies:

1. local pedagogy output can be generated
2. local-bank questions can be previewed for a skill
3. automatic skill selection works
4. fallback mode works
5. no attempt/progress/scoring/live consumption behavior is enabled

## Non-goals

This milestone does not:

- change the dashboard
- change skill detail
- change study session routes
- save or score answers
- update progress
- change weak review
- replace legacy quiz/question data
- add OpenAI, Mathpix, Ollama, LM Studio, or API costs

## Recommended next milestone

v0.4.50 — Local bank study preview diagnostics route or protected UI marker.

Suggested scope:

- optionally expose a protected/non-user-facing route or internal diagnostics endpoint
- keep live study session unchanged
- keep progress untouched
- keep fallback to legacy

