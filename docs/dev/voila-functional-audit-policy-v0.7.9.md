# Voila Functional Audit Policy v0.7.9

Milestone: `v0.7.9-owner-local-functional-audit-baseline-no-build-no-distribution`

Baseline: `v0.7.8-owner-local-ocr-math-report-audit-trail-doc-no-build-no-distribution`

Expected protected main HEAD at milestone start: `a2ad6ba`

## Policy summary

v0.7.9 is an audit baseline milestone. It is not a behavior milestone, not a feature milestone, not a tester package milestone, and not a release milestone.

## Mandatory constraints

- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no feature changes
- no OCR/pages/course/Study/Progress rewrite
- no public UI expansion
- no behavior changes

## Allowed changes

Only the following repository changes are allowed:

- add functional audit inventory documentation
- add functional smoke map documentation
- add functional test checklist documentation
- add functional audit policy documentation
- add a read-only/non-destructive validation script

## Forbidden changes

The milestone must not change runtime behavior.

Forbidden areas include, but are not limited to:

- OCR behavior
- pages extraction behavior
- course generation behavior
- cleaned course behavior
- Study behavior
- Progress behavior
- Exam Prep behavior
- upload/generate/regenerate behavior
- OCR Math report generation behavior
- route behavior
- public UI behavior
- public UI scope
- package/build/release/share behavior

## Allowed validation behavior

The v0.7.9 validation script may:

- check that required v0.7.9 documents exist
- check that required headings exist
- check that required policy phrases exist
- read source files as text
- list route decorators as text
- reject forbidden build/package/release/upload command patterns in new v0.7.9 files
- print a PASS/FAIL summary

The validation script must not:

- start the application
- stop the application
- import application modules
- run OCR
- upload files
- generate course artifacts
- regenerate course artifacts
- submit quiz/study/exam answers
- write progress/session data
- create a build
- create an archive package
- publish a release
- upload or share assets

## Server policy

v0.7.9 does not require starting the local server.

If an operator manually chooses to run GET-only checks against an already running owner-local server, that activity is outside the automated validation script and must remain read-only.

## Evidence policy

v0.7.9 repository evidence is limited to docs and validation output.

No release asset, ZIP package, tester package, installer, GitHub release, public upload, OneDrive share, or delivery artifact is allowed.

## Next milestone boundary

A later milestone may collect manual smoke evidence using the v0.7.9 smoke map, but that must be separate and explicitly scoped.

Recommended next milestone after v0.7.9:

`v0.7.10-owner-local-manual-smoke-evidence-no-build-no-distribution`

v0.7.10 should still preserve the same no-build/no-ZIP/no-delivery/no-distribution policy unless explicitly changed by the owner.