# Local exercise bank discovery — v0.4.45

Status: scaffold integration checkpoint.

## Purpose

This milestone adds a safe discovery and validation layer for `exercise_bank.local.json`.

It follows v0.4.44, where the local pedagogy engine started generating:

```text
course_analysis.local.json
exercise_bank.local.json
exam_blueprint.local.json
```

v0.4.45 does not make Exam Prep consume the local bank yet. It creates the bridge needed for future non-destructive integration.

## Added module

```text
services/api/local_exercise_bank.py
```

Responsibilities:

- discover `exercise_bank.local.json`
- validate minimum schema
- validate exercise ids and required fields
- expose a selected valid bank candidate
- report a legacy fallback policy
- avoid cloud/API/LLM dependencies

## Added check

```text
scripts/dev/check-local-exercise-bank-discovery.ps1
```

The check:

1. creates temporary local pedagogy output using `local_pedagogy_engine.py`
2. discovers `exercise_bank.local.json`
3. validates the bank
4. verifies that a valid selected bank exists
5. verifies that fallback policy still points to legacy quiz/question data

## Non-goals

This milestone does not:

- replace `quiz.json`
- replace legacy generated questions
- change Exam Prep UI
- change progress thresholds
- change weak review behavior
- add OpenAI, Mathpix, Ollama, LM Studio, or any API cost
- perform formula OCR

## Future integration model

```text
Exam Prep question source order:
1. local exercise_bank.local.json, when present and valid
2. existing exercise_bank.json, if introduced later
3. legacy quiz/question source
```

## Recommended next milestone

v0.4.46 — Non-destructive Exam Prep local exercise bank source preview.

Suggested scope:

- expose source diagnostics in backend only
- keep UI minimal or unchanged
- keep fallback to legacy
- do not change scoring/progress thresholds
- use the local bank only when explicitly available and valid

