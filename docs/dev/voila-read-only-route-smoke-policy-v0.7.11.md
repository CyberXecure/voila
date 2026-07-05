# Voila v0.7.11 read-only route smoke policy

Milestone: `v0.7.11-owner-local-read-only-route-smoke-doc-no-build-no-distribution`

Policy:
- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no behavior changes
- no feature changes
- no OCR/pages/course/Study/Progress rewrite
- no public UI expansion
- read-only
- GET-only route smoke documentation

## Policy intent

v0.7.11 narrows the v0.7.10 manual smoke evidence baseline into a route-focused documentation baseline for existing GET/read-only routes.

It does not perform live automated HTTP smoke testing.
It does not start, stop, build, package, upload, generate, save, delete, reset, rebuild, or distribute anything.

## Permitted changes

Only these repository changes are permitted:
- v0.7.11 runbook document
- v0.7.11 route smoke map document
- v0.7.11 evidence template document
- v0.7.11 policy document
- v0.7.11 read-only validation script

## Forbidden changes

Forbidden:
- runtime behavior changes
- route changes
- UI changes
- feature changes
- OCR pipeline changes
- pages generation changes
- course generation changes
- Study logic changes
- Progress logic changes
- Exam Prep behavior changes
- public UI expansion
- packaging
- distribution
- delivery
- release asset creation
- local course generation
- owner-local data mutation

## Validation policy

The validation script may:
- read v0.7.9 and v0.7.10 baseline documents
- read v0.7.11 documents
- read `services/api/web_app.py` as text
- count route decorators as text
- confirm expected route references exist as text
- confirm policy phrases and evidence vocabulary exist

The validation script must not:
- call a running server
- perform live route requests
- submit forms
- execute application behavior
- start application processes
- create packages
- create archives
- create release assets
- modify owner-local course data

## Interpretation of route smoke

A read-only route smoke observation checks only whether an existing GET route can be observed safely under current behavior.

It is acceptable for data-dependent routes to show safe empty, missing-parameter, missing-course, missing-report, or 404 responses.

A failed manual observation does not authorize any code fix in this milestone.
