# v0.8.47 Friendly explanation form design — no build/no ZIP/no share/no delivery

## Purpose

This milestone designs the shared learner-facing explanation form used inside the new `Revizuire document` shell.

It follows:

- v0.8.43 Student workflow UX reset charter
- v0.8.44 Review Document shell design
- v0.8.45 OCR + LanguageTool review queue design
- v0.8.46 Formula/image/diagram/crop queue design

This is design/documentation/check only.

No UI implementation is performed in this milestone.

## Product context

Voila! — Documentele tale, lecții clare

The learner should not feel like they are editing metadata.

The learner should feel like they are explaining a useful idea from the document in their own words.

The form must work for:

- text fragments
- corrected OCR text
- formulas
- diagrams
- images
- drawings
- tables
- graphs
- important observations

## Target user

The form is designed for:

- a 15-year-old student
- a 17-year-old preparing for an exam
- an adult without technical knowledge
- a teacher or parent preparing a clean lesson from a document

The user should not need to understand metadata, bbox, source IDs, evidence IDs, JSON artifacts, crop paths, route names, or dry-runs.

## Place in the shell

Parent shell:

`Revizuire document`

The form is used in:

- `Text detectat`
- `Corecturi sugerate`
- `Formule și imagini`
- `Noțiuni importante`
- `Gata pentru studiu`

The form is the bridge between reviewed document content and clean Study material.

## Learner-facing goal

The form answers one simple question:

`Cum explici această idee ca să o poți învăța mai târziu?`

The form turns accepted text or selected visual content into a study-ready concept.

## Main form title

Preferred title:

`Adaugă explicația pentru lecție`

Alternative short title:

`Pregătește pentru studiu`

## Required learner-facing fields

The form should use friendly labels:

- Titlu scurt
- Ce este asta?
- Text / zonă verificată
- Explicație pe înțeles
- De ce este important?
- Sursa: pagina X
- Limba lecției
- Gata pentru studiu

The form should avoid primary labels like:

- metadata
- verified_text
- source_status
- source_note
- bbox
- source_bbox
- source_evidence_id
- manual_study_item_id
- visual_evidence_id
- crop_path
- artifact

## Field — Titlu scurt

Purpose:

Help the learner name the idea.

Learner-facing prompt:

`Dă un titlu scurt acestei idei.`

Examples:

- Formula sinusului
- Definiția derivabilității
- Graficul funcției de gradul doi
- Tabel de valori
- Exemplu rezolvat

Rules:

- short
- readable
- not technical
- useful later in Study

## Field — Ce este asta?

Purpose:

Let the learner choose a friendly item type.

Learner-facing label:

`Ce este asta?`

Recommended item types:

- Definiție
- Formulă
- Exemplu
- Teoremă
- Diagramă
- Imagine
- Tabel
- Desen
- Grafic
- Observație importantă

The selected type helps Study present the item clearly later.

## Field — Text / zonă verificată

Purpose:

Show what content is being explained.

For text items, this shows the accepted or corrected text.

For visual items, this shows a crop preview or selected page area.

Learner-facing labels:

- Text verificat
- Zonă selectată
- Conținut verificat

The learner may be allowed to edit the text version, but should not be required to edit technical source fields.

## Field — Explicație pe înțeles

Purpose:

Capture the learner-facing explanation.

Learner-facing prompt:

`Explică pe înțeles ce înseamnă.`

The explanation should be:

- clear
- simple
- in the selected lesson language
- useful for Study
- not mixed RO/EN

This field replaces the old feeling of metadata editing.

## Field — De ce este important?

Purpose:

Help the learner connect the idea to exam learning.

Learner-facing prompt:

`De ce merită învățat?`

Examples:

- Apare frecvent în exerciții.
- Ajută la rezolvarea problemelor cu triunghiuri.
- Este o formulă de bază pentru capitol.
- Explică legătura dintre două noțiuni.

This field may be optional, but should be encouraged.

