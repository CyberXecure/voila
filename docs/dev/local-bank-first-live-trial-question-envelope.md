# Guarded first live trial question envelope sanitizer — v0.4.80

Status: JSON-only local module; disabled by default.

## Purpose

This milestone defines a safe question envelope sanitizer for a future first live trial.

It strips answer, explanation, raw snapshot, raw contract, dry-run, selected-question, and source-excerpt fields from candidate questions.

It does not enable live local-bank consumption.

## Added module

services/api/exam_prep_local_bank_first_live_trial_question_envelope.py

## Added check

scripts/dev/check-local-bank-first-live-trial-question-envelope.ps1

## Sanitizer flag

VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_QUESTION_ENVELOPE_SANITIZER

Default: OFF.

## Safe envelope contains

envelope_schema_version
envelope_version
question_id
skill_id
question_type
difficulty
source
display_index
prompt
choices
metadata_only
answer_hidden_until_submission
explanation_hidden_until_submission
will_deliver_live
will_save_attempt
will_update_progress
will_score_answer

## Sanitizer strips

correct_answer
correct_answer_preview
answer
expected_answer
solution
explanation
explanation_preview
source_excerpt
raw_snapshots
raw_contract
dry_run_items
selected_questions

## Guarantees

effective_source = legacy_fallback
json_only_local_module = true
adds_web_route = false
patches_web_app = false
adds_public_ui = false
starts_live_session = false
replaces_live_study_session = false
delivers_local_bank_questions_live = false
persists_attempts = false
updates_progress = false
scores_live_session = false
requires_cloud_or_api = false

## Recommended next milestone

v0.4.81 — Guarded first live trial dry-run session envelope, disabled by default.
