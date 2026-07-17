# v0.7.93 owner-local Crop Editor Formula Evidence audit — no build/no ZIP/no delivery

## Finding

Manual visual validation after v0.7.92 showed that Formula Visual Evidence is technically functional but not sufficient for learning quality:

- Automatic crops can be partial.
- Important definitions and formulas require manual crop selection.
- Cleaned OCR/course HTML is unsatisfactory for formula-heavy content.
- Original-page visual evidence must become a first-class source for definitions and formulas.

## Current local course reality

Course id:

`03-pag-30-34-vectori-trigonometrie`

Observed artifacts:

- `formula_visual_evidence.manifest.json` exists.
- `formula_visual_evidence.edits.json` does not exist yet.
- `figures_hybrid/figures_manifest.hybrid.json` does not exist for this course.
- Figure Crop Editor cannot be reused as-is for this course because the figure manifest source is absent.

## Product decision

Do not create a separate Formula Crop Editor.

Integrate Formula Visual Evidence into the existing Edit crops / Crop Editor workflow as a separate source mode:

- `source=figures` for existing figure crops.
- `source=formula_visual_evidence` for formula/definition crops.

## Required next artifact

`data/output/{course_id}/formula_visual_evidence.edits.json`

Proposed shape:

```json
{
  "artifact": "formula_visual_evidence_edits",
  "course_id": "03-pag-30-34-vectori-trigonometrie",
  "version": "v0.7.94-proposed",
  "source_manifest": "formula_visual_evidence.manifest.json",
  "edits": [
    {
      "edit_id": "manual-p001-001",
      "source": "manual_page_crop",
      "page": 1,
      "bbox": [0, 0, 0, 0],
      "label": "Definiție vector",
      "kind": "definition",
      "status": "pending_owner_review",
      "crop_path": "formula_visual_evidence/edited_crops/manual-p001-001.png",
      "notes": ""
    }
  ],
  "policy": {
    "raw_manifest_modified": false,
    "ocr_rewrite_performed": false,
    "formula_ocr_performed": false,
    "build_performed": false,
    "zip_created": false,
    "share_created": false,
    "delivery_performed": false
  }
}
```

## v0.7.94 recommended implementation

Add a guarded owner-local integration path:

- Course Tools keeps current Formula Visual Evidence viewer.
- Existing Edit crops gains a source mode or link for `formula_visual_evidence`.
- Manual crop uses full rendered page image from `formula_visual_evidence/pages/page-NNN.png`.
- Saving writes only `formula_visual_evidence.edits.json`.
- Edited crops go to `formula_visual_evidence/edited_crops/`.
- Raw `formula_visual_evidence.manifest.json` and raw `formula_visual_evidence/crops/` stay untouched.

## Non-goals

- No OCR rewrite.
- No Formula OCR.
- No OCR Review decision write.
- No Study learning logic change.
- No BKT logic change.
- No Progress logic change.
- No generator course rewrite.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
