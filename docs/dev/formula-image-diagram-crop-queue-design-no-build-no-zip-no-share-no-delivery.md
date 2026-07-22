# v0.8.46 Formula/image/diagram/crop queue design — no build/no ZIP/no share/no delivery

## Purpose

This milestone designs the learner-facing review queue for the third step of the new `Revizuire document` shell:

`Formule și imagini`

It follows:

- v0.8.43 Student workflow UX reset charter
- v0.8.44 Review Document shell design
- v0.8.45 OCR + LanguageTool review queue design

This is design/documentation/check only.

No UI implementation is performed in this milestone.

## Product context

Voila! — Documentele tale, lecții clare

The learner should not see a technical crop editor or formula diagnostics console.

The learner should see a guided visual review flow.

Formula detection, image detection, diagram detection, crop extraction, and any OCR/visual helpers run in the background.

The learner only decides what the selected visual area means and whether it should become learning material.

## Target user

The queue is designed for:

- a 15-year-old student
- a 17-year-old preparing for an exam
- an adult without technical knowledge
- a teacher or parent reviewing visual content before Study

The user should not need to understand bbox, crop IDs, image artifact paths, Formula OCR debug state, visual evidence IDs, route names, JSON files, or dry-runs.

## Place in the shell

Parent shell:

`Revizuire document`

Covered step:

- `Formule și imagini`

Related previous steps:

- `Text detectat`
- `Corecturi sugerate`

Related later steps:

- `Noțiuni importante`
- `Gata pentru studiu`
- clean Study mode

## Learner-facing goal

Turn visual material from the document into clear study-ready items.

The learner-facing question is:

`Ce reprezintă această zonă și merită să intre în lecție?`

## Unified visual queue concept

The visual queue should unify:

- formulas
- diagrams
- drawings
- images
- tables
- graphs
- scanned visual fragments
- manually selected crop areas

The learner should not switch between separate product surfaces named:

- OCR Math report
- Formula visual evidence
- Crop Editor
- Manual Learning Evidence
- Manual Study preview

Internally, these systems can still exist.

Externally, the learner sees one guided flow: `Formule și imagini`.

## Queue concept

The queue should be page-based and visual-area-based.

A queue item represents a candidate visual region from a source page.

Each queue item should show:

- document name
- page number
- page image or preview
- selected visual area
- crop preview
- friendly type selector
- explanation input
- source confirmation
- simple status
- next action

The learner should move through one clear visual item at a time.

## Suggested queue item fields

Conceptual design only.

A learner-facing visual queue item may contain:

- `page`
- `visual_preview`
- `selected_area`
- `item_type`
- `short_title`
- `what_it_represents`
- `learner_explanation`
- `source_page`
- `learner_status`
- `language`
- `notes`

Technical fields may exist internally, but must not be primary learner content.

## Learner-facing statuses

Use simple statuses:

- `De verificat`
- `Selectat`
- `Explicat`
- `Gata pentru lecție`
- `Ignorat`

Avoid primary learner statuses like:

- bbox_ready
- crop_saved
- formula_ocr_pending
- visual_evidence_id
- source_bbox
- artifact_ready
- dry_run
- route_ok

## Step — Formule și imagini

Purpose:

Help the learner verify and explain visual material before it becomes learning material.

Learner-facing labels:

- Formule și imagini
- Pagina sursă
- Selectează zona din pagină
- Ce reprezintă?
- Tip de conținut
- Titlu scurt
- Explicație pe înțeles
- Salvează pentru lecție
- Ignoră zona
- Continuă

Learner-facing actions:

- Selectează zona
- Ajustează selecția
- Marchează ca formulă
- Marchează ca diagramă
- Marchează ca imagine
- Marchează ca tabel
- Marchează ca grafic
- Adaugă explicația
- Salvează pentru lecție
- Ignoră zona
- Continuă

The learner should see:

- source page
- selected area
- readable crop preview
- item type
- friendly explanation prompt
- clear save/ignore/continue buttons

The learner should not see as primary content:

- raw bbox values
- crop file paths
- visual evidence IDs
- Formula OCR logs
- OCR Math diagnostics
- JSON artifact names
- route names
- dry-run state
- package policy markers

## Friendly item types

The learner-facing type selector should include:

- Formulă
- Diagramă
- Imagine
- Tabel
- Desen
- Grafic
- Observație importantă

The selected type should help Study later present the item in a clean way.

## Formula handling

Formula areas should be treated as visual learning material, not as raw OCR math diagnostics.

Learner-facing formula flow:

1. Selectează formula din pagină
2. Spune ce reprezintă formula
3. Adaugă explicația
4. Salvează pentru lecție

The learner should be able to explain a formula even if formula OCR is imperfect.

The main learner flow should not require perfect Formula OCR before a formula can be used for Study.

Formula OCR or symbolic extraction can remain diagnostic/background support.

## Diagram, drawing, graph, and table handling

Non-text visual areas should have the same friendly flow:

1. Selectează zona
2. Alege tipul
3. Scrie ce arată
4. Adaugă explicația
5. Salvează pentru lecție

Examples:

- a geometry diagram
- a function graph
- a chemistry scheme
- a physics drawing
- a table from a textbook
- a scanned image fragment

The learner should not need to know whether the system calls it a crop, visual evidence, page image, or OCR artifact.

## Explanation model

