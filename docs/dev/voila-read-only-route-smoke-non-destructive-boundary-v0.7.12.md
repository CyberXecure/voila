# Voila v0.7.12 Non-Destructive Boundary for Read-Only Route Smoke Evidence

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

## Boundary statement

v0.7.12 is an evidence documentation milestone.
It must not evolve into a fix milestone, UI change milestone, test automation milestone, or packaging milestone.

## Permitted

- add evidence documentation;
- add evidence vocabulary;
- reference existing routes from v0.7.11;
- classify route evidence as pending, skipped, or manually observed;
- run static/read-only validation over repository text.

## Not permitted

- modify runtime behavior;
- change route handlers;
- change UI;
- expand public UI;
- start services;
- run live HTTP checks;
- run write paths;
- generate new course/OCR/progress/report artifacts;
- package or distribute anything.

## Handling observations

If manual route smoke later reveals an issue, do not fix it inside this milestone.
Record it as `OBSERVED_NON_BLOCKING_NOTE` and create a separate future milestone proposal.

## Handling missing data

Missing data is not a failure for v0.7.12.
Use `SKIPPED_NO_EXISTING_DATA` when a route needs existing local course/OCR/report data.
Do not create missing data inside this milestone.
