# Guarded live-consumption adapter no-op boundary — v0.4.71

Status: disabled-by-default no-op adapter boundary.

## Purpose

This milestone adds a no-op boundary for a future guarded local-bank live-consumption adapter.

It does not enable live local-bank consumption.

## Added module

```text
services/api/exam_prep_local_bank_live_consumption_adapter_noop_boundary.py
```

## Added check

```text
scripts/dev/check-local-bank-live-consumption-adapter-noop-boundary.ps1
```

## Adapter boundary flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY
```

Default:

```text
OFF
```

## Status values

```text
legacy_fallback_only
live_adapter_candidate_noop
```

## No-op adapter candidate

When all owner flags and decision gate flags are enabled, the module returns:

```text
live_adapter_candidate.candidate_mode = noop_boundary_only
effective_source = legacy_fallback
```

## Explicitly not live yet

```text
adapter boundary is no-op only
local-bank questions are not consumed live
live study sessions are not replaced
effective_source remains legacy_fallback
attempts are not persisted
progress is not updated
sessions are not persisted
live scoring is not enabled
public Exam Prep navigation is not changed
```

## Minimum contract for first real live trial

```text
owner decision gate remains explicit
legacy fallback remains available
effective_source change requires separate milestone
attempt persistence requires separate milestone
progress update requires separate milestone
live scoring requires separate milestone
web routes must not accept user-provided filesystem roots
answer/explanation preview leaks remain blocked
CodeQL and final main checks must pass
```

## Safety constraints

v0.4.71 still does not:

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

v0.4.72 — Guarded live-consumption adapter owner dry-run plan, still disabled by default.
