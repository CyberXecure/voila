# v0.8.76 Review Document visual validation save-action plan — no share/no delivery

## Purpose

This milestone defines the controlled owner-local save-action plan for visual validation decisions in `Revizuire document`.

This is a planning-only milestone.

It does not implement a POST endpoint.

It does not modify `services/api/web_app.py`.

It does not write manual decisions.

It does not write Clean Study.

It does not change `/study`.

## Existing validated chain

The save-action implementation must build on the existing chain:

1. `v0.8.67` defines the bbox visual item contract.
2. `v0.8.68` validates bbox visual item artifacts.
3. `v0.8.69` creates real crop artifacts from bbox coordinates.
4. `v0.8.70` creates OCR Math candidates from real crop PNG artifacts.
5. `v0.8.71` defines and validates explicit manual decisions.
6. `v0.8.72` ingests only validated accept/edit items into Clean Study preview.
7. `v0.8.73` defines the visual validation UI plan.
8. `v0.8.74` adds read-only UI in `Revizuire document`.
9. `v0.8.75` smoke-tests the read-only UI through a GET-only TestClient check.

## Future save action

The future implementation should add one controlled owner-local save action for visual validation decisions.

Recommended future route name:

`POST /review-document/visual-validation/save`

This route should be owner-local only.

It should accept only explicit user decisions from the `Revizuire document` visual validation UI.

## Allowed decisions

The only allowed user decisions are:

- `accept`;
- `edit`;
- `ignore`.

No other value is allowed.

No implicit approval is allowed.

Pending items remain pending unless the user explicitly chooses one of the allowed decisions.

## Future form fields

The future UI form should submit only minimal user-controlled fields:

- `course_id`;
- `item_id`;
- `decision`;
- `user_corrected_text`;
- `user_explanation`.

The form must not submit:

- bbox coordinates;
- crop path;
- page image path;
- absolute local path;
- schema version;
- source PDF path;
- ready flag;
- OCR Math status;
- Clean Study eligibility.

Those values must be reloaded server-side from existing local artifacts.

## Server-side lookup rule

The future route must load the current visual item from existing local artifacts.

Preferred input artifact:

`formula_visual_evidence/visual_items.bbox.with-ocrmath-candidates.json`

If a validated artifact already exists, the route may also load:

`formula_visual_evidence/visual_items.bbox.validated.json`

The route must identify the item by `item_id`.

The route must not trust client-submitted crop paths, bbox coordinates, page numbers, or ready flags.

## Validation rule for Acceptă

`accept` is valid only when:

- the item exists in the server-side artifact;
- `crop_exists=true`;
- `crop_path` is present in the server-side artifact;
- `ocr_math_candidate_text` is non-empty;
- the user action is explicit.

The saved item should become:

- `user_decision=accept`;
- `ocr_math_status=validated_by_user`;
- `ready_for_study=true`;
- `user_corrected_text=""` unless previously edited text is intentionally preserved by implementation policy.

## Validation rule for Editează

`edit` is valid only when:

- the item exists in the server-side artifact;
- `crop_exists=true`;
- `crop_path` is present in the server-side artifact;
- `user_corrected_text` is non-empty after trimming;
- the user action is explicit.

The saved item should become:

- `user_decision=edit`;
- `ocr_math_status=validated_by_user`;
- `ready_for_study=true`;
- `user_corrected_text=<trimmed user text>`.

## Validation rule for Ignoră

`ignore` is valid only when:

- the item exists in the server-side artifact;
- the user action is explicit.

The saved item should become:

- `user_decision=ignore`;
- `ocr_math_status=not_applicable`;
- `ready_for_study=false`.

Ignored items must not enter Clean Study.

## Pending rule

Items not included in the submitted decision remain pending.

A missing form submission must not change the item.

A page refresh must not approve any item.

A GET request must not write anything.

## Output artifact

The future save action should write only:

`formula_visual_evidence/visual_items.bbox.validated.json`

It may also write a local summary artifact:

`formula_visual_evidence/visual_items.bbox.validation-summary.json`

The write should be local only.

The write should be atomic or replace-safe.

The write should preserve unrelated items.

## Clean Study rule after save

Saving decisions must not directly write Clean Study.

Clean Study preview should be rebuilt only by the separate controlled ingestion step from v0.8.72 or a future explicit milestone.

Clean Study may include only:

- `ready_for_study=true`;
- `user_decision=accept` or `user_decision=edit`.

Clean Study must exclude:

- `user_decision=ignore`;
- `user_decision=pending`;
- any item without a crop;
- any accepted item without OCR Math candidate text;
- any edited item without corrected text.

## Security and safety plan

The future route must use bounded validation for user-controlled fields.

`course_id` must use a safe ASCII allowlist.

`item_id` must be treated as an identifier only, not as a path.

The route must resolve output directories through the existing safe course-output lookup pattern.

The route must not join client-controlled paths.

The route must not expose stack traces.

The route must return friendly errors.

The route must escape all reflected values in HTML.

The route must redirect only to a safe local `Revizuire document` URL.

## UX plan

The future UI should keep the read-only v0.8.74 card structure and add explicit controls:

- `Acceptă`;
- `Salvează corectarea`;
- `Ignoră`.

The corrected text field should be required only for `edit`.

The explanation field should be optional but preserved when supplied.

After save, the UI should show a clear status:

- `Acceptat`;
- `Corectat`;
- `Ignorat`;
- `În așteptare`.

The UI should show whether the item is `Gata pentru lecție` or `Nu intră încă în lecție`.

## Explicit non-goals for v0.8.76

This milestone does not implement the save action.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

It does not add buttons.

It does not submit a form.

It does not call any route.

It does not start the server.

It does not upload a PDF.

It does not run `/generate`.

It does not run OCR.

It does not run LanguageTool.

It does not run OCR Math.

It does not generate crops.

It does not write `visual_items.bbox.validated.json`.

It does not write `visual_items.clean-study.preview.json`.

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

`v0.8.77-owner-local-review-document-visual-validation-save-action-implementation-no-share-no-delivery`

That milestone may implement the controlled owner-local POST route and a local TestClient POST check, but only after this save-action plan is merged.
