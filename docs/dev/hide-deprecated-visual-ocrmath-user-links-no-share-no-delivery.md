# v0.8.66 Hide deprecated visual/OCR Math user links — no share/no delivery

## Purpose

This milestone hides deprecated visual/OCR Math entry points from the primary user-facing navigation.

It does not delete routes.

It does not delete engines.

It does not delete artifacts.

It is a display-only cleanup after the v0.8.65 pipeline plan.

## Product decision preserved

The canonical user-facing flow remains:

`PDF -> OCR text -> LanguageTool suggestions -> page image -> bbox -> real crop -> OCR Math on crop -> manual validation -> clean Study`

## Hidden from primary user-facing flow

- Home link to old `figures_hybrid/figures_hybrid.html`
- Home link to old `figures/figures.html`
- Home link to old `/edit-crops`
- Course Tools card `OCR Math Diagnostic`
- Course Tools card `Figures`
- Course Tools card `Edit crops`
- Injected bottom/navigation link `OCR Math` to the global OCR Math report

## Still preserved as owner-local technical capability

The following routes/files may still exist temporarily:

- `/owner/ocr-math-report/{course_id}/view`
- `/edit-crops`
- `/view-figures`
- `ocr_math_report.json`
- `ocr_math_report.md`
- `figures_hybrid`
- `figures.html`

They are not the primary user-facing learning flow.

## Policy

Display-only UI/navigation change.

No OCR logic change.

No LanguageTool logic change.

No crop generation logic change.

No Study logic change.

No Progress logic change.

No server required.

No POST.

No upload.

No generate.

No OCR run.

No LanguageTool run.

No crop generation.

No build.

No ZIP.

No OneDrive staging.

No share link.

No tester delivery.

No distribution.

No public release.
