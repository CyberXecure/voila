# v0.8.44 Review Document shell design — no build/no ZIP/no share/no delivery

## Purpose

This milestone designs the new learner-first shell for:

`Revizuire document`

It follows v0.8.43, which reset the Voila UX direction around:

`Voila! — Documentele tale, lecții clare`

This is design/documentation/check only.

No UI implementation is performed in this milestone.

## Product rule

The learner must not see a developer diagnostics console.

The learner must see a guided review workflow.

Internal engines can remain separate.

The learner-facing experience must be unified.

## Target user

The shell is designed for:

- a 15-year-old student
- a 17-year-old preparing for an exam
- an adult without technical knowledge
- a teacher or parent who wants a clear document-to-study workflow

The user should not need to understand OCR internals, JSON artifacts, bbox, crop IDs, source evidence IDs, dry-runs, route names, or package policy markers.

## Shell name

Main shell title:

`Revizuire document`

Subtitle:

`Verifică textul, formulele și imaginile înainte să creezi lecția.`

Product context:

`Voila! — Documentele tale, lecții clare`

## Main shell workflow

The shell should guide the user through five learner-facing steps:

1. Text detectat
2. Corecturi sugerate
3. Formule și imagini
4. Noțiuni importante
5. Gata pentru studiu

These steps replace the current fragmented learner-facing concepts:

- OCR Review
- Crop Editor
- Manual Learning Evidence
- Learning Pack dry-run
- Manual Study Items preview

Internally, those systems can still exist.

Externally, the learner sees one flow: `Revizuire document`.

## Step 1 — Text detectat

Goal:

Show the OCR text in readable page-based blocks.

Learner-facing actions:

- Citește
- Corectează
- Acceptă textul
- Ignoră fragmentul
- Continuă

The learner should see:

- page number
- readable extracted text
- confidence or quality only if translated into simple wording
- clear next action

The learner should not see:

- raw OCR engine output dumps
- low-level OCR logs
- internal artifact names
- technical confidence fields without explanation

Suggested labels:

- `Text detectat`
- `Pagina sursă`
- `Text de verificat`
- `Acceptă textul`
- `Corectează textul`

## Step 2 — Corecturi sugerate

Goal:

Present LanguageTool suggestions as friendly correction choices.

Learner-facing actions:

- Acceptă sugestia
- Păstrează textul
- Editează manual
- Aplică toate sugestiile clare
- Continuă

The learner should see:

- original text
- suggested correction
- short explanation
- accept/ignore controls

The learner should not see:

- LanguageTool JSON
- rule IDs as primary content
- raw offsets
- technical category names as the main UI

Suggested labels:

- `Sugestii de corectare`
- `Text corectat`
- `Acceptă`
- `Păstrează`
- `Explicație`

## Step 3 — Formule și imagini

Goal:

Unify formula review, image review, diagram review, drawing review, table review, and crop review.

Learner-facing actions:

- Selectează zona
- Spune ce reprezintă
- Adaugă explicația
- Salvează pentru lecție
- Ignoră

The learner should see:

- page image
- selection area
- preview crop
- friendly type selector
- explanation input

Possible item types:

- Formulă
- Diagramă
- Imagine
- Tabel
- Desen
- Grafic
- Observație importantă

The learner should not see:

- raw bbox values
- crop file paths
- source image internals
- Formula OCR debug state
- old external crop editor as a separate product surface

Suggested labels:

- `Formule și imagini`
- `Selectează zona din pagină`
- `Ce reprezintă?`
- `Explicație pe înțeles`
- `Salvează pentru lecție`

## Step 4 — Noțiuni importante

Goal:

Turn verified text/crops into study-ready concepts.

Learner-facing actions:

- Adaugă la lecție
- Editează explicația
- Marchează ca definiție
- Marchează ca formulă
- Marchează ca exemplu
- Marchează ca teoremă
- Elimină din lecție

The learner should see:

- short title
- type
- verified text
- explanation
- source page
- readiness state

Possible readiness states:

- `De verificat`
- `Aproape gata`
- `Gata pentru studiu`
- `Ignorat`

The learner should not see:

