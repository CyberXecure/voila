# Local bank dry-run attempt envelope — v0.4.57

Status: dry-run attempt envelope scaffold.

## Purpose

This milestone wraps a local-bank dry-run question, submitted answer, evaluation result, and feedback preview into an attempt-like object.

The envelope is not persisted and does not affect progress.

## Added module

```text
services/api/exam_prep_local_bank_dry_run_attempt_envelope.py
```

## Envelope fields

```text
dry_run_attempt_id
created_at
course_id
skill_id
source
question_snapshot
submitted_answer
evaluation.verdict
evaluation.score_preview
evaluation.feedback_preview
persistence flags
```

## Added check

```text
scripts/dev/check-local-bank-dry-run-attempt-envelope.ps1
```

## Safety constraints

v0.4.57 still does not:

```text
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

v0.4.58 — Local-bank dry-run session summary.

