# Local bank dry-run session summary — v0.4.58

Status: dry-run session summary scaffold.

## Purpose

This milestone groups local-bank dry-run attempt envelopes into a session-like summary.

The summary is not persisted and does not affect progress.

## Added module

```text
services/api/exam_prep_local_bank_dry_run_session_summary.py
```

## Summary fields

```text
dry_run_session_id
total_questions
correct_count
partial_count
incorrect_count
average_score_preview
feedback_summary
envelopes
session persistence flags
```

## Added check

```text
scripts/dev/check-local-bank-dry-run-session-summary.ps1
```

## Safety constraints

v0.4.58 still does not:

```text
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

v0.4.59 — Local-bank dry-run progress impact preview.

