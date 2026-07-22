# v0.8.45 OCR + LanguageTool review queue design — no build/no ZIP/no share/no delivery

## Purpose

This milestone designs the learner-facing review queue for the first two steps of the new `Revizuire document` shell:

1. Text detectat
2. Corecturi sugerate

It follows v0.8.44, which designed the learner-first `Revizuire document` shell.

This is design/documentation/check only.

No UI implementation is performed in this milestone.

## Product context

Voila! — Documentele tale, lecții clare

The learner should not see a technical OCR report.

The learner should see a guided text review flow.

OCR and LanguageTool run in the background.

The learner only decides what is correct, what needs editing, and what can continue toward Study.

## Target user

The queue is designed for:

- a 15-year-old student
- a 17-year-old preparing for an exam
- an adult without technical knowledge
- a teacher or parent reviewing a document before Study

The user should not need to understand OCR engines, JSON, offsets, LanguageTool rule IDs, token spans, internal confidence values, source IDs, route names, or artifacts.

## Place in the shell

Parent shell:

`Revizuire document`

Covered steps:

- `Text detectat`
- `Corecturi sugerate`

Not covered in this milestone:

- Formule și imagini
- Noțiuni importante
- Gata pentru studiu
- Study clean mode implementation
- package rebuild
- tester delivery

## Learner-facing goal

Turn raw OCR text into clean, confirmed text blocks that can later feed:

- important concepts
- manual explanations
- clean Study cards
- exam practice

The learner-facing question is:

`Textul din document este corect și gata pentru lecție?`

## Queue concept

The review queue should be page-based and block-based.

A queue item represents a readable OCR text block from a source page.

Each queue item should show:

- page number
- detected text
- LanguageTool suggestions when available
- simple status
- next action

The learner should move through one clear item at a time.

## Suggested queue item fields

Conceptual design only.

A learner-facing queue item may contain:

- `page`
- `block_title`
- `detected_text`
- `suggested_text`
- `correction_summary`
- `learner_status`
- `source_page_preview`
- `language`
- `notes`

Technical fields may exist internally, but must not be primary learner content.

## Learner-facing statuses

Use simple statuses:

- `De verificat`
- `Are sugestii`
- `Corectat`
- `Acceptat`
- `Ignorat`

Avoid primary learner statuses like:

- raw_ocr
- lt_match
- source_offset
- bbox
- rule_id
- artifact_ready
- dry_run

## Step 1 — Text detectat

Purpose:

Show the OCR text in readable page-based blocks.

Learner-facing labels:

- Text detectat
- Pagina sursă
- Text de verificat
- Acceptă textul
- Corectează textul
- Ignoră fragmentul
- Continuă

Learner-facing actions:

- Citește
- Acceptă textul
- Corectează textul
- Ignoră fragmentul
- Continuă

The learner should see:

- document name
- page number
- clean text block
- short instruction
- clear action buttons

The learner should not see:

- raw OCR logs
- OCR debug dumps
- engine internals
- JSON artifact names
- extracted file paths
- hidden IDs

## Step 2 — Corecturi sugerate

Purpose:

Present LanguageTool suggestions as friendly correction choices.

Learner-facing labels:

- Corecturi sugerate
- Sugestie
- Text original
- Text corectat
- Explicație
- Acceptă sugestia
- Păstrează textul
- Editează manual
- Aplică sugestiile clare
- Continuă

Learner-facing actions:

- Acceptă sugestia
- Păstrează textul
- Editează manual
- Aplică sugestiile clare
- Continuă

The learner should see:

- the text with a highlighted issue
- the suggested correction
- a short explanation in the selected lesson language
- a clear accept/keep/edit choice

The learner should not see as primary content:

- LanguageTool JSON
- rule ID
- offset
- length
- category ID
- replacement arrays
- server URL
- request payload

## Language consistency

The queue must respect the lesson language selected in `Revizuire document`.

Supported first-level options:

- Română
- English

If the lesson language is Română:

- labels should be Romanian
- correction explanations should be Romanian when possible
- learner prompts should be Romanian
- Study handoff should remain Romanian

If the lesson language is English:

- labels should be English
- correction explanations should be English when possible
- learner prompts should be English
- Study handoff should remain English

No mixed RO/EN learner flow.

Technical diagnostics can remain in English if needed, but not the main learner path.

## Background engine behavior

OCR and LanguageTool should run in the background.

Learner-facing progress labels:

- Se citește documentul
- Se extrage textul
- Se verifică textul
- Se pregătesc sugestiile
- Textul este gata de revizuire

The learner should not need to manually start:

- OCR engine
- LanguageTool server
- correction parser
- artifact generation

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

3. Queue card
   - page number
   - detected text
   - suggestion panel when available
   - status badge
   - action buttons

4. Guidance panel
   - what the learner is reviewing
   - what to do next
   - why this matters for Study

5. Diagnostic tehnic
   - collapsed by default
   - owner/developer only

## Primary buttons

Preferred learner-facing buttons:

- Acceptă textul
- Corectează textul
- Acceptă sugestia
- Păstrează textul
- Editează manual
- Ignoră fragmentul
- Continuă
- Înapoi

Avoid primary buttons:

- Save metadata
- Write artifact
- Export dry-run
- Accept source evidence
- Apply LT match
- Save bbox
- Generate JSON

## Friendly editing model

Manual correction should feel like editing a sentence, not editing metadata.

Use labels:

- Text original
- Text corectat
- Explicație
- Salvează corectura

Avoid labels:

- metadata
- verified_text
- source_status
- source_note
- rule_id
- offset
- artifact

## Readiness for Study

A text block becomes ready for downstream learning only after one of these learner decisions:

- accepted as correct
- corrected manually
- LanguageTool suggestion accepted
- intentionally ignored as not useful

The queue must distinguish:

- useful accepted text
- corrected text
- ignored/noise text
- unresolved text

Unresolved text should not silently become clean Study material.

## Diagnostic boundary

Diagnostic may show technical details, but only behind `Diagnostic tehnic`.

Diagnostic may include:

- OCR artifact names
- LanguageTool rule IDs
- offsets
- confidence values
- source IDs
- JSON paths
- route names
- engine status
- dry-run state

Diagnostic must be collapsed by default.

Diagnostic must not be required to complete the learner workflow.

## Handoff contract

This queue should eventually produce or feed clean learner-facing review decisions.

Study-facing clean text should include:

- source page
- final text
- correction state
- lesson language
- optional learner note
- ignored/not useful state

Study should not receive unresolved OCR text as if it were verified.

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

This milestone does not write new OCR artifacts.

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

## Recommended next

v0.8.46 — learner-facing formula/image/diagram crop queue design.

v0.8.47 — friendly explanation form design.

v0.8.48 — clean Study mode design.

v0.8.49 — owner personal full workflow test after implementation.

## Final decision

The OCR + LanguageTool review queue is not a technical report.

It is a guided learner workflow that turns detected text into clean, confirmed text for later learning.
