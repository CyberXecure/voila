# Guarded first live trial activation / rollback playbook — v0.4.93

Status: JSON-only local module; disabled by default.

## Purpose

This milestone adds an activation plan and rollback playbook after the v0.4.92 owner reconfirmation record.

It does not make activation effective and does not deliver local-bank questions live.

## Added module

services/api/exam_prep_local_bank_first_live_trial_activation_playbook.py

## Added check

scripts/dev/check-local-bank-first-live-trial-activation-playbook.ps1

## Playbook flag

VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_ACTIVATION_ROLLBACK_PLAYBOOK

Default: OFF.

## Playbook result

activation_rollback_playbook_ready = true  
activation_effective = false  
may_deliver_live = false  
go_for_real_delivery_now = false  
real_delivery_allowed_now = false  
delivery_performed = false  
delivered_question_count = 0  
effective_source = legacy_fallback  

## Activation sequence

confirm exact owner phrases in chat  
create separate explicitly named real-delivery implementation milestone  
add a new disabled-by-default real-delivery flag  
keep no-op adapter and legacy_fallback rollback path available  
limit to owner-only fixed course_id and skill_id  
limit to max 5 sanitized local-bank questions  
run no-persistence route smoke  
run rollback smoke to legacy_fallback  

## Rollback sequence

turn off future real-delivery flag  
force effective_source back to legacy_fallback  
verify no session persisted  
verify no attempts persisted  
verify no progress updated  
verify delivery_performed=false after rollback  
run owner smoke and preflight audit again  

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
