# v0.7.77 Owner-local generate integration from readiness-gated learning pack and browser smoke

Status: PASS_REAL_GENERATE_INTEGRATION_AND_BROWSER_SMOKE

Marker:
VOILA_V0_7_77_GENERATE_INTEGRATION_AND_BROWSER_SMOKE_CHECK=PASS

Baseline:
v0.7.76 completed and merged to protected main at `3fe9f8b`.

## Purpose

This milestone adds the real owner-local `/generate` integration from the readiness-gated rebuilt document learning pack.

It requires:

- `document_learning_pack.json` rebuilt from applied OCR Review evidence.
- `generate_readiness_gate.json` with v0.7.76 PASS.

It changes the local generate path so the learning pack is used by the generated artifacts.

## Real integration

`web_app.py` now detects a valid readiness gate and passes the learning pack into the generator pipeline.

`course_generator.py` uses the learning pack to enrich:

- `course.md`
- `glossary.json`
- `quiz.json`
- `flashcards.json`

`course_polisher.py` uses the learning pack to enrich:

- `course.cleaned.md`

When a learning pack is used, stale `course.cleaned.html` is removed before HTML export so the browser course reflects the updated `course.cleaned.md`.

## Real generate smoke

- `VOILA_V0_7_77_REAL_GENERATE_INTEGRATION_SMOKE=PASS`
- `VOILA_V0_7_77_HTML_REBUILT_FROM_LEARNING_PACK_MARKDOWN=PASS`
- `learning_pack_used=True`
- `learning_pack_glossary_items=14`
- `learning_pack_quiz_items=34`
- `learning_pack_flashcard_items=14`
- `LEARNING_PACK_VISIBLE_IN_HTML=True`
- `GENERATE_INTEGRATION=CHANGED_AND_USED`
- `GENERATOR_ROUTE_CHANGED=True`
- `COURSE_REGENERATION=True`
- `BUILD_PERFORMED=False`
- `ZIP_CREATED=False`
- `SHARE_CREATED=False`
- `DELIVERY_PERFORMED=False`

## Browser smoke

- `VOILA_V0_7_77_BROWSER_SMOKE=PASS`
- `ROUTES_CHECKED=13`
- `GENERATE_INTEGRATION=CHANGED_AND_USED`
- `LEARNING_PACK_VISIBLE_IN_COURSE=True`
- `JSON_ARTIFACTS_USE_LEARNING_PACK=True`
- `BUILD_PERFORMED=False`
- `ZIP_CREATED=False`
- `SHARE_CREATED=False`
- `DELIVERY_PERFORMED=False`

Browser smoke evidence:

`D:\dev\tester-runs\v0777-browser-smoke\V0.7.77-BROWSER-SMOKE.json`

Real generate smoke evidence:

`D:\dev\tester-runs\v0777-real-generate-integration-smoke\V0.7.77-REAL-GENERATE-INTEGRATION-SMOKE.json`

## Explicit non-goals

This milestone does not build.

It does not create ZIP.

It does not share.

It does not deliver.

It does not distribute.

## Policy

Owner-local generate integration only.
Browser smoke completed.
No build.
No ZIP.
No share.
No delivery.
No distribution.

TESTER_READINESS=LOCAL_BROWSER_SMOKE_PASS_NOT_PACKAGED
