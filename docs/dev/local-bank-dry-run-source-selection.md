# Local bank dry-run source selection — v0.4.53

Status: dry-run source selection scaffold.

## Purpose

This milestone adds a dry-run helper that models which source a future Exam Prep study session would select.

It uses the v0.4.52 flag:

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION
```

## Added module

```text
services/api/exam_prep_local_bank_dry_run_source_selection.py
```

## Behavior

Flag OFF:

```text
selected_source = legacy_fallback
dry_run_item_count = 0
```

Flag ON:

```text
selected_source = local_exercise_bank_adapter
dry_run_item_count > 0
```

## Safety constraints

v0.4.53 still does not:

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
accept user-provided filesystem roots
```

## Path safety

The dry-run helper does not accept a filesystem root from user input. It relies on the v0.4.52 internal diagnostic snapshot.

## Added check

```text
scripts/dev/check-local-bank-dry-run-source-selection.ps1
```

The check verifies:

1. flag OFF selects `legacy_fallback`
2. flag ON selects `local_exercise_bank_adapter`
3. selected local questions are dry-run only
4. no attempts/scoring/progress/live consumption behavior is enabled
5. legacy fallback remains available

## Non-goals

This milestone does not:

- wire local bank into live study sessions
- persist attempts
- score answers
- update progress
- change weak review
- add public UI
- add a web route
- add OpenAI, Mathpix, Ollama, LM Studio, or API costs

## Recommended next milestone

v0.4.54 — Local bank dry-run question quality gate.

Suggested scope:

- validate dry-run question diversity and minimum quality
- detect repetitive concept-recognition questions
- keep flag default OFF
- keep no attempts/progress/scoring

