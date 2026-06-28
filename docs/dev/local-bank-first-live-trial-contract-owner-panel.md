# Guarded first live trial contract owner panel — v0.4.79

Status: disabled-by-default hidden/internal owner panel.

## Purpose

This milestone adds a hidden owner panel over the v0.4.78 sanitized contract report route.

It does not enable live local-bank consumption.

## Added route

GET /exam-prep/local-bank/first-live-trial-contract-panel

## Added check

scripts/dev/check-local-bank-first-live-trial-contract-owner-panel.ps1

## Panel flag

VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_OWNER_PANEL

Default: OFF.

## Panel displays

contract_status
effective_source
candidate_source
fallback_source
contract_sections_available
source_selection_summary
contract_guardrails
implementation_scope
explicit_not_live_yet

## Panel omits

raw contract object
raw snapshots
correct_answer
correct_answer_preview
explanation
explanation_preview
source_excerpt
dry_run_items
selected_questions

## Guarantees

effective_source = legacy_fallback
route_kind = internal_hidden_owner_panel
has_public_ui_link = false
safe DOM rendering only
no innerHTML for fetched report data
adds_public_ui = false
starts_live_session = false
replaces_live_study_session = false
persists_attempts = false
updates_progress = false
scores_live_session = false
requires_cloud_or_api = false

## Recommended next milestone

v0.4.80 — Guarded first live trial question envelope sanitizer, disabled by default.
