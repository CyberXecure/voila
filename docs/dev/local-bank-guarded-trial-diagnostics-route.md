# Local bank guarded live-trial diagnostics route — v0.4.65

Status: disabled-by-default internal JSON diagnostics route.

## Purpose

This milestone adds a compact diagnostics route for the guarded local-bank trial chain.

It does not enable live local-bank consumption.

## Added route

```text
GET /exam-prep/local-bank/guarded-trial-diagnostics
```

## Route flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE
```

Default:

```text
OFF
```

## Related guarded trial flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL
```

## Diagnostics summary

The route reports:

```text
diagnostics_status
hook_status
boundary_status
readiness_status
candidate_available
effective_source
fallback_source
safety_ok
safety_flags
versions
```

## Safety constraints

v0.4.65 still does not:

```text
consume local-bank questions live
start live sessions
replace effective source
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

v0.4.66 — Guarded live-trial candidate question preview route, disabled by default.

