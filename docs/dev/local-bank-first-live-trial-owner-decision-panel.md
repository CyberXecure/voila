# Guarded first live trial owner decision panel — v0.4.88

Status: disabled-by-default hidden/internal owner panel.

## Purpose

This milestone adds a hidden owner panel over the v0.4.87 sanitized owner decision report route.

It does not deliver local-bank questions live.

## Added route

GET /exam-prep/local-bank/first-live-trial-owner-decision-panel

## Added check

scripts/dev/check-local-bank-first-live-trial-owner-decision-panel.ps1

## Panel flag

VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_DECISION_PANEL

Default: OFF.

## Panel displays

accepted_decision
ready_for_next_decision
real_delivery_allowed_now
delivery_performed
delivered_question_count
effective_source
next_decision_options
readiness_checks
decision_gate_policy
explicit_not_live_yet

## Panel omits

raw decision gate
raw adapter result
raw contract
raw session envelope
raw question envelopes
answers
explanations
source excerpts
selected questions

## Guarantees

effective_source = legacy_fallback
route_kind = internal_hidden_owner_panel
has_public_ui_link = false
safe DOM rendering only
no innerHTML for fetched report data
real_delivery_allowed_now = false
delivery_performed = false
delivered_question_count = 0
starts_live_session = false
delivers_local_bank_questions_live = false
persists_attempts = false
updates_progress = false
scores_live_session = false
requires_cloud_or_api = false

## Recommended next milestone

v0.4.89 — owner-ready checkpoint and stop/go summary before any real delivery milestone.
