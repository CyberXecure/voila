# Local bank guarded live-trial no-op study-session hook — v0.4.63

Status: disabled-by-default no-op study-session hook scaffold.

## Purpose

This milestone adds a hook-shaped result that a future study session can call.

It does not consume local-bank questions live.

## Added module

```text
services/api/exam_prep_local_bank_noop_study_session_hook.py
```

## Behavior

Flag OFF:

```text
hook_status = legacy_path_unchanged
effective_source = legacy_fallback
```

Flag ON + boundary candidate available:

```text
hook_status = local_source_candidate_reported_noop
effective_source = legacy_fallback
reported_candidate_available = true
```

The local candidate is reported only. The live study source remains legacy.

## Safety constraints

v0.4.63 still does not:

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

v0.4.64 — Guarded live-trial route smoke, disabled by default.

