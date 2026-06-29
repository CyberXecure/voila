# Guarded first live trial real-delivery proposal gate — v0.4.91

Status: JSON-only local module; disabled by default.

## Purpose

This milestone adds a real-delivery proposal and owner reconfirmation gate after the v0.4.90 preflight audit.

It does not deliver local-bank questions live.

## Added module

services/api/exam_prep_local_bank_first_live_trial_real_delivery_proposal.py

## Added check

scripts/dev/check-local-bank-first-live-trial-real-delivery-proposal.ps1

## Proposal gate flag

VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_REAL_DELIVERY_PROPOSAL_GATE

Default: OFF.

## Proposal result

proposal_ready_waiting_for_owner_reconfirmation = true  
may_deliver_live = false  
go_for_real_delivery_now = false  
real_delivery_allowed_now = false  
delivery_performed = false  
delivered_question_count = 0  
effective_source = legacy_fallback  

## Exact owner reconfirmation phrases

CONFIRM OWNER-ONLY NO-PERSISTENCE REAL DELIVERY  
CONFIRM ROLLBACK TO LEGACY_FALLBACK  
CONFIRM NO ATTEMPT OR PROGRESS PERSISTENCE  
CONFIRM MAX 5 LOCAL-BANK QUESTIONS  
CONFIRM SEPARATE REAL-DELIVERY MILESTONE  

## Future activation scope

owner_only = true  
fixed course_id  
fixed skill_id  
max_questions = 5  
sanitized_question_envelopes_only = true  
no public UI  
no attempt persistence  
no session persistence  
no progress update  
no live scoring persistence  

## Rollback plan

rollback_to_effective_source = legacy_fallback  
disable_real_delivery_flag = true  
keep_noop_adapter_available = true  
final_owner_smoke_required = true  

## Guarantees

effective_source = legacy_fallback  
json_only_local_module = true  
adds_web_route = false  
patches_web_app = false  
adds_public_ui = false  
starts_live_session = false  
delivers_local_bank_questions_live = false  
persists_sessions = false  
persists_attempts = false  
updates_progress = false  
scores_live_session = false  
requires_cloud_or_api = false
