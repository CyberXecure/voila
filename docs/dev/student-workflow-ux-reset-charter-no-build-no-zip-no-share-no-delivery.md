# v0.8.43 Student workflow UX reset charter — no build/no ZIP/no share/no delivery

## Purpose

This milestone resets the Voila UX direction before any further tester package work.

v0.8.41 proved that the technical Manual Study path works, but the workflow is not understandable enough for a tester without extra explanation.

v0.8.42 added a first Course Tools UX polish, but the current UI still exposes too many technical concepts to the learner.

This charter says: stop patching the technical UI and redesign the learner workflow as a guided product experience.

## Product positioning

Voila! — Documentele tale, lecții clare

Voila should feel like a guided learning tool, not a developer diagnostics console.

The target user is:

- a 15-year-old student
- a 17-year-old preparing for an exam
- an adult without technical knowledge
- a teacher or parent who wants a clean study flow from a document

## Main learner workflow

The learner-facing flow must be:

1. Încarcă documentul
2. Revizuiește documentul
3. Alege ce merită învățat
4. Creează lecția
5. Învață
6. Exersează pentru examen

The learner should not need to understand internal artifacts, JSON files, OCR pipelines, crop IDs, bbox values, dry-runs, or source evidence identifiers.

## Unified learner concept

OCR Review, Crop Editor, and Manual Learning Evidence must become one learner-facing workflow:

`Revizuire document`

Internally, these can remain separate engines and artifacts.

Externally, the learner sees one guided review surface.

## What Revizuire document includes

The document review workflow should guide the user through:

- full document OCR text review
- LanguageTool correction review
- formula review
- image/crop review
- diagram/drawing review
- manual explanation entry
- concept selection
- source page confirmation
- final confirmation that the item can be used in Study

All engines should run in the background.

The user should see simple decisions:

- Corectează
- Acceptă
- Ignoră
- Adaugă la lecție
- Explică pe înțeles
- Gata pentru studiu

## OCR text and LanguageTool

The OCR text review should not be a technical OCR report.

It should show clean editable or confirmable text blocks with LanguageTool suggestions in a guided way.

The learner-facing labels should be:

- Text detectat
- Sugestii de corectare
- Text corectat
- Acceptă textul
- Continuă

The technical labels should be hidden from the main learner flow.

## Formulas, diagrams, drawings, and crops

Formulas, drawings, diagrams, tables, and visual fragments should be selected through a friendly crop experience.

The learner-facing flow should be:

1. Selectează zona din pagină
2. Spune ce reprezintă
3. Adaugă explicația
4. Salvează pentru lecție

The user should not see raw bbox values in the main workflow.

Raw bbox values may remain in Diagnostic only.

## Manual explanations

Manual explanation entry is not "metadata editing".

It should be presented as:

- Titlu scurt
- Ce este asta?
- Text verificat
- Explicație pe înțeles
- Pagina sursă
- Adaugă la lecție

Possible learner-facing item types:

- Definiție
- Formulă
- Exemplu
- Teoremă
- Diagramă
- Imagine
- Tabel
- Observație importantă

## Clean Study mode

Study must become a clean learner experience.

Study should show:

- Întrebare
- Răspuns
- Explicație
- Sursa: pagina X
- Înapoi
- Următorul card

Study should not show, in the main learner mode:

- manual_study_default_enabled
- fallback_legacy_study_available
- manual_study_connected_to_real_study
- source_evidence_id
- manual_study_item_id
- source_bbox
- build_performed
- zip_created
- share_created
- delivery_performed
- Card 1 Card 2 Card 3 as raw anchor lists
- JSON artifact names

These belong only in Diagnostic.

## Language consistency

The learner must choose or inherit a lesson language.

Supported first-level options:

- Română
- English

Once selected, the entire learner experience should remain in one language:

- UI labels
- prompts
- answers
- explanations
- study cards
- exam practice labels

No mixed RO/EN learner flow.

Technical diagnostics can remain in English if needed, but not in the main learner path.

## Background engines

The engines should run in the background and surface simple progress states.

Background engines may include:

- OCR
- LanguageTool
- formula/image detection
- crop extraction
- manual evidence storage
- learning material preparation
- study adapter
- exam practice adapter

Learner-facing progress should be simple:

- Se citește documentul
- Se verifică textul
- Se caută formule și imagini
- Alege ce intră în lecție
- Lecția este gata pentru studiu

## Diagnostics boundary

Technical information is still valuable for the owner and developer.

It must be moved to:

`Diagnostic tehnic`

Diagnostic may include:

- artifact names
- JSON paths
- source IDs
- bbox
- route names
- dry-run state
- package policy markers

Diagnostic must not be the default learner experience.

## No delivery boundary

This milestone does not implement the redesigned UI.

It only freezes the direction and creates a validation checkpoint.

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

## Recommended next milestones

v0.8.44 — Design shell for `Revizuire document`.

v0.8.45 — Learner-facing OCR text + LanguageTool review queue.

v0.8.46 — Learner-facing formula/image/diagram crop queue.

v0.8.47 — Friendly explanation form.

v0.8.48 — Clean Study mode.

v0.8.49 — Owner personal full workflow test on real document.

## Final decision

We do not throw away the engines.

We hide the engines behind a simple, guided, learner-first workflow.

The product direction is:

`Voila! — Documentele tale, lecții clare`