- accepted_owner_verified
- manual_learning_evidence.json
- manual_study_items.preview.json
- source_evidence_id
- manual_study_item_id
- dry-run state as primary content

Suggested labels:

- `Noțiuni importante`
- `Titlu scurt`
- `Ce este asta?`
- `Text verificat`
- `Explicație pe înțeles`
- `Pagina sursă`
- `Gata pentru studiu`

## Step 5 — Gata pentru studiu

Goal:

Show a clean final confirmation before Study.

Learner-facing actions:

- Creează lecția
- Învață acum
- Revino la revizuire
- Exersează pentru examen

The learner should see:

- number of ready items
- number of items still needing review
- warning if no useful material is ready
- language selected for Study
- primary button to Study

The learner should not see:

- build_performed
- zip_created
- share_created
- delivery_performed
- package policy markers
- JSON artifact names

Suggested labels:

- `Lecția este gata`
- `Noțiuni gata pentru studiu`
- `Mai ai de verificat`
- `Învață acum`
- `Exersează pentru examen`

## Language selector

The shell must include a clear lesson language selector.

Supported first-level options:

- Română
- English

Learner-facing label:

`Limba lecției`

Once chosen, the learner-facing workflow should not mix RO and EN.

The selected language should apply to:

- shell labels
- correction explanations
- manual explanation prompts
- study cards
- exam practice labels

Technical diagnostics can remain in English if needed, but not the main learner flow.

## Background engines

The shell should make engines invisible and progress visible.

Background engines can include:

- OCR
- LanguageTool
- formula detection
- image detection
- diagram detection
- crop extraction
- manual evidence storage
- learning material preparation
- study adapter
- exam practice adapter

Learner-facing progress labels:

- `Se citește documentul`
- `Se verifică textul`
- `Se caută formule și imagini`
- `Pregătim noțiunile importante`
- `Lecția este gata pentru studiu`

## Layout design

The shell layout should use:

- a top progress stepper
- a main review workspace
- a right-side or bottom guidance panel
- a persistent primary action
- a small secondary Diagnostic toggle

Recommended layout sections:

1. Header
   - document title
   - lesson language
   - progress summary

2. Stepper
   - Text detectat
   - Corecturi sugerate
   - Formule și imagini
   - Noțiuni importante
   - Gata pentru studiu

3. Work area
   - current page or item
   - review content
   - friendly controls

4. Guidance panel
   - what this step means
   - what the learner should do now
   - next action

5. Diagnostic tehnic
   - collapsed by default
   - only for owner/developer

## Primary navigation labels

Preferred user-facing labels:

- `Înapoi`
- `Continuă`
- `Acceptă`
- `Ignoră`
- `Corectează`
- `Adaugă la lecție`
- `Salvează pentru lecție`
- `Învață acum`
- `Exersează pentru examen`

Avoid as primary learner labels:

- metadata
- bbox
- JSON
- dry-run
- artifact
- evidence id
- source id
- route
- fallback
- package
- delivery

## Diagnostic boundary

Technical data remains useful but must be separated.

Diagnostic may include:

- artifact paths
- JSON names
- route names
- source IDs
- bbox
- engine status
- dry-run state
- package policy markers

Diagnostic must be collapsed by default.

Diagnostic must not be required to complete the learner workflow.

## Study handoff contract

The shell should hand off only clean, verified material to Study.

Study receives learner-facing items:

- question
- answer
- explanation
- source page
- item type
- lesson language

Study should not expose internal IDs in the main learner view.

## Non-goals

This milestone does not implement the shell.

This milestone does not change the current UI.

This milestone does not change routing.

This milestone does not write new evidence artifacts.

This milestone does not perform OCR.

This milestone does not perform LanguageTool correction.

This milestone does not perform crop extraction.

This milestone does not change Study.

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

## Recommended next

v0.8.45 — learner-facing OCR text + LanguageTool review queue design.

v0.8.46 — learner-facing formula/image/diagram crop queue design.

v0.8.47 — friendly explanation form design.

v0.8.48 — clean Study mode design.

v0.8.49 — owner personal full workflow test after implementation.

## Final decision

The new shell is:

`Revizuire document`

It hides technical engines behind a guided learner-first workflow.

It is designed before implementation so we do not continue patching the old technical UI.
