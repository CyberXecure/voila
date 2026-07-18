# v0.7.95 Manual Learning Evidence UI Design — no build/no ZIP/no delivery

## Purpose

This milestone designs the first owner-local Manual Learning Evidence UI.

It does not implement the UI yet.

The design follows the v0.7.94 Voila Direction Charter:

- Voila is a human-in-the-loop verified learning tool.
- Voila is not a fully automatic AI course generator.
- AI assists. The owner validates.
- Learning Pack must consume accepted owner-verified evidence.
- Learning content must be traceable to source page, crop, verified text, and owner explanation.

## Product concept

The owner opens a real document page, selects a region manually, then confirms the learning meaning.

The selected region can be:

- formula
- definition
- example
- theorem
- diagram
- drawing
- note

The owner then adds:

- title
- kind
- verified_text
- explanation_ro
- source_status
- source_note
- status

The crop image is visual evidence. The owner-confirmed metadata is the learning interpretation.

## Future route proposal

Proposed future owner-local route:

`/owner/manual-learning-evidence/{course_id}`

Optional query parameters:

- `page=1`
- `edit_id=...`

The route should run inside the main Voila app on port `8787`.

It should not use the old external Crop Editor on port `8790`.

## UI layout proposal

The UI should have four main areas:

### 1. Source page selector

- Course id
- PDF name
- Current page number
- Previous page
- Next page
- Page image rendered from the original source

### 2. Manual crop canvas

The owner selects a rectangle with the mouse over the rendered page image.

The UI should show:

- selected bbox
- crop preview
- reset selection
- save crop

### 3. Evidence metadata form

Required fields:

- title
- kind
- verified_text
- explanation_ro
- source_status
- source_note
- status

Allowed `kind` values:

- formula
- definition
- example
- theorem
- diagram
- drawing
- note

Allowed `source_status` values:

- verified
- uncertain
- possible_source_error

Allowed `status` values:

- pending_owner_review
- accepted_owner_verified
- rejected_noise

### 4. Evidence list

The UI should show existing manual evidence items:

- title
- kind
- page
- source_status
- status
- crop preview
- edit
- mark accepted
- mark noise
- mark possible source error

## Canonical artifact

The future canonical artifact is:

`manual_learning_evidence.json`

Proposed path:

`data/output/{course_id}/manual_learning_evidence.json`

Proposed crop folder:

`data/output/{course_id}/manual_learning_evidence/crops/`

## Proposed artifact shape

```json
{
  "artifact": "manual_learning_evidence",
  "course_id": "03-pag-30-34-vectori-trigonometrie",
  "source_pdf": "03-pag-30-34-vectori-trigonometrie.pdf",
  "version": "v0.7.96-proposed",
  "items": [
    {
      "evidence_id": "manual-p001-001",
      "page": 1,
      "bbox": [0, 0, 0, 0],
      "crop_path": "manual_learning_evidence/crops/manual-p001-001.png",
      "kind": "formula",
      "title": "Modulul vectorului AB",
      "verified_text": "|AB| = sqrt((x - x0)^2 + (y - y0)^2)",
      "explanation_ro": "Formula calculează distanța dintre două puncte în plan.",
      "source_status": "verified",
      "source_note": "",
      "status": "accepted_owner_verified"
    }
  ],
  "policy": {
    "owner_verified_required": true,
    "ai_assists_owner_validates": true,
    "raw_ocr_rewrite_performed": false,
    "formula_ocr_performed": false,
    "build_performed": false,
    "zip_created": false,
    "share_created": false,
    "delivery_performed": false
  }
}
```

## Learning Pack contract

Learning Pack must not treat image pixels alone as trusted learning meaning.

Learning Pack may consume an item only when:

- `status` is `accepted_owner_verified`
- `title` is present
- `kind` is present
- `verified_text` or `explanation_ro` is present
- `crop_path` is present
- `page` is present
- `source_status` is present

The crop is evidence. The owner metadata is the interpretation.

## Source mistake support

The UI must allow:

`source_status = possible_source_error`

This is required because books, diagrams, formulas, OCR output, and source material can contain mistakes.

Voila should preserve the owner note rather than pretending the source is always correct.

## AI assistance boundary

AI may later assist by suggesting:

- title
- kind
- verified_text formatting
- explanation_ro
- possible source inconsistency
- quiz/study questions from accepted evidence

AI must not silently create trusted learning blocks without owner acceptance.

## v0.7.96 recommended next implementation

The next implementation milestone should be small:

`v0.7.96-owner-local-manual-learning-evidence-ui-skeleton-no-build-no-zip-no-delivery`

Recommended scope:

- add read-only route skeleton
- show course id
- show first rendered source page
- show empty metadata form
- show no save yet or save disabled
- no Learning Pack integration yet

## Non-goals

- No UI implementation in this milestone.
- No manual crop implementation.
- No save endpoint.
- No Learning Pack integration.
- No Course generation change.
- No Study change.
- No Progress change.
- No OCR rewrite.
- No Formula OCR.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
