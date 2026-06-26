# Exam Prep local bank preview — v0.4.46

Status: non-destructive backend/diagnostic preview.

## Purpose

This milestone connects the v0.4.44 Local Pedagogy Engine scaffold and the v0.4.45 local exercise bank discovery layer to Exam Prep as a preview only.

The goal is to verify that Exam Prep can detect a valid `exercise_bank.local.json` source without replacing the existing legacy quiz/question behavior.

## Added module

```text
services/api/exam_prep_local_bank_preview.py
```

The module reports:

- whether a valid local exercise bank exists
- which source would be preview-selected
- how many local exercises are available
- whether legacy fallback remains available
- whether progress/UI/legacy generator behavior would be modified

For v0.4.46, the answers must remain conservative:

```text
will_modify_progress = false
will_modify_exam_prep_ui = false
will_replace_legacy_generator = false
requires_cloud_or_api = false
```

## Added check

```text
scripts/dev/check-exam-prep-local-bank-preview.ps1
```

The check verifies two paths:

1. local bank available path:
   - generates local pedagogy output
   - discovers valid `exercise_bank.local.json`
   - previews `local_exercise_bank_preview`
2. fallback path:
   - uses an empty root
   - previews `legacy_fallback`

## Non-goals

This milestone does not:

- make Exam Prep consume local exercises in live routes
- replace `quiz.json`
- change the dashboard
- change skill detail
- change progress thresholds
- change weak review behavior
- introduce OpenAI, Mathpix, Ollama, LM Studio, or any API cost

## Future integration model

```text
Current v0.4.46:
Exam Prep -> preview local bank availability -> still uses legacy behavior

Future v0.4.47+:
Exam Prep -> use local bank when explicitly valid/enabled -> fallback to legacy
```

## Recommended next milestone

v0.4.47 — Local bank source adapter for Exam Prep.

Suggested scope:

- introduce a read-only adapter that normalizes local exercises into Exam Prep question-like records
- keep legacy fallback
- do not change progress scoring yet
- add source labels for diagnostics
- keep UI change minimal or absent

