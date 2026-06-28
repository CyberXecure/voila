# Local bank guarded live-trial adapter boundary — v0.4.62

Status: disabled-by-default adapter boundary scaffold.

## Purpose

This milestone creates a boundary object between a future study session and the local-bank source.

It does not wire local bank into live study sessions.

## Added module

```text
services/api/exam_prep_local_bank_guarded_adapter_boundary.py
```

## Behavior

Flag OFF:

```text
boundary_status = legacy_fallback_only
```

Flag ON + v0.4.61 trial plan ready:

```text
boundary_status = local_source_candidate_available
```

The returned `local_source_candidate` is only a candidate object for a future milestone.

## Safety constraints

v0.4.62 still does not:

```text
start live sessions
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

v0.4.63 — Guarded live-trial no-op study-session hook, disabled by default.

