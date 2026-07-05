# Voila v0.7.12 Owner-Local Read-Only Route Smoke Evidence Index

Milestone: `v0.7.12-owner-local-read-only-route-smoke-evidence-no-build-no-distribution`
Baseline: `v0.7.11-owner-local-read-only-route-smoke-doc-no-build-no-distribution`
Baseline final main HEAD: `7844aeb`

## Policy

This milestone is documentation and read-only validation only.

Required policy:

- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no behavior changes
- no feature changes
- no public UI expansion
- read-only GET-only
- no POST
- no upload
- no generate
- no save
- no delete
- no reset

## Purpose

v0.7.12 adds an evidence packet for the existing read-only route smoke map prepared in v0.7.11.
It does not execute the app, does not start a server, does not send live requests, and does not change any application state.

The evidence packet is intended to support a later manual owner-local smoke pass where the owner can record observations for already-existing GET/read-only routes only.

## Files in this milestone

- `docs/dev/voila-read-only-route-smoke-evidence-index-v0.7.12.md`
- `docs/dev/voila-read-only-route-smoke-evidence-log-v0.7.12.md`
- `docs/dev/voila-read-only-route-smoke-session-notes-v0.7.12.md`
- `docs/dev/voila-read-only-route-smoke-non-destructive-boundary-v0.7.12.md`
- `scripts/dev/check-voila-read-only-route-smoke-evidence-v0.7.12.ps1`

## Relationship to v0.7.9-v0.7.11

- v0.7.9 created the functional audit baseline and smoke map.
- v0.7.10 created manual smoke evidence scaffolding and risk register.
- v0.7.11 created the GET/read-only route smoke documentation baseline.
- v0.7.12 adds the evidence packet for GET/read-only route smoke observations.

## Evidence status vocabulary

Allowed evidence statuses:

- `PENDING_MANUAL_SMOKE` - evidence row prepared but not executed in this milestone.
- `PASS_MANUAL_GET_ONLY` - owner manually observed expected read-only route behavior.
- `PASS_WITH_EXISTING_DATA_ONLY` - route was observed using existing local data only.
- `SKIPPED_NO_EXISTING_DATA` - route needs an existing course/page/report and was not forced.
- `SKIPPED_OWNER_LOCAL_ONLY` - owner-only route not observed in a shared/public context.
- `SKIPPED_WRITE_OR_DESTRUCTIVE` - route/action is not eligible for v0.7.12.
- `OBSERVED_NON_BLOCKING_NOTE` - observation recorded without making a fix.

## Completion criteria

This milestone is complete when:

- the evidence packet exists;
- the evidence packet references the v0.7.11 route smoke map;
- all evidence rows are clearly marked as manual and read-only;
- write-generating and destructive actions remain explicitly skipped;
- the validation script passes without starting services or making live requests.
