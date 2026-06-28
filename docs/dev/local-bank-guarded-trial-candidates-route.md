# Local bank guarded live-trial candidate question preview route — v0.4.66

Status: disabled-by-default internal JSON candidate question preview route.

## Purpose

This milestone adds a route that previews candidate local-bank questions for a future guarded trial.

It does not expose answer previews and does not enable live local-bank consumption.

## Added route

```text
GET /exam-prep/local-bank/guarded-trial-candidates
```

## Route flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE
```

Default:

```text
OFF
```

## Required related flags

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL
```

## Candidate question fields

```text
candidate_index
dry_run_item_id
question_id
course_id
skill_id
question_type
difficulty
question
choices
source
answer_preview_hidden
explanation_preview_hidden
dry_run_only
```

## Safety constraints

v0.4.66 still does not:

```text
expose answer previews
expose explanation previews
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

v0.4.67 — Guarded live-trial candidate preview UI panel, hidden/internal and disabled by default.