## Field — Sursa: pagina X

Purpose:

Keep source trust visible.

Learner-facing label:

`Sursa: pagina X`

The learner should always know where the idea came from.

Study should later show the same friendly source label.

The main learner flow should not expose internal source IDs.

## Field — Limba lecției

Purpose:

Prevent mixed RO/EN output.

Supported first-level options:

- Română
- English

The selected language should apply to:

- form labels
- prompts
- explanations
- Study cards
- exam practice labels

No mixed RO/EN learner flow.

Technical diagnostics can remain in English if needed, but not the main learner path.

## Readiness model

The form should clearly show whether an item is ready.

Learner-facing readiness states:

- Incomplet
- De verificat
- Gata pentru studiu
- Ignorat

An item becomes `Gata pentru studiu` only when it has:

- short title
- friendly item type
- verified text or selected visual area
- learner-facing explanation
- source page
- lesson language

Incomplete items should not silently become Study cards.

## Primary actions

Preferred learner-facing buttons:

- Salvează pentru lecție
- Gata pentru studiu
- Editează explicația
- Ignoră
- Înapoi
- Continuă
- Învață acum

Avoid primary buttons:

- Save metadata
- Save source evidence
- Write JSON
- Export dry-run
- Save bbox
- Save artifact
- Accept evidence ID

## Validation behavior

The form should guide the learner gently.

If required information is missing, use friendly messages:

- Adaugă un titlu scurt.
- Alege ce este această idee.
- Adaugă o explicație pe înțeles.
- Confirmă pagina sursă.
- Alege limba lecției.

Avoid technical validation messages like:

- missing verified_text
- invalid bbox
- source_evidence_id required
- artifact write failed
- JSON schema validation failed

Technical errors can be shown in `Diagnostic tehnic`.

## Explanation quality hints

The form may offer friendly hints:

- Scrie ca pentru un coleg de clasă.
- Folosește propoziții scurte.
- Evită copierea mecanică.
- Explică ce se folosește la exerciții.
- Dacă este formulă, spune ce reprezintă fiecare parte.
- Dacă este diagramă, spune ce arată desenul.

These hints should respect the selected lesson language.

## Text item variant

For text fragments, the form should show:

- source page
- accepted/corrected text
- title
- item type
- explanation
- importance
- readiness state

The learner should not see OCR offsets, LanguageTool rule IDs, or artifact names in the main form.

## Visual item variant

For formulas, diagrams, images, drawings, tables, and graphs, the form should show:

- source page
- selected area
- crop preview
- title
- item type
- explanation
- importance
- readiness state

The learner should not see raw bbox values, crop paths, Formula OCR logs, visual evidence IDs, or OCR Math diagnostics in the main form.

## Diagnostic boundary

Diagnostic may show technical details, but only behind `Diagnostic tehnic`.

Diagnostic may include:

- metadata
- bbox
- source IDs
- evidence IDs
- JSON paths
- crop paths
- route names
- engine status
- dry-run state
- package policy markers

Diagnostic must be collapsed by default.

Diagnostic must not be required to complete the learner workflow.

## Handoff contract

The form should eventually produce or feed clean study-ready concepts.

Study-facing clean concepts should include:

- short title
- item type
- verified text or visual preview reference
- learner explanation
- importance note
- source page
- lesson language
- readiness state
- ignored/not useful state

Study should not receive incomplete items as if they were verified learning material.

Study should not expose metadata, bbox, source evidence IDs, manual study item IDs, visual evidence IDs, crop paths, or JSON artifact names in the main learner view.

## Non-goals

This milestone does not implement the form.

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

This milestone does not write manual evidence artifacts.

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

No manual evidence writing.

## Recommended next

v0.8.48 — clean Study mode design.

v0.8.49 — owner personal full workflow test after implementation.

## Final decision

The friendly explanation form replaces metadata editing in the learner flow.

The learner explains ideas for study.

The system handles technical storage in the background.
