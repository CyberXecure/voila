# Guarded local-bank live consumption shadow route report — v0.4.73

Status: disabled-by-default internal JSON-only shadow report route.

## Purpose

This milestone exposes the v0.4.72 shadow selector through a compact sanitized JSON report.

It does not expose raw snapshots, answers, explanations, correct answer previews, or explanation previews.

## Added route

```text
GET /exam-prep/local-bank/live-consumption-shadow-report
```

## Route flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_ROUTE
```

Default:

```text
OFF
```

## Required related flags for enabled smoke

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_SOURCE_SELECTOR
```

## Sanitized report fields

```text
selector_status
adapter_boundary_status
effective_source
shadow_source
shadow_candidate_count
coverage_comparison
local_candidate_profile
selected_shadow_questions
```

## Explicit omissions

The route does not return:

```text
correct_answer
correct_answer_preview
explanation
explanation_preview
source_excerpt
raw snapshots
decision gate raw output
owner checklist raw output
dry_run_items
selected_questions
```

## Safety constraints

v0.4.73 still does not:

```text
deliver local-bank questions live
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

v0.4.74 — Guarded live-consumption shadow route owner panel, disabled by default.
