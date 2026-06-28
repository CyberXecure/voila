# Guarded first live trial owner smoke route — v0.4.85

Status: disabled-by-default internal JSON-only route.

## Purpose

This milestone adds an owner smoke route that verifies the guarded first-live-trial chain up to the no-op delivery boundary.

It does not deliver local-bank questions live.

## Added route

GET /exam-prep/local-bank/first-live-trial-owner-smoke

## Added check

scripts/dev/check-local-bank-first-live-trial-owner-smoke-route.ps1

## Route flag

VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_SMOKE_ROUTE

Default: OFF.

## Smoke validates

adapter_ready
delivery_attempted_false
delivery_performed_false
delivered_question_count_zero
candidate_question_count_positive
legacy_fallback_available
blocks_delivery_now
returns_noop_result
no_persistence_contract_ready

## Route result

route_kind = internal_json_only
smoke_status = owner_smoke_ready_for_next_decision
delivery_attempted = false
delivery_performed = false
delivered_question_count = 0
delivered_question_ids = []
effective_source = legacy_fallback

## Guarantees

effective_source = legacy_fallback
has_public_ui_link = false
starts_live_session = false
delivers_local_bank_questions_live = false
persists_sessions = false
persists_attempts = false
updates_progress = false
scores_live_session = false
requires_cloud_or_api = false

## Recommended next milestone

v0.4.86 — Guarded first live trial explicit no-persistence delivery decision gate, disabled by default.
