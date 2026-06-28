# Guarded first live trial contract skeleton — v0.4.77

Status: JSON-only contract skeleton.

## Purpose

This milestone adds a contract object for future first live-trial owner review.

It does not enable live local-bank consumption.

## Added files

```text
services/api/exam_prep_local_bank_first_live_trial_contract.py
scripts/dev/check-local-bank-first-live-trial-contract.ps1
docs/dev/local-bank-first-live-trial-contract.md
```

## New owner flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT
```

Default: `OFF`.

## Contract statuses

```text
disabled
blocked
contract_skeleton_ready_for_owner_review
```

## Contract sections

```text
source_selection
session_boundary
attempt_persistence
progress_updates
live_scoring
sanitization
```

## Guarantees

```text
effective_source = legacy_fallback
candidate_source = local_exercise_bank_adapter
fallback_source = legacy_fallback
json_only_contract_object = true
adds_web_route = false
patches_web_app = false
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
contract skeleton does not change effective_source
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

v0.4.78 — Guarded first live trial contract report route, disabled by default.
