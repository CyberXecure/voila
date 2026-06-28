# Guarded first live trial contract report route — v0.4.78

Status: disabled-by-default internal JSON-only route.

## Purpose

This milestone exposes the v0.4.77 first live-trial contract skeleton through a compact sanitized JSON route.

It does not enable live local-bank consumption.

## Added route

```text
GET /exam-prep/local-bank/first-live-trial-contract-report
```

## Added check

```text
scripts/dev/check-local-bank-first-live-trial-contract-report-route.ps1
```

## Route flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_REPORT_ROUTE
```

Default: `OFF`.

## Report contains

```text
contract_status
contract_flag_name
contract_flag_enabled
shadow_consolidation_status
effective_source
candidate_source
fallback_source
contract_sections_available
source_selection_summary
contract_guardrails
implementation_scope
next_allowed_milestone_options
```

## Report omits

```text
raw contract object
raw snapshots
correct_answer
correct_answer_preview
explanation
explanation_preview
source_excerpt
dry_run_items
selected_questions
```

## Guarantees

```text
effective_source = legacy_fallback
candidate_source = local_exercise_bank_adapter
fallback_source = legacy_fallback
route_kind = internal_json_only
has_public_ui_link = false
adds_public_ui = false
starts_live_session = false
replaces_live_study_session = false
persists_attempts = false
updates_progress = false
scores_live_session = false
requires_cloud_or_api = false
```

## Explicitly not live yet

```text
contract report route does not change effective_source
local-bank questions are not delivered live
local-bank questions are not consumed live
live study sessions are not started
effective_source remains legacy_fallback
attempts are not persisted
progress is not updated
sessions are not persisted
live scoring is not enabled
public Exam Prep navigation is not changed
```

## Recommended next milestone

v0.4.79 — Guarded first live trial contract owner panel, disabled by default.
