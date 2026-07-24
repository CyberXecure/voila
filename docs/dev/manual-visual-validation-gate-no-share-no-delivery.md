# v0.8.71 Manual visual validation gate — no share/no delivery

## Purpose

This milestone adds a controlled local manual validation gate for bbox visual OCR Math candidates.

It converts candidate-only visual items into validated visual items only when explicit local decisions are provided.

## Added capability

The standalone script is:

`scripts/dev/apply-bbox-visual-validation-decisions.py`

It accepts:

- `visual_items.bbox.with-ocrmath-candidates.json`;
- a local decisions JSON file;
- an output root.

It writes:

- `formula_visual_evidence/visual_items.bbox.validated.json`;
- `formula_visual_evidence/visual_items.bbox.validation-summary.json`.

## Decision model

Allowed decisions are:

- `accept`
- `edit`
- `ignore`

No implicit approval is allowed.

Items without decisions remain:

- `user_decision=pending`;
- `ready_for_study=false`.

## Gate rules

For `accept`:

- crop must exist;
- OCR Math candidate text must be present;
- `ocr_math_status` becomes `validated_by_user`;
- `user_decision` becomes `accept`;
- `ready_for_study` becomes `true`.

For `edit`:

- crop must exist;
- `user_corrected_text` must be non-empty;
- `ocr_math_status` becomes `validated_by_user`;
- `user_decision` becomes `edit`;
- `ready_for_study` becomes `true`.

For `ignore`:

- `user_decision` becomes `ignore`;
- `ocr_math_status` becomes `not_applicable`;
- `ready_for_study` remains `false`.

Pending and ignored items must not feed Study.

## Scope boundary

This milestone does not connect the gate to the web UI.

It does not modify `services/api/web_app.py`.

It does not run `/generate`.

It does not run OCR.

It does not run LanguageTool.

It does not run OCR Math.

It does not ingest validated items into Study.

It does not write Progress.

## Validation approach

The milestone check creates a synthetic local candidate artifact outside the repo under `D:\dev\tester-runs`.

The check creates local manual decisions outside the repo.

The check validates that:

- accepted items become ready for Study;
- edited items become ready for Study only with corrected text;
- ignored items remain blocked from Study;
- undecided items remain pending and blocked from Study;
- the tracked v0.8.68 validator accepts the validated artifact;
- invalid edit without corrected text is rejected;
- `services/api/web_app.py` is unchanged.

## Policy

Controlled local manual visual validation gate only.

No web route change.

No server required.

No POST.

No upload.

No generate.

No OCR run.

No LanguageTool run.

No OCR Math run.

No Study ingestion.

No Study write.

No Progress write.

No build.

No ZIP.

No OneDrive staging.

No share link.

No tester delivery.

No distribution.

No public release.
