# Guarded local-bank live consumption decision gate — v0.4.70

Status: disabled-by-default decision gate.

## Purpose

This milestone adds a decision gate after the v0.4.69 owner enablement checklist.

It does not enable live local-bank consumption.

## Added module

```text
services/api/exam_prep_local_bank_live_consumption_decision_gate.py
```

## Added check

```text
scripts/dev/check-local-bank-live-consumption-decision-gate.ps1
```

## Decision flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE
```

Default:

```text
OFF
```

## Required eligibility flags

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE
```

## Status values

```text
blocked
eligible_for_owner_decision
```

## Owner decision options

```text
keep_disabled
continue_preview_only
plan_v0_4_71_guarded_live_consumption_adapter_noop
```

## Explicitly not live yet

```text
decision gate does not enable live consumption
local-bank questions are not consumed live
live study sessions are not replaced
effective_source remains legacy_fallback
attempts are not persisted
progress is not updated
sessions are not persisted
live scoring is not enabled
public Exam Prep navigation is not changed
```

## Safety constraints

v0.4.70 still does not:

```text
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

v0.4.71 — Guarded live-consumption adapter no-op boundary, still disabled by default.
