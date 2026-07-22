# v0.8.49 Learner workflow implementation preflight — no build/no ZIP/no share/no delivery

## Purpose

This milestone prepares the implementation of the new learner-first Voila workflow.

It follows the completed UX design chain:

- v0.8.43 — Student workflow UX reset charter
- v0.8.44 — Review Document shell design
- v0.8.45 — OCR + LanguageTool review queue design
- v0.8.46 — Formula/image/diagram/crop queue design
- v0.8.47 — Friendly explanation form design
- v0.8.48 — Clean Study mode design

This is implementation preflight only.

No UI implementation is performed in this milestone.

## Product direction

Voila! — Documentele tale, lecții clare

The new user-facing workflow is:

1. Încarcă documentul
2. Revizuiește documentul
3. Alege ce merită învățat
4. Creează lecția
5. Învață
6. Exersează pentru examen

## Implementation principle

Do not patch the old technical UI in place as the main learner experience.

Implement the new learner workflow as an additive guided surface first.

Existing technical routes may remain available for owner/developer diagnostics.

The learner should see:

- Revizuire document
- Text detectat
- Corecturi sugerate
- Formule și imagini
- Noțiuni importante
- Gata pentru studiu
- Învață lecția

The learner should not see as the default experience:

- metadata
- bbox
- source_evidence_id
- manual_study_item_id
- visual_evidence_id
- JSON artifact names
- dry-run
- route names
- package policy markers
- build flags
- delivery flags

## Route strategy

Preferred additive route strategy for implementation:

- keep existing routes intact
- add learner-facing shell route only when implementation starts
- do not remove OCR Review, Crop Editor, Manual Evidence, or Study routes yet
- link learner-facing shell from Course Tools only after a guarded implementation slice passes
- keep technical routes reachable from Diagnostic tehnic or owner-only links

Candidate learner-facing route:

`/review-document?pdf={pdf_name}`

Alternative if existing route conventions require course IDs:

`/review-document/{course_id}`

Route choice must be finalized in the first implementation slice before code changes.

## First implementation slice recommendation

Recommended next implementation milestone:

`v0.8.50-owner-local-review-document-shell-read-only-first-slice-no-build-no-zip-no-share-no-delivery`

First slice scope should be small:

- add read-only learner shell
- show document name
- show lesson language selector display
- show five steps
- show friendly guidance panel
- show Diagnostic tehnic collapsed by default
- link back to Course Tools
- do not write data
- do not run OCR
- do not run LanguageTool
- do not run crop extraction
- do not change Study behavior

## Implementation slice order

Recommended implementation order:

1. v0.8.50 — read-only `Revizuire document` shell
2. v0.8.51 — Course Tools link to learner shell
3. v0.8.52 — read-only Text detectat queue from existing OCR artifacts
4. v0.8.53 — read-only Corecturi sugerate queue from existing LanguageTool artifacts
5. v0.8.54 — read-only Formule și imagini queue from existing visual/crop artifacts
6. v0.8.55 — friendly explanation form read-only/static draft shell
7. v0.8.56 — safe local save for explanation drafts
8. v0.8.57 — clean Study read-only preview
9. v0.8.58 — owner personal workflow smoke
10. separate explicit owner approval only after PASS for package rebuild

## File strategy

Expected implementation files may include:

