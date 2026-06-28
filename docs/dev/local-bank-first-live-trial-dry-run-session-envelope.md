# Guarded first live trial dry-run session envelope — v0.4.81

Status: JSON-only local module; disabled by default.

## Purpose

This milestone groups sanitized question envelopes into an owner-only dry-run session envelope.

It does not enable live local-bank delivery, persistence, progress updates, or scoring.

## Added module

services/api/exam_prep_local_bank_first_live_trial_dry_run_session.py

## Added check

scripts/dev/check-local-bank-first-live-trial-dry-run-session.ps1

## Session flag

VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_DRY_RUN_SESSION_ENVELOPE

Default: OFF.

## Session envelope contains

session_schema_version
session_envelope_version
session_kind
course_id
skill_id
effective_source
candidate_source
fallback_source
question_count
question_envelopes
metadata_only
will_deliver_live
will_start_live_session
will_persist_session
will_save_attempts
will_update_progress
will_score_answers

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

v0.4.82 — Guarded first live trial no-persistence delivery contract, disabled by default.
