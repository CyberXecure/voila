# Guarded local-bank live consumption shadow route owner panel — v0.4.74

Status: disabled-by-default hidden/internal owner panel.

## Purpose

This milestone adds a hidden/internal owner panel over the v0.4.73 sanitized shadow report route.

It does not expose raw snapshots, answers, explanations, correct answer previews, or explanation previews.

## Added route

```text
GET /exam-prep/local-bank/live-consumption-shadow-panel
```

## Panel flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_OWNER_PANEL
```

Default:

```text
OFF
```

## Related flags for full owner smoke

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_SOURCE_SELECTOR
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_ROUTE
```

## Panel displays

```text
selector_status
effective_source
shadow_source
shadow_candidate_count
coverage comparison
selected shadow question metadata only
```

## Explicit omissions

The panel does not render:

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

v0.4.74 still does not:

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

v0.4.75 — Guarded live-consumption shadow report/panel consolidation status.