- services/api/web_app.py
- docs/dev/*
- scripts/dev/check-*.ps1
- scripts/dev/check-*.py

The first implementation slice should avoid broad rewrites.

Avoid touching unrelated areas queue from existing visual/crop artifacts
6. v0.8.55 — friendly explanation form read-only/static draft shell
7. v0.8.56 — safe local save for explanation drafts
8. v0.8.57 — clean Study read-only preview
9. v0.8.58 — owner personal workflow smoke
10. separate explicit owner approval only after PASS for package rebuild

## File strategy

Expected implementation files may include:

- services/api/web_app.py
- docs/dev/*
- scripts/dev/check-*.ps1
- scripts/dev/check-*.py

The first implementation slice should:

- package builder scripts
- OneDrive scripts
- release assets
- installer assets
- Progress persistence
- scoring
- public release scripts

## Safety guardrails

Every implementation milestone must explicitly check:

- no build
- no ZIP
- no package rebuild
- no OneDrive copy
- no share
- no delivery
- no distribution
- no public release
- no Progress write unless explicitly scoped later
- no answer marking unless explicitly scoped later
- no destructive OCR rewrite
- no unguarded Study behavior change
- no public route exposure beyond owner-local/dev local scope

## Existing engines

The implementation should reuse existing engines and artifacts.

Do not throw away:

- OCR text artifacts
- LanguageTool correction artifacts
- OCR Math report artifacts
- visual evidence artifacts
- manual learning evidence artifacts
- manual learning pack preview
- manual study items preview
- Study adapter work

But the learner-facing UI must hide technical engine details.

## Background engine rule

Engines should eventually run in the background behind the learner workflow.

The learner-facing progress should be:

- Se citește documentul
- Se extrage textul
- Se verifică textul
- Se caută formule și imagini
- Pregătim noțiunile importante
- Lecția este gata pentru studiu

Do not expose engine startup details in the main learner UI.

## Language rule

Implementation must include a clear lesson language model.

Supported first-level options:

- Română
- English

No mixed RO/EN learner flow.

The selected language must eventually apply to:

- UI labels
- review prompts
- correction explanations
- friendly explanation form
- Study cards
- exam practice labels

## Diagnostic boundary

Technical details remain allowed only inside:

`Diagnostic tehnic`

Diagnostic should be collapsed by default.

Diagnostic may include:

- JSON paths
- route names
- source IDs
- evidence IDs
- bbox
- crop paths
- engine status
- dry-run state
- package policy markers

Diagnostic must not be required to complete the learner workflow.

## Study protection

Study must not be changed casually.

Clean Study implementation should happen only after the review shell and handoff contract are stable.

Until then:

- existing Study behavior must remain protected
- Manual Study fallback must remain protected
- no Progress writes
- no answer marking
- no scoring
- no automatic delivery of unresolved content into Study

## Data write protection

Early implementation slices should be read-only.

When writes are introduced later, they must be explicit and local-only.

Allowed later write types must be separately scoped:

- learner review decision drafts
- friendly explanation drafts
- saved-for-lesson decisions

Forbidden in this preflight:

- OCR rewrite
- crop writing
- manual evidence writing
- Study card creation
- Progress writing
- answer marking
- package generation

## Test strategy

Each implementation slice must include a dedicated check script.

Checks should validate:

- route or document exists
- learner-facing labels exist
- technical labels are hidden from the main learner surface
- Diagnostic tehnic exists when technical detail is present
- route remains local/owner-safe
- no build/ZIP/share/delivery flags occurred
- no unrelated files changed
- Study and Progress are protected unless explicitly scoped

## Manual smoke strategy

After the first implementation sequence, run owner personal smoke:

Home → Course Tools → Revizuire document → Text detectat → Corecturi sugerate → Formule și imagini → Noțiuni importante → Gata pentru studiu → Study curat

A tester package rebuild is blocked until owner personal smoke passes.

## Package readiness

Current package readiness remains blocked.

`PACKAGE_READINESS=BLOCKED_PENDING_UI_IMPLEMENTATION_AND_RETEST`

No package rebuild is allowed in this milestone.

No ZIP is allowed in this milestone.

No share or delivery is allowed in this milestone.

## Non-goals

This milestone does not implement the learner shell.

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

v0.8.50 — owner-local Review Document shell read-only first slice.

## Final decision

Implementation starts only after this preflight.

The first code slice must be additive, read-only, local, guarded, and learner-facing.

No tester package work resumes until the new learner workflow is implemented and retested personally by the owner.
