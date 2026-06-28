# Local bank guarded live-trial scaffold — v0.4.61

Status: disabled-by-default guarded live-trial scaffold.

## Purpose

This milestone prepares a guarded local-bank live-trial plan, but does not activate live consumption.

## Added module

```text
services/api/exam_prep_local_bank_guarded_live_trial.py
```

## Added flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL
```

Default:

```text
OFF
```

## Behavior

Flag OFF:

```text
trial_status = disabled
```

Flag ON + readiness ready:

```text
trial_status = guarded_trial_plan_ready
```

This still does not wire local-bank questions into live study sessions.

## Safety constraints

v0.4.61 still does not:

```text
persist progress
persist sessions
persist attempts
update progress
score live study sessions
modify Exam Prep UI
modify weak review
replace live study sessions
replace the legacy generator
enable live consumption
require cloud/API
accept user-provided filesystem roots
```

## Recommended next milestone

v0.4.62 — Guarded live-trial adapter boundary, disabled by default.

