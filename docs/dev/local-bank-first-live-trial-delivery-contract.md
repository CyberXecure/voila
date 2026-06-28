# Guarded first live trial no-persistence delivery contract — v0.4.82

Status: JSON-only local module; disabled by default.

## Purpose

This milestone defines an owner-only no-persistence delivery contract for a future first live trial.

It does not deliver local-bank questions live yet.

## Added module

services/api/exam_prep_local_bank_first_live_trial_delivery_contract.py

## Added check

scripts/dev/check-local-bank-first-live-trial-delivery-contract.ps1

## Contract flag

VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_CONTRACT

Default: OFF.

## Contract defines

owner_only delivery scope
fixed course_id
fixed skill_id
max 5 questions
candidate_delivery_source = local_exercise_bank_adapter
fallback_source = legacy_fallback
may_deliver_live_now = false
delivery_mode = contract_only_not_live
no-persistence policy
abort policy
future delivery requirements

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

v0.4.83 — Guarded first live trial no-persistence delivery adapter no-op, disabled by default.
