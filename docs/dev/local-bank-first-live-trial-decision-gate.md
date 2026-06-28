# Guarded first live trial decision gate — v0.4.86

Status: JSON-only local module; disabled by default.

## Purpose

This milestone adds an explicit decision gate over the guarded first-live-trial chain.

It verifies readiness up to the no-op delivery boundary but blocks real delivery now.

## Added module

services/api/exam_prep_local_bank_first_live_trial_decision_gate.py

## Added check

scripts/dev/check-local-bank-first-live-trial-decision-gate.ps1

## Gate flag

VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DECISION_GATE

Default: OFF.

## Allowed decision values

keep_noop_only
prepare_owner_panel_review
prepare_future_real_delivery_milestone

## Policy

real_delivery_allowed_now = false
may_flip_effective_source_now = false
may_start_live_session_now = false
may_persist_session_now = false
may_persist_attempts_now = false
may_update_progress_now = false
may_score_live_session_now = false
requires_separate_real_delivery_milestone = true
requires_owner_reconfirmation_before_real_delivery = true
requires_rollback_to_legacy_fallback = true

## Guarantees

effective_source = legacy_fallback
json_only_local_module = true
adds_web_route = false
patches_web_app = false
adds_public_ui = false
starts_live_session = false
replaces_live_study_session = false
delivers_local_bank_questions_live = false
persists_sessions = false
persists_attempts = false
updates_progress = false
scores_live_session = false
requires_cloud_or_api = false

## Recommended next milestone

v0.4.87 — Guarded first live trial owner decision report route, disabled by default.
