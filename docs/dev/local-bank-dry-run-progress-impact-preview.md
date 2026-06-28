# Local bank dry-run progress impact preview — v0.4.59

Status: dry-run progress impact preview.

## Purpose

This milestone simulates how a local-bank dry-run session summary could affect skill mastery.

The preview is not persisted and does not update real progress.

## Added module

```text
services/api/exam_prep_local_bank_dry_run_progress_impact.py
```

## Preview fields

```text
skill_id
old_mastery_preview
mastery_delta_preview
new_mastery_preview
impact_direction
correct_count
partial_count
incorrect_count
total_questions
```

## Added check

```text
scripts/dev/check-local-bank-dry-run-progress-impact.ps1
```

## Safety constraints

v0.4.59 still does not:

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

v0.4.60 — Local-bank dry-run integration readiness report.

