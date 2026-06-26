# Local bank source adapter — v0.4.47

Status: read-only adapter checkpoint.

## Purpose

This milestone introduces a read-only adapter that normalizes local `exercise_bank.local.json` records into an Exam Prep-compatible question shape.

It follows:

```text
v0.4.44 — Local Pedagogy Engine scaffold
v0.4.45 — Local exercise bank discovery
v0.4.46 — Exam Prep local bank preview
```

## Added module

```text
services/api/exam_prep_local_bank_adapter.py
```

The adapter normalizes local exercises into records with:

```text
question_id
source_exercise_id
course_id
skill_id
question_type
difficulty
question
choices
correct_answer
explanation
source_excerpt
source = local_exercise_bank_adapter
source_bank_path
ready_for_exam_prep_preview = true
```

## Safety constraints

v0.4.47 remains read-only.

It does not:

- change live Exam Prep routes
- change scoring
- change progress thresholds
- change weak review behavior
- change the dashboard
- change skill detail UI
- replace legacy quiz/question data
- introduce OpenAI, Mathpix, Ollama, LM Studio, or API cost

The adapter explicitly reports:

```text
will_modify_progress = false
will_replace_legacy_generator = false
requires_cloud_or_api = false
```

## Fallback behavior

When no valid local exercise bank exists, the adapter reports:

```text
active_source_adapter = legacy_fallback
question_count = 0
legacy_fallback_available = true
```

## Added check

```text
scripts/dev/check-local-bank-source-adapter.ps1
```

The check verifies:

- local pedagogy output can be generated
- local bank can be discovered and adapted
- normalized question records contain required fields
- fallback mode works when no local bank is available
- no progress/UI/legacy generator replacement is performed

## Recommended next milestone

v0.4.48 — Exam Prep local bank adapter diagnostics route/check.

Suggested scope:

- expose adapter summary through backend diagnostics or health-only checks
- do not make live study sessions consume local bank yet
- keep fallback to legacy
- keep UI changes absent or minimal

