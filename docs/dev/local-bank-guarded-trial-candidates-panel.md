# Local bank guarded live-trial candidate preview internal panel — v0.4.67

Status: disabled-by-default hidden/internal candidate preview panel.

## Purpose

This milestone adds a hidden/internal UI panel that previews candidate local-bank questions by reading the v0.4.66 candidate route.

It does not expose answer previews and does not enable live local-bank consumption.

## Added route

```text
GET /exam-prep/local-bank/guarded-trial-candidates-panel
```

## Panel flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL
```

Default:

```text
OFF
```

## Related flags for full candidate data

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL
```

## Behavior

Panel flag OFF:

```text
data-panel-status = disabled
```

Panel flag ON:

```text
data-panel-status = enabled
```

The panel fetches:

```text
GET /exam-prep/local-bank/guarded-trial-candidates
```

## Safety constraints

v0.4.67 still does not:

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
modify Exam Prep public navigation
modify weak review
replace live study sessions
replace the legacy generator
enable live consumption
require cloud/API
accept user-provided filesystem roots
```

## Recommended next milestone

v0.4.68 — Guarded live-trial candidate preview panel polish and owner smoke.
