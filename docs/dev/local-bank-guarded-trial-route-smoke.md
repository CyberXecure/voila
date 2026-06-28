# Local bank guarded live-trial route smoke — v0.4.64

Status: disabled-by-default internal JSON smoke route.

## Purpose

This milestone adds an internal route that smoke-tests the v0.4.63 no-op study-session hook.

It does not enable live local-bank consumption.

## Added route

```text
GET /exam-prep/local-bank/guarded-trial-smoke
```

## Route flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_SMOKE_ROUTE
```

Default:

```text
OFF
```

## Related guarded trial flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL
```

## Behavior

Route flag OFF:

```text
status = disabled
```

Route flag ON + guarded trial flag ON:

```text
status = ok
hook_status = local_source_candidate_reported_noop
effective_source = legacy_fallback
reported_candidate_available = true
```

The route is JSON-only and has no public UI link.

## Safety constraints

v0.4.64 still does not:

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

v0.4.65 — Guarded live-trial route diagnostics panel, JSON-only and disabled by default.

