# Guarded local-bank owner enablement checklist — v0.4.69

Status: JSON-only local owner enablement checklist.

## Purpose

This milestone adds an explicit checklist before any future milestone can attempt real guarded live consumption.

It does not enable live local-bank consumption.

## Added module

```text
services/api/exam_prep_local_bank_owner_enablement_checklist.py
```

## Added check

```text
scripts/dev/check-local-bank-owner-enablement-checklist.ps1
```

## Required owner flags

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH
```

## Checklist verifies

```text
integration readiness
guarded trial plan
adapter boundary candidate
no-op hook candidate report
candidate preview route flag
candidate panel flags
legacy fallback remains effective source
minimum criteria for v0.4.70
```

## Explicitly not live yet

```text
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

v0.4.69 still does not:

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

v0.4.70 — Guarded local-bank live consumption decision gate, still disabled by default.