Manual explanation entry is not metadata editing.

Use learner-facing labels:

- Titlu scurt
- Ce reprezintă?
- Explicație pe înțeles
- De ce este important?
- Pagina sursă
- Salvează pentru lecție

Avoid labels:

- metadata
- bbox
- verified_text
- source_status
- source_note
- visual_evidence_id
- crop_path
- artifact

## Source confirmation

The learner should always see where the visual item comes from.

Learner-facing source label:

`Sursa: pagina X`

The source should be visible in Study later, but internal source IDs should not be visible in the main learner flow.

## Language consistency

The queue must respect the lesson language selected in `Revizuire document`.

Supported first-level options:

- Română
- English

If the lesson language is Română:

- labels should be Romanian
- explanation prompts should be Romanian
- learner notes should be encouraged in Romanian
- Study handoff should remain Romanian

If the lesson language is English:

- labels should be English
- explanation prompts should be English
- learner notes should be encouraged in English
- Study handoff should remain English

No mixed RO/EN learner flow.

Technical diagnostics can remain in English if needed, but not the main learner path.

## Background engine behavior

Visual engines should run in the background.

Background engines may include:

- page rendering
- formula detection
- image detection
- diagram detection
- table detection
- crop extraction
- Formula OCR
- OCR Math diagnostics
- visual evidence storage
- manual evidence storage
- study adapter

Learner-facing progress labels:

- Se caută formule și imagini
- Se pregătesc paginile
- Selectează zona importantă
- Adaugă explicația
- Zona este gata pentru lecție

The learner should not need to manually start:

- crop editor service
- Formula OCR
- OCR Math report
- artifact generation
- dry-run exporter

These should be orchestrated behind the learner workflow.

## Queue layout

Recommended layout:

1. Header
   - Revizuire document
   - document name
   - lesson language
   - progress summary

2. Step indicator
   - Text detectat
   - Corecturi sugerate
   - Formule și imagini
   - Noțiuni importante
   - Gata pentru studiu

3. Visual workspace
   - page image
   - selection overlay
   - crop preview

4. Explanation panel
   - type selector
   - short title
   - what it represents
   - explanation field
   - source page confirmation

5. Guidance panel
   - what the learner is reviewing
   - what to do next
   - why this matters for Study

6. Diagnostic tehnic
   - collapsed by default
   - owner/developer only

## Primary buttons

Preferred learner-facing buttons:

- Selectează zona
- Ajustează selecția
- Adaugă explicația
- Salvează pentru lecție
- Ignoră zona
- Continuă
- Înapoi

Avoid primary buttons:

- Save metadata
- Save bbox
- Write crop artifact
- Export dry-run
- Accept visual evidence ID
- Run Formula OCR
- Generate JSON

## Readiness for Study

A visual item becomes ready for downstream learning only after the learner has:

- selected or confirmed the visual area
- chosen a friendly item type
- provided or confirmed a short title
- provided a learner-facing explanation
- confirmed the source page
- saved the item for the lesson

The queue must distinguish:

- useful saved visual item
- visual item needing explanation
- ignored visual/noise item
- unresolved visual item

Unresolved visual items should not silently become clean Study material.

## Diagnostic boundary

Diagnostic may show technical details, but only behind `Diagnostic tehnic`.

Diagnostic may include:

- bbox
- crop paths
- visual evidence IDs
- OCR Math report paths
- Formula OCR state
- image detection state
- source IDs
- JSON paths
- route names
- dry-run state
- package policy markers

Diagnostic must be collapsed by default.

Diagnostic must not be required to complete the learner workflow.

## Handoff contract

This queue should eventually produce or feed clean visual study items.

Study-facing clean visual items should include:

- source page
- item type
- short title
- learner explanation
- visual preview or crop reference
- lesson language
- ignored/not useful state

Study should not receive unresolved visual regions as if they were verified learning material.

Study should not expose raw bbox or visual evidence IDs in the main learner view.

## Non-goals

This milestone does not implement the queue.

This milestone does not change the current UI.

This milestone does not change `services/api/web_app.py`.

This milestone does not add a route.

This milestone does not add a POST endpoint.

This milestone does not start or stop OCR.

This milestone does not start or stop LanguageTool.

This milestone does not perform OCR.

This milestone does not perform LanguageTool correction.

This milestone does not perform Formula OCR.

This milestone does not perform crop extraction.

This milestone does not write crop files.

This milestone does not write visual evidence artifacts.

This milestone does not rewrite OCR text.

This milestone does not write Progress.

This milestone does not mark answers.

This milestone does not create Study cards.

This milestone does not rebuild a package.

This milestone does not create a ZIP.

This milestone does not create a share.

This milestone does not deliver anything.

## Boundary

No build.

No ZIP.

No package rebuild.

No OneDrive copy.

No share.

No delivery.

No distribution.

No public release.

No route changes.

No POST endpoints.

No Study behavior change.

No Progress write.

No answer marking.

No OCR rewrite.

No Formula OCR.

No crop writing.

No visual evidence writing.

## Recommended next

v0.8.47 — friendly explanation form design.

v0.8.48 — clean Study mode design.

v0.8.49 — owner personal full workflow test after implementation.

## Final decision

The formula/image/diagram/crop queue is not a technical crop editor.

It is a guided learner workflow that turns visual document material into clear study-ready explanations.
