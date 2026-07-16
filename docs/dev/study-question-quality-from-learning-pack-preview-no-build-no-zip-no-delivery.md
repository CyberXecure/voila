# v0.7.81 Study question quality from learning pack preview

Status: PASS_STUDY_ITEMS_PREVIEW_QUALITY

Marker:
VOILA_V0_7_81_STUDY_QUESTION_QUALITY_PREVIEW_CHECK=PASS

Baseline:
v0.7.80 completed and merged to protected main at `e86d419`.

## Purpose

This milestone adds a deterministic local Study item preview generator.

It improves the quality of Study question candidates by deriving pedagogical items from the verified document learning pack instead of using mechanical legacy prompts.

## Scope

Added:

- `services/api/study_item_generator.py`

The generator reads:

- `document_learning_pack.json`
- `generate_readiness_gate.json`

The generator writes local preview output:

- `study_items.preview.json`

## Output model

Each preview item includes:

- `concept_id`
- `term`
- `question_type`
- `question`
- `expected_answer`
- `hint`
- `explanation`
- `source_pdf_pages`
- `source_evidence`
- `generation_method`
- `integration_status`

## Quality result

Validated on real course:

`03-pag-30-34-vectori-trigonometrie`

Results:

- `item_count=27`
- `concept_count=14`
- `covered_concept_count=14`
- `bad_prompt_hit_count=0`
- `copied_answer_hit_count=0`
- `too_short_explanation_hit_count=0`
- `missing_hint_hit_count=0`
- `raw_notation_visible_fields=False`
- `vectori_opusi_template_active=True`

## Evidence

Source inspect:

`D:\dev\tester-runs\v0781-study-question-quality-preview\V0.7.81-STUDY-QUESTION-QUALITY-SOURCE-INSPECT.json`

Schema inspect:

`D:\dev\tester-runs\v0781-study-question-quality-preview\V0.7.81-LEARNING-PACK-SCHEMA-INSPECT.json`

Content sample:

`D:\dev\tester-runs\v0781-study-question-quality-preview\V0.7.81-STUDY-ITEM-SOURCE-CONTENT-SAMPLE.json`

Quality smoke:

`D:\dev\tester-runs\v0781-study-question-quality-preview\V0.7.81-STUDY-ITEMS-PREVIEW-QUALITY-SMOKE.json`

Visible fields smoke:

`D:\dev\tester-runs\v0781-study-question-quality-preview\V0.7.81-STUDY-ITEMS-PREVIEW-VISIBLE-FIELDS-SMOKE.json`

## Important policy

This is preview only.

No `/study` integration.
No BKT logic change.
No Study state change.
No Progress change.
No course generation integration.
No build.
No ZIP.
No share.
No delivery.
No distribution.

Validated markers:

- `VOILA_V0_7_81_STUDY_ITEMS_PREVIEW_GENERATED=PASS`
- `VOILA_V0_7_81_STUDY_ITEMS_PREVIEW_QUALITY_SMOKE=PASS`
- `VOILA_V0_7_81_STUDY_ITEMS_PREVIEW_VISIBLE_FIELDS_SMOKE=PASS`
- `bad_prompt_hit_count=0`
- `copied_answer_hit_count=0`
- `too_short_explanation_hit_count=0`
- `missing_hint_hit_count=0`
- `raw_notation_visible_fields=False`
- `question_generation_changed=False`
- `bkt_logic_changed=False`
- `study_integration_changed=False`
- `preview_only=True`
- `BUILD_PERFORMED=False`
- `ZIP_CREATED=False`
- `SHARE_CREATED=False`
- `DELIVERY_PERFORMED=False`

TESTER_READINESS=LOCAL_STUDY_QUESTION_QUALITY_PREVIEW_PASS_NOT_INTEGRATED
