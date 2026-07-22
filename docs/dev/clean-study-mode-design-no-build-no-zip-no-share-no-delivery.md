# v0.8.48 Clean Study mode design — no build/no ZIP/no share/no delivery

## Purpose

This milestone designs the learner-facing clean Study mode.

It follows:

- v0.8.43 Student workflow UX reset charter
- v0.8.44 Review Document shell design
- v0.8.45 OCR + LanguageTool review queue design
- v0.8.46 Formula/image/diagram/crop queue design
- v0.8.47 Friendly explanation form design

This is design/documentation/check only.

No UI implementation is performed in this milestone.

## Product context

Voila! — Documentele tale, lecții clare

Study is where the learner should feel that the document has become a clear lesson.

The learner should not see a technical Manual Study debug page.

The learner should see simple study cards built only from reviewed and confirmed material.

## Target user

Clean Study mode is designed for:

- a 15-year-old student
- a 17-year-old preparing for an exam
- an adult without technical knowledge
- a teacher or parent reviewing a clean lesson

The user should not need to understand metadata, bbox, source IDs, evidence IDs, JSON artifacts, crop paths, route names, dry-runs, fallback states, package policy markers, or delivery flags.

## Place in the product flow

Clean Study mode comes after:

1. Revizuire document
2. Text detectat
3. Corecturi sugerate
4. Formule și imagini
5. Noțiuni importante
6. Gata pentru studiu

Study should receive only clean, confirmed learner-facing material.

Study should not silently receive unresolved OCR text, unresolved visual items, incomplete explanations, or technical artifacts as learning cards.

## Learner-facing goal

Clean Study answers one simple question:

`Ce trebuie să învăț acum din document?`

The learner should be able to study without understanding the pipeline that created the cards.

## Main Study screen

Preferred page title:

`Învață lecția`

Alternative title:

`Study curat`

Subtitle:

`Parcurge noțiunile verificate din document, una câte una.`

The main Study screen should show:

- current card
- total cards
- lesson language
- item type
- source page
- question
- answer
- explanation
- optional visual preview
- previous/next navigation
- exam practice handoff

## Clean Study card structure

Each learner-facing card should contain:

- Tip
- Titlu scurt
- Întrebare
- Răspuns
- Explicație pe înțeles
- Sursa: pagina X
- Imagine / formulă / diagramă, when relevant
- Înapoi
- Următorul card
- Exersează pentru examen

The learner should not see:

- manual_study_default_enabled
- fallback_legacy_study_available
- manual_study_connected_to_real_study
- source_evidence_id
- manual_study_item_id
- visual_evidence_id
- source_bbox
- bbox
- crop_path
- artifact path
- JSON file name
- route name
- build_performed
- zip_created
- share_created
- delivery_performed
- package policy marker

## Card types

Clean Study should support friendly item types:

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

The type should help the learner understand what kind of thing they are studying.

The type should not expose internal artifact categories.

## Text card design

For text-based items, Study should show:

- Titlu scurt
- Tip
- Întrebare
- Răspuns
- Explicație pe înțeles
- Sursa: pagina X

Example learner-facing structure:

`Ce înseamnă derivabilitatea?`

`Răspuns: ...`

`Explicație: ...`

`Sursa: pagina 3`

Study should not show OCR offsets, LanguageTool rule IDs, correction internals, or raw OCR diagnostics.

## Visual card design

For visual items such as formulas, diagrams, drawings, images, tables, and graphs, Study should show:

- visual preview
- title
- item type
- question
- answer
- explanation
- source page

Example learner-facing structure:

`Ce reprezintă această formulă?`

`Răspuns: ...`

`Explicație: ...`

`Sursa: pagina 4`

Study should not show raw bbox values, crop paths, visual evidence IDs, Formula OCR logs, OCR Math diagnostics, or image artifact paths in the main learner view.

## Question and answer model

Study should use simple learner-facing question/answer cards.

Allowed learner-facing labels:

- Întrebare
- Răspuns
- Explicație
- Explicație pe înțeles
- Sursa
- Tip
- Următorul card
- Înapoi
- Arată răspunsul
- Ascunde răspunsul
- Exersează pentru examen

Avoid primary labels:

- prompt
- completion
- metadata
- evidence
- artifact
- source id
- bbox
- fallback
- dry-run
- route
- package
- delivery

## Answer reveal behavior

Answer reveal should be safe and simple.

Recommended behavior:

1. Show question first.
2. Let learner press `Arată răspunsul`.
3. Show answer and explanation.
4. Keep source page visible.
5. Let learner continue to the next card.

The answer area should be read-only in Study.

Editing should happen back in `Revizuire document`, not accidentally inside Study.

## Source trust

Study should keep source trust visible.

Learner-facing label:

`Sursa: pagina X`

The source should be visible but not technical.

The learner should not see internal source IDs in the main Study view.

A secondary action may allow:

`Revino la sursă`

This should take the learner back to the relevant review/source context when implemented.

## Language consistency

Clean Study must respect the lesson language selected in `Revizuire document`.

Supported first-level options:

- Română
- English

If lesson language is Română:

- Study labels should be Romanian
- questions should be Romanian
- answers should be Romanian
- explanations should be Romanian
- exam practice labels should be Romanian

If lesson language is English:

- Study labels should be English
- questions should be English
- answers should be English
- explanations should be English
- exam practice labels should be English

No mixed RO/EN learner flow.

Technical diagnostics can remain in English if needed, but not the main learner path.

## Navigation model

Study navigation should be simple.

Preferred learner-facing controls:

- Înapoi
- Următorul card
- Arată răspunsul
- Ascunde răspunsul
- Revino la revizuire
- Exersează pentru examen

Avoid large raw anchor lists such as:

- Card 1
- Card 2
- Card 3
- Card 4
- Card 5
- Card 31

A compact progress indicator is better:

`Card 3 din 18`

## Progress model

Clean Study may show light progress, but not heavy scoring.

Learner-facing progress labels:

- Card X din Y
- Ai parcurs X carduri
- Mai ai Y carduri
- Continuă lecția

This milestone does not design grading, scoring, mastery, or Progress writes.

Progress writes are out of scope.

## Exam practice handoff

Clean Study should include a learner-facing handoff to future exam practice.

Preferred button:

`Exersează pentru examen`

Purpose:

Let the learner practice after reviewing the cards.

The handoff should use clean, reviewed concepts only.

It should not expose Exam Prep internals, bank IDs, source IDs, JSON artifacts, or dry-runs.

## Empty and warning states

Study should handle empty or incomplete material clearly.

If no material is ready:

`Nu ai încă noțiuni gata pentru studiu.`

Suggested action:

`Revino la Revizuire document`

If some items are incomplete:

`Unele noțiuni mai trebuie verificate înainte să apară în Study.`

Suggested action:

`Verifică noțiunile importante`

Study should not silently show incomplete or unresolved items as clean cards.

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
- fallback state
- package policy markers

Diagnostic must be collapsed by default.

Diagnostic must not be required to complete the learner Study flow.

## Clean Study handoff contract

Clean Study should eventually consume study-ready concepts that include:

- short title
- item type
- question
- answer
- learner explanation
- source page
- lesson language
- optional visual preview reference
- readiness state

Clean Study should reject or hide items that are:

- incomplete
- unresolved
- ignored
- missing explanation
- missing source page
- in the wrong lesson language

Clean Study should not expose internal IDs in the main learner view.

## Non-goals

This milestone does not implement Clean Study.

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

This milestone does not change Study behavior.

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

v0.8.49 — owner-local learner workflow implementation preflight.

v0.8.50 — first implementation slice for Revizuire document shell.

v0.8.51 — owner personal full workflow test after implementation.

## Final decision

Clean Study is not a technical Manual Study debug surface.

Clean Study is the learner-facing place where reviewed document material becomes a clear lesson.
