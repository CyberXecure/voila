# v0.7.84 Study items preview guarded Study integration

Status: PASS_STUDY_ITEMS_PREVIEW_GUARDED_STUDY_INTEGRATION

Marker:
VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_GUARDED_INTEGRATION_CHECK=PASS

Baseline:
v0.7.83 completed and merged to protected main at `b281179`.

## Purpose

This milestone integrates `study_items.preview.json` into `/study` behind a guarded quality gate.

Study uses the preview items only when:

- `study_items.preview.json` exists
- artifact is `study_items_preview`
- quality gate is `PASS`

If preview is missing or invalid, Study falls back to existing `quiz.study.json` / `quiz.json`.

## Scope

Changed:

- `services/api/study_engine.py`
- `services/api/web_app.py`

Behavior:

- `load_questions(output_dir)` tries guarded preview items first.
- Preview items are normalized into the existing Study question shape.
- `/study` displays the preview item question directly.
- Fallback without preview still works.

## Validation

Evidence:

`D:\dev\tester-runs\v0784-study-items-preview-guarded-study-integration\V0.7.84-STUDY-PREVIEW-INTEGRATION-SOURCE-INSPECT.json`

`D:\dev\tester-runs\v0784-study-items-preview-guarded-study-integration\V0.7.84-STUDY-ENGINE-SOURCE-INSPECT.json`

`D:\dev\tester-runs\v0784-study-items-preview-guarded-study-integration\V0.7.84-STUDY-ITEMS-PREVIEW-GUARDED-INTEGRATION-SMOKE.json`

Validated markers:

- `VOILA_V0_7_84_STUDY_ITEMS_PREVIEW_GUARDED_INTEGRATION_SMOKE=PASS`
- `loaded_question_count=27`
- `view_total_questions=27`
- `study_items_preview_used=True`
- `question_source=study_items.preview.json`
- `study_route_status=200`
- `preview_question_visible_in_study=True`
- `display_builder_preserves_preview_question=True`
- `hint_visible=True`
- `explanation_visible=True`
- `legacy_prompt_visible=False`
- `legacy_short_answer_visible=False`
- `fallback_without_preview_works=True`
- `question_generation_changed=False`
- `bkt_logic_changed=False`
- `progress_logic_changed=False`
- `generator_logic_changed=False`
- `BUILD_PERFORMED=False`
- `ZIP_CREATED=False`
- `SHARE_CREATED=False`
- `DELIVERY_PERFORMED=False`

## Policy

Owner-local guarded Study integration only.

No question generation change.
No BKT logic change.
No Progress logic change.
No generator logic change.
No build.
No ZIP.
No share.
No delivery.
No distribution.

TESTER_READINESS=LOCAL_STUDY_ITEMS_PREVIEW_GUARDED_INTEGRATION_PASS_NOT_PACKAGED
