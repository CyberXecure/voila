# Guarded first live trial owner decision report route — v0.4.87

Status: disabled-by-default internal JSON-only route.

## Purpose

This milestone exposes the v0.4.86 decision gate as a sanitized owner decision report route.

It does not deliver local-bank questions live.

## Added route

GET /exam-prep/local-bank/first-live-trial-owner-decision-report

## Added check

scripts/dev/check-local-bank-first-live-trial-owner-decision-report-route.ps1

## Route flag

VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_DECISION_REPORT_ROUTE

Default: OFF.

## Report validates

decision_gate_ready_for_owner_review
ready_for_next_decision
accepted_decision = keep_noop_only
real_delivery_allowed_now = false
delivery_attempted = false
delivery_performed = false
delivered_question_count = 0
effective_source = legacy_fallback

## Report omits

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
has_public_ui_link = false
starts_live_session = false
delivers_local_bank_questions_live = false
persists_sessions = false
persists_attempts = false
updates_progress = false
scores_live_session = false
requires_cloud_or_api = false

## Recommended next milestone

v0.4.88 — Guarded first live trial owner decision panel, disabled by default.
