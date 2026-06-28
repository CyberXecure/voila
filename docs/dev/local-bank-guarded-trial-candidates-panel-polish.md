# Local bank guarded live-trial candidate panel polish owner smoke — v0.4.68

Status: disabled-by-default hidden/internal candidate panel polish and owner smoke.

## Purpose

This milestone adds a polished hidden/internal panel for owner smoke testing candidate local-bank questions.

It does not expose answer previews and does not enable live local-bank consumption.

## Added route

```text
GET /exam-prep/local-bank/guarded-trial-candidates-panel-polish
```

## Panel polish flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH
```

Default:

```text
OFF
```

## UI polish

The panel includes:

```text
compact summary
status / count / source / safety cards
type / difficulty / skill badges
safe DOM rendering
noindex/nofollow
internal hidden owner-smoke route
```

## Safety constraints

v0.4.68 still does not:

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
modify public Exam Prep navigation
replace live study sessions
enable live consumption
require cloud/API
accept user-provided filesystem roots
```

## Recommended next milestone

v0.4.69 — Guarded local-bank trial explicit owner enablement checklist.
