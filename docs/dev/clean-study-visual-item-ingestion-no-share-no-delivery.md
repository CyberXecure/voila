# v0.8.72 Clean Study visual item ingestion — no share/no delivery

## Purpose

This milestone adds a controlled local ingestion step from validated bbox visual items into a Clean Study preview artifact.

It is not a default Study integration.

It does not modify the learner Study route.

It does not modify Progress.

## Added capability

The standalone script is:

`scripts/dev/build-clean-study-visual-items-from-bbox.py`

It accepts:

- `visual_items.bbox.validated.json`;
- output root.

It writes:

- `formula_visual_evidence/visual_items.clean-study.preview.json`;
- `formula_visual_evidence/visual_items.clean-study.preview-summary.json`.

## Ingestion rule

Only validated visual items may enter the Clean Study preview artifact.

Included items must have:

- `ready_for_study=true`;
- `user_decision=accept` or `user_decision=edit`;
- `crop_exists=true`;
- non-empty `crop_path`;
- accepted items with non-empty `ocr_math_candidate_text`;
- edited items with non-empty `user_corrected_text`.

Ignored items are excluded.

Pending items are excluded.

## Clean Study item shape

Each preview item contains:

- learner-facing title;
- learner-facing prompt;
- answer text;
- explanation text;
- page number;
- crop image reference;
- source decision.

It does not include bbox coordinates.

## Scope boundary

This milestone does not connect ingestion to the web UI.

It does not modify `services/api/web_app.py`.

It does not modify `/study`.

It does not write Progress.

It does not run `/generate`.

It does not run OCR.

It does not run LanguageTool.

It does not run OCR Math.

It does not create new crops.

## Validation approach

The milestone check creates a synthetic validated visual item artifact outside the repo under `D:\dev\tester-runs`.

The check runs the Clean Study visual ingestion script.

The check validates that:

- accepted item is included;
- edited item is included with corrected text;
- ignored item is excluded;
- pending item is excluded;
- output contains no `bbox` field in learner-facing items;
- Clean Study preview artifact exists;
- preview summary exists;
- `services/api/web_app.py` is unchanged.

## Policy

Controlled local Clean Study visual preview artifact only.

No web route change.

No server required.

No POST.

No upload.

No generate.

No OCR run.

No LanguageTool run.

No OCR Math run.

No crop generation.

No default Study route change.

No Progress write.

No build.

No ZIP.

No OneDrive staging.

No share link.

No tester delivery.

No distribution.

No public release.
