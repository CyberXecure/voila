# Voila v0.7.13 read-only smoke next-step gate

Milestone: `v0.7.13-owner-local-read-only-smoke-index-consolidation-no-build-no-distribution`

## Purpose

This gate defines what may happen after the v0.7.9-v0.7.12 audit/smoke documentation chain.

It prevents accidental transition from documentation/static validation into live behavior changes, live non-GET write request smoke, build, ZIP packaging, delivery, or distribution.

## Current allowed state

Allowed in v0.7.13:

- documentation updates
- static text validation
- route reference scans as text
- consolidation index
- risk notes
- next-step planning
- read-only validation scripts that do not start the application

Not allowed in v0.7.13:

- build
- ZIP
- delivery
- distribution
- public release
- tester package
- installer
- GitHub release
- external share location distribution
- server startup
- live HTTP smoke
- non-GET write request route execution
- upload
- generate
- save
- delete
- reset
- rebuild
- OCR/pages/course/Study/Progress rewrite
- public UI expansion
- behavior changes

## Next possible milestone types

### Safe continuation option A: final audit packet summary

Possible milestone:

`v0.7.14-owner-local-audit-smoke-final-summary-no-build-no-distribution`

Purpose:

- summarize v0.7.9-v0.7.13 into a final audit packet
- identify unresolved manual smoke gaps
- no live app execution
- no build/distribution

### Safe continuation option B: live GET-only smoke protocol, documentation only

Possible milestone:

`v0.7.14-owner-local-live-get-smoke-protocol-doc-no-build-no-distribution`

Purpose:

- document how a human may run live GET-only smoke manually later
- define prerequisites and stop conditions
- still do not execute the smoke in the milestone

### Separate explicit milestone required for any live run

Any live HTTP smoke must be a separate explicit owner-approved milestone. It must state:

- whether server is already running or may be started
- whether only GET requests are allowed
- which existing local data may be used
- that no non-GET write request/upload/generate/save/delete/reset/rebuild is allowed
- how evidence is recorded
- how to stop immediately on unexpected writes or behavior changes

## Hard stop conditions

Stop immediately if a proposed step requires or implies:

- modifying runtime code
- running non-GET write request requests
- generating course artifacts
- changing OCR/pages/course/Study/Progress behavior
- packaging or delivery
- public UI expansion
- distribution to testers or public users

## Final gate statement

v0.7.13 is not a release milestone and not a live test milestone. It is a documentation/read-only consolidation milestone for owner-local audit and smoke readiness.

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




