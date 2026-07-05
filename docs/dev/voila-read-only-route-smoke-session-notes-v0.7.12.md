# Voila v0.7.12 Read-Only Route Smoke Session Notes

Milestone: `v0.7.12-owner-local-read-only-route-smoke-evidence-no-build-no-distribution`

## Policy

- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no behavior changes
- read-only GET-only
- no POST
- no upload
- no generate
- no save
- no delete
- no reset

## Session notes purpose

This document captures how a future manual owner-local route smoke session should be recorded.
It is not an instruction to start services, run a build, package the app, or distribute anything.

## Allowed manual observation context

A future manual evidence session may use an already-running owner-local Voila instance.
The owner may open existing GET/read-only pages and record visible results.
The owner must not create missing data just to make a route observable.

## Suggested manual note fields

For each route observation, record:

- absolute date and local time;
- current main HEAD;
- route opened;
- whether existing data was already present;
- visible outcome;
- status from the approved evidence vocabulary;
- non-blocking notes, if any;
- explicit confirmation that no write action was triggered.

## Do-not-cross boundary

Do not click buttons or submit forms that perform any of the following:

- upload;
- generate;
- regenerate;
- answer;
- save;
- delete;
- reset;
- rebuild.

If a route requires one of those actions to become meaningful, leave it as `SKIPPED_NO_EXISTING_DATA`.

## Current v0.7.12 session status

This milestone prepares the evidence packet only.
No live HTTP route smoke execution is claimed by this document.

Current status: `PENDING_MANUAL_SMOKE`.
