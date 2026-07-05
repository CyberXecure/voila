# Voila v0.7.13 consolidated risk notes

Milestone: `v0.7.13-owner-local-read-only-smoke-index-consolidation-no-build-no-distribution`

## Purpose

This document consolidates the main risks identified by the owner-local audit/smoke documentation chain and records the current mitigation stance.

## Policy risks

| Risk | Description | Mitigation |
| --- | --- | --- |
| Build creep | A documentation milestone accidentally adds build/package steps | Validation scans for build/ZIP/delivery/distribution terms and the policy forbids execution |
| Live smoke creep | A static route-smoke milestone becomes a live HTTP test | v0.7.11-v0.7.13 state that no server startup and no live HTTP smoke are performed |
| non-GET write request creep | GET-only route documentation accidentally includes non-GET write request smoke | non-GET write request routes are counted/static only and excluded from execution |
| Write-generating creep | Upload/generate/save/reset/delete/rebuild actions are treated as smoke candidates | Evidence statuses explicitly classify these as skipped/excluded |
| Behavior creep | Audit discovers a bug and the milestone starts fixing it | v0.7.13 is docs/read-only only; fixes require separate explicit milestones |
| Public UI creep | Owner-local route documentation expands public UI | No public UI expansion is allowed |
| OCR/course rewrite creep | Smoke/audit work touches OCR/pages/course/Study/Progress behavior | Explicit no rewrite policy is preserved |

## Operational risks

| Risk | Description | Mitigation |
| --- | --- | --- |
| Missing local data | Some GET pages require existing course/report artifacts | Mark as `SKIPPED_NO_EXISTING_DATA` or `PASS_WITH_EXISTING_DATA_ONLY`; do not generate data in this milestone |
| Ambiguous route status | A route might be GET but still sensitive depending on query parameters | Keep route-smoke documentation conservative and manual; do not execute live requests here |
| Evidence overclaim | Documentation claims live results that were not executed | v0.7.13 records only documentation/static validation; no live result claims |
| Validator self-scan false positives | Check scripts can detect their own pattern vocabulary | v0.7.13 scans docs for forbidden command patterns and uses script text checks only where safe |

## Current safe interpretation

The v0.7.9-v0.7.13 packet is an audit/smoke readiness package. It does not prove that every live route works. It proves that the current audit/smoke scope is documented, categorized, and guarded against destructive or distribution actions.

## Next-risk stance

Before any live route smoke, create a separate explicit milestone with:

- GET-only allowed routes
- exact local URL and precondition
- evidence format
- stop conditions
- no non-GET write requests/upload/generate/save/delete/reset/rebuild rule
- no build/ZIP/delivery/distribution rule

Until then, the safe status remains documentation/read-only validation only.

## Mandatory milestone policy

This milestone preserves the required owner-local safety policy:

- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no behavior changes
- no feature changes
- no public UI expansion
- read-only GET-only
- no non-GET write requests
- no upload
- no generate
- no save
- no delete
- no reset
- no server startup
- no live HTTP smoke

This document is documentation-only and static/read-only validation only.

## Exact validator policy phrases

Required exact policy phrase for v0.7.13 validation:

- no upload/generate/save/delete/reset

This phrase confirms that upload, generate, save, delete, and reset actions are excluded from this milestone.




