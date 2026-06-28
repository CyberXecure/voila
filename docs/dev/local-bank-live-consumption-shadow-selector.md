# Guarded local-bank live consumption source selector shadow mode — v0.4.72

Status: disabled-by-default shadow source selector.

## Purpose

This milestone adds a shadow selector after the v0.4.71 no-op adapter boundary.

It compares the local-bank candidate path with the legacy fallback path, but does not change the effective source.

## Added module

```text
services/api/exam_prep_local_bank_live_consumption_shadow_selector.py
```

## Added check

```text
scripts/dev/check-local-bank-live-consumption-shadow-selector.ps1
```

## Shadow selector flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_SOURCE_SELECTOR
```

Default:

```text
OFF
```

## Status values

```text
disabled
blocked
shadow_selection_ready
```

## Behavior

When disabled:

```text
selector_status = disabled
effective_source = legacy_fallback
```

When all guarded flags are enabled and v0.4.71 reports candidate availability:

```text
selector_status = shadow_selection_ready
effective_source = legacy_fallback
shadow_source = local_exercise_bank_adapter
```

## Shadow report

The report includes:

```text
effective_source
shadow_source
shadow_candidate_count
legacy_source_profile
local_candidate_profile
question_type_counts
difficulty_counts
skill_counts
coverage_comparison
selected_shadow_questions
```

## Explicitly not live yet

```text
shadow selector does not change effective_source
local-bank questions are not delivered live
live study sessions are not started
effective_source remains legacy_fallback
attempts are not persisted
progress is not updated
sessions are not persisted
live scoring is not enabled
public Exam Prep navigation is not changed
```

## Safety constraints

v0.4.72 still does not:

```text
deliver local-bank questions live
consume local-bank questions live
start live sessions
replace effective source
persist progress
persist sessions
persist attempts
update progress
score live study sessions
modify public Exam Prep navigation
modify weak review
replace live study sessions
replace the legacy generator
enable live consumption
require cloud/API
accept user-provided filesystem roots
```

## Recommended next milestone

v0.4.73 — Guarded live-consumption shadow route report, disabled by default.
