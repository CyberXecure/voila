# Exam Prep local bank diagnostics — v0.4.48

Status: read-only diagnostics checkpoint.

## Purpose

This milestone adds read-only diagnostics over the local exercise bank adapter.

It follows:

```text
v0.4.44 — Local Pedagogy Engine scaffold
v0.4.45 — Local exercise bank discovery
v0.4.46 — Exam Prep local bank preview
v0.4.47 — Local bank source adapter
```

v0.4.48 does not make live Exam Prep routes consume local bank questions. It only reports whether the adapted local records are available and valid.

## Added module

```text
services/api/exam_prep_local_bank_diagnostics.py
```

The diagnostics report:

```text
active_source_adapter
local_bank_available
local_question_count
legacy_fallback_available
question_types coverage
difficulty coverage
skills coverage
sample_question_ids
validation status
warnings
```

## Safety constraints

The diagnostics explicitly report:

```text
will_modify_progress = false
will_modify_exam_prep_ui = false
will_modify_scoring = false
will_modify_weak_review = false
will_replace_legacy_generator = false
will_enable_live_consumption = false
requires_cloud_or_api = false
```

## Added check

```text
scripts/dev/check-exam-prep-local-bank-diagnostics.ps1
```

The check verifies:

1. local pedagogy output can be generated
2. local exercise bank can be adapted
3. diagnostics show local source availability
4. normalized fields pass validation
5. fallback mode still reports `legacy_fallback`
6. no live Exam Prep behavior is changed

## Non-goals

This milestone does not:

- change the dashboard
- change skill detail
- change study sessions
- change progress scoring
- change weak review
- replace legacy quiz/question data
- add OpenAI, Mathpix, Ollama, LM Studio, or API costs

## Recommended next milestone

v0.4.49 — Local bank read-only study preview.

Suggested scope:

- produce a read-only preview list of normalized local questions for a skill
- do not update progress
- do not score attempts
- do not replace the live study session source yet
- keep legacy fallback available

