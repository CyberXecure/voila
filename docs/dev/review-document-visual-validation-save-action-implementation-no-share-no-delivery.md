# v0.8.77 Review Document visual validation save-action implementation — no share/no delivery

## Purpose

This milestone implements the controlled owner-local save action for visual validation decisions in `Revizuire document`.

It implements:

`POST /review-document/visual-validation/save`

The route saves explicit visual validation decisions only.

It does not write Clean Study.

It does not change `/study`.

## Allowed decisions

The route accepts only:

- `accept`;
- `edit`;
- `ignore`.

No implicit approval is allowed.

Pending items remain pending unless the user explicitly submits one of the allowed decisions.

## Accepted form fields

The route accepts only minimal user-controlled form fields:

- `course_id`;
- `item_id`;
- `decision`;
- `user_corrected_text`;
- `user_explanation`.

The route does not trust client-submitted crop paths, bbox coordinates, page numbers, OCR Math status, ready flags, or Clean Study eligibility.

## Server-side artifact lookup

The route loads existing local artifacts server-side from the safe course output directory.

It reads:

- `formula_visual_evidence/visual_items.bbox.validated.json` when present;
- otherwise `formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json`.

It writes only:

- `formula_visual_evidence/visual_items.bbox.validated.json`;
- `formula_visual_evidence/visual_items.bbox.validation-summary.json`.

## Decision rules

`accept` requires:

- item exists;
- `crop_exists=true`;
- server-side `crop_path` is present;
- server-side `ocr_math_candidate_text` is non-empty;
- explicit POST action.

`edit` requires:

- item exists;
- `crop_exists=true`;
- server-side `crop_path` is present;
- submitted `user_corrected_text` is non-empty after trimming;
- explicit POST action.

`ignore` requires:

- item exists;
- explicit POST action.

## Saved state

`accept` saves:

- `user_decision=accept`;
- `ocr_math_status=validated_by_user`;
- `ready_for_study=true`.

`edit` saves:

- `user_decision=edit`;
- `ocr_math_status=validated_by_user`;
- `ready_for_study=true`;
- trimmed `user_corrected_text`.

`ignore` saves:

- `user_decision=ignore`;
- `ocr_math_status=not_applicable`;
- `ready_for_study=false`.

## Clean Study boundary

This save action does not write Clean Study.

Clean Study preview remains a separate controlled ingestion step.

Ignored and pending items must not enter Clean Study.

## Security and safety

The implementation uses bounded form parsing.

`course_id` and `item_id` use a safe ASCII allowlist.

`item_id` is used only as an identifier, never as a path.

The route resolves course output under `data/output`.

The route does not join client-controlled file paths.

The route does not redirect to user-controlled URLs.

The route returns friendly HTML responses.

Reflected values are escaped.

Stack traces are not exposed.

## Validation

The check uses FastAPI TestClient.

It creates a temporary fixture under `data/output/v0877-visual-save-action-smoke`.

It performs POST requests for:

- accept;
- edit;
- ignore;
- invalid edit without corrected text.

It verifies:

- validated artifact exists;
- validation summary exists;
- accept becomes ready for study;
- edit uses corrected text and becomes ready for study;
- ignore remains excluded;
- pending remains pending;
- invalid edit is rejected;
- Clean Study is not written;
- `/study` is not changed;
- no server is started;
- no upload/generate/OCR/LanguageTool/OCR Math/crop generation/build/ZIP/share/delivery occurs.

## Scope boundary

This milestone may modify `services/api/web_app.py` for the controlled POST save action.

It does not add UI buttons.

It does not perform a browser server smoke.

It does not start uvicorn.

It does not start LanguageTool.

It does not upload a PDF.

It does not run `/generate`.

It does not run OCR.

It does not run LanguageTool.

It does not run OCR Math.

It does not generate crops.

It does not write Clean Study.

It does not write Progress.

It does not build.

It does not create a ZIP.

It does not create OneDrive staging.

It does not create a share link.

It does not deliver to testers.

It does not distribute anything.

It does not create a public release.

## Recommended next slice

The next milestone should be:

`v0.8.78-owner-local-review-document-visual-validation-form-controls-no-share-no-delivery`

That milestone can add UI form controls/buttons that submit to the controlled save action.
