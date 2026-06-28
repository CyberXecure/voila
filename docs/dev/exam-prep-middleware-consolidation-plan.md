# Voila Exam Prep — Middleware Consolidation Plan

Milestone: v0.4.21  
Scope: planning/checklist only

## Current state

Exam Prep is functional and protected by smoke checks.

Validated routes:

- `/exam-prep`
- `/exam-prep/skill/{skill_id}`
- `/exam-prep/skill/derivate`

Validated dashboard sections:

1. `Ce să faci acum?`
2. `Rezumat progres`
3. `Skill-uri Exam Prep`

Validated skill detail sections:

- `Întrebări asociate din Modul Studiu`
- `Acțiune recomandată`
- `Continuă în Modul Studiu`
- `Înapoi la Pregătire examene`

Validated terminology:

- `Consolidat`
- `În progres`
- `Funcții`
- `Pregătire examene`
- `Modul Studiu`

Forbidden user-facing regressions:

- `Stăpânire`
- `Stapanire`
- visible `Functii`
- visible `In progres`
- mixed wording such as `Study Mode` in Romanian UI labels
- mixed wording such as `Exam Prep` in Romanian back links

Allowed technical slug:

- `/exam-prep/skill/functii`

## Existing protection

Permanent smoke script:

- `scripts/dev/smoke-exam-prep-skill-detail.ps1`

Permanent health checkpoint:

- `scripts/dev/check-exam-prep-health.ps1`

The health checkpoint validates:

- Python compile
- source markers
- dashboard markers
- skill detail markers
- route availability
- Romanian wording
- section order
- absence of forbidden terminology

## Technical debt observed

Several Exam Prep UI features were added incrementally through helper functions and FastAPI middleware guards.

This is acceptable for the controlled milestone sequence, but before adding larger features, the implementation should be consolidated.

Main candidates for future cleanup:

1. Dashboard section injection
   - next action
   - progress summary
   - skill cards
   - ordering wrapper
   - visual style marker

2. Skill detail section injection
   - related Modul Studiu questions
   - next action
   - wording polish guards

3. Romanian wording wrappers
   - duplicate wording replacement logic
   - defensive response middleware

4. Marker strategy
   - keep stable smoke markers
   - reduce duplicate marker injection paths

## Recommended future consolidation

Do this in small milestones, not in one large refactor.

### Proposed v0.4.22

Move dashboard rendering toward a single `render_exam_prep_dashboard_sections_html()` helper.

Target:

- one helper returns ordered dashboard sections
- middleware only injects one final dashboard block
- keep all existing markers
- keep health checkpoint passing

### Proposed v0.4.23

Move skill detail rendering toward a single `render_exam_prep_skill_detail_sections_html(skill_id)` helper.

Target:

- one helper controls related questions + next action + buttons
- route/middleware stays thin
- keep all existing markers
- keep health checkpoint passing

### Proposed v0.4.24

Reduce wording polish wrappers.

Target:

- approved Romanian labels live in canonical helpers
- response middleware remains only as fallback guard
- keep `Modul Studiu`, `Pregătire examene`, `Consolidat`
- keep technical slug `/exam-prep/skill/functii`

## Non-goals

This plan does not:

- change OCR
- change PDF processing
- change course generation
- change Study/Review/Progress BKT engine
- change packaging
- create ZIP/release assets
- publish anything externally
- add adaptive recommendations
- add Exam Sprint Mode
- add an exam simulator

## Required safety rule for future refactors

Every future cleanup milestone must pass:

```powershell
python -m py_compile .\services\api\exam_prep.py .\services\api\web_app.py .\services\api\study_quiz_builder.py
& .\scripts\dev\smoke-exam-prep-skill-detail.ps1
& .\scripts\dev\check-exam-prep-health.ps1
```

## v0.4.21 PASS criteria

- this plan exists in `docs/dev/`
- Python compile passes
- permanent Exam Prep smoke passes
- permanent Exam Prep health checkpoint passes
- no application runtime logic is changed

## v0.4.26 consolidation status update

The consolidation plan from v0.4.21 has now been executed through small protected milestones.

Completed cleanup milestones:

- v0.4.22 — dashboard rendering consolidation
  - added `render_exam_prep_dashboard_sections_html()`
  - added `exam-prep-dashboard-consolidated-v0422`
  - preserved dashboard order: `Ce să faci acum?` → `Rezumat progres` → `Skill-uri Exam Prep`

- v0.4.23 — skill detail rendering consolidation
  - added `render_exam_prep_skill_detail_sections_html(skill_id)`
  - added `exam-prep-skill-detail-consolidated-v0423`
  - preserved related questions before next action

- v0.4.24 — wording wrapper cleanup
  - removed legacy wording wrapper/middleware blocks
  - kept consolidated dashboard and skill detail helpers as canonical paths
  - preserved approved Romanian wording

- v0.4.25 — post-cleanup health checkpoint expansion
  - expanded `scripts/dev/check-exam-prep-health.ps1`
  - now directly guards v0.4.22, v0.4.23 and v0.4.24 markers
  - confirms `Modul Studiu`, `Pregătire examene`, `Funcții`, `În progres`, and `Consolidat`

Current stable safety gate:

```powershell
python -m py_compile .\services\api\exam_prep.py .\services\api\web_app.py .\services\api\study_quiz_builder.py
& .\scripts\dev\smoke-exam-prep-skill-detail.ps1
& .\scripts\dev\check-exam-prep-health.ps1
```

## Recommended next functional phase

After consolidation, the next safe product direction is to return to small functional Exam Prep improvements.

Recommended next milestones:

### Proposed v0.4.27 — Exam Prep skill metadata display

Add read-only metadata to skill detail pages:

- topic group
- short description
- prerequisites if available
- related Study Mode status

Constraints:

- no BKT algorithm changes
- no OCR/PDF/course generation changes
- no packaging/release changes

### Proposed v0.4.28 — Exam Prep weak skill review entry

Improve the path from Exam Prep to existing weak-concept review flows:

- keep it link/display only
- do not change the Study/Review/Progress engine
- protect with smoke and health checkpoint

### Proposed v0.4.29 — Exam Prep sample skill coverage check

Add a test/checkpoint validating that the Bac Matematică M1 skill tree includes expected core areas:

- Mulțimi
- Funcții
- Derivate
- Integrale
- Geometrie

This should remain a test/checkpoint milestone, not a runtime feature.

## Current non-goals remain unchanged

Do not change in this phase:

- OCR
- PDF processing
- course generation
- Study/Review/Progress BKT engine
- packaging
- ZIP/release assets
- public publishing

## v0.4.30 post-consolidation status update

The first post-consolidation functional checkpoints are complete.

Completed functional/test milestones after cleanup:

- v0.4.27 — Exam Prep skill metadata display
  - added read-only metadata to skill detail pages
  - displays `Detalii skill`, `Capitol`, `Descriere`, `Condiții preliminare`, and `Status Modul Studiu`
  - added `exam-prep-skill-metadata-v0427`
  - kept the section before related questions and next action

- v0.4.28 — Exam Prep weak skill review entry
  - added `Revizuire concepte slabe`
  - added `Deschide revizuirea conceptelor slabe`
  - linked to the existing course/library flow through `/#library`
  - added `exam-prep-weak-review-entry-v0428`
  - did not change Review, Study, Progress, or BKT behavior

- v0.4.29 — Exam Prep sample skill coverage check
  - added `scripts/dev/check-exam-prep-skill-coverage.ps1`
  - validates the Bac Matematică M1 skill tree contains:
    - `Mulțimi`
    - `Funcții`
    - `Derivate`
    - `Integrale`
    - `Geometrie`
  - integrated the coverage script into `scripts/dev/check-exam-prep-health.ps1`

Current protected safety gate:

```powershell
python -m py_compile .\services\api\exam_prep.py .\services\api\web_app.py .\services\api\study_quiz_builder.py
& .\scripts\dev\check-exam-prep-skill-coverage.ps1
& .\scripts\dev\smoke-exam-prep-skill-detail.ps1
& .\scripts\dev\check-exam-prep-health.ps1
```

## Recommended next functional phase after v0.4.30

The codebase is now ready for small product improvements again.

Recommended next milestones:

### Proposed v0.4.31 — Exam Prep prerequisites / learning path display

Add a small read-only learning path view on skill detail pages.

Possible display:

- current skill
- prerequisite skills if available
- next recommended neighboring skill if available
- fallback message when prerequisites are not defined

Constraints:

- display only
- no BKT algorithm changes
- no Study/Review/Progress engine changes
- no OCR/PDF/course generation changes

### Proposed v0.4.32 — Exam Prep dashboard learning path entry

Add a dashboard entry that points users toward the learning path.

Possible display:

- `Traseu recomandat`
- recommended skill from existing dashboard next action
- link to skill detail
- no new adaptive engine

### Proposed v0.4.33 — Exam Prep learning path checkpoint

Add a test/checkpoint that validates learning path display markers and approved Romanian terminology.

This should remain test/checkpoint only.

## Current product state

Exam Prep now has:

- dashboard consolidation
- skill detail consolidation
- health checkpoint expansion
- sample skill coverage check
- skill metadata display
- weak concept review entry
- approved Romanian terminology
- permanent smoke and health safety gates

## Current non-goals remain unchanged

Do not change in this phase:

- OCR
- PDF processing
- course generation
- Study/Review/Progress BKT engine
- packaging
- ZIP/release assets
- public publishing

## v0.4.34 learning path status update

The learning path phase is now completed and protected by a permanent checkpoint.

Completed learning path milestones:

- v0.4.31 — Exam Prep prerequisites / learning path display
  - added the skill detail section Traseu de învățare
  - added xam-prep-learning-path-v0431
  - displays Skill curent, Condiții preliminare, and Următorul pas
  - keeps the section order: Detalii skill → Traseu de învățare → Întrebări asociate din Modul Studiu → Acțiune recomandată

- v0.4.32 — Exam Prep dashboard learning path entry
  - added the dashboard section Traseu recomandat
  - added xam-prep-dashboard-learning-path-v0432
  - displays Skill recomandat, Status curent, and Vezi traseul de învățare
  - keeps the dashboard order: Ce să faci acum → Traseu recomandat → Rezumat progres

- v0.4.33 — Exam Prep learning path checkpoint
  - added scripts/dev/check-exam-prep-learning-path.ps1
  - validates dashboard and skill detail learning path markers
  - validates section order
  - validates approved Romanian wording
  - integrated the checkpoint into scripts/dev/check-exam-prep-health.ps1

Current protected safety gate:

``powershell
python -m py_compile .\services\api\exam_prep.py .\services\api\web_app.py .\services\api\study_quiz_builder.py
& .\scripts\dev\check-exam-prep-skill-coverage.ps1
& .\scripts\dev\check-exam-prep-learning-path.ps1
& .\scripts\dev\smoke-exam-prep-skill-detail.ps1
& .\scripts\dev\check-exam-prep-health.ps1
``

## Recommended next functional phase after v0.4.34

The Exam Prep UI now has a stable dashboard, skill detail pages, metadata, weak-review entry, and learning path.

Recommended next milestones:

### Proposed v0.4.35 — Exam Prep study session entry polish

Improve the copy and CTA around Continuă în Modul Studiu.

Possible changes:

- clarify that progress updates after answering Study Mode questions
- keep the action display-only / link-only
- do not alter quiz generation, BKT, or study state calculations

### Proposed v0.4.36 — Exam Prep progress interpretation helper

Add small read-only explanatory text for statuses:

- Nepornit
- În progres
- Consolidat

This should be UI/copy only and should not change thresholds or scoring.

### Proposed v0.4.37 — Exam Prep learning path docs/checkpoint refresh

Add a checkpoint/doc refresh after v0.4.35-v0.4.36 if those UI polish milestones are completed.

## Current product state

Exam Prep now has:

- dashboard consolidation
- skill detail consolidation
- Romanian wording cleanup
- expanded health checkpoint
- sample skill coverage check
- skill metadata display
- weak concept review entry
- skill detail learning path
- dashboard learning path entry
- permanent learning path checkpoint

## Current non-goals remain unchanged

Do not change in this phase:

- OCR
- PDF processing
- course generation
- Study/Review/Progress BKT engine
- scoring thresholds
- packaging
- ZIP/release assets
- public publishing

## v0.4.37 study/progress copy checkpoint update

The Study Mode entry and progress interpretation polish phase is now protected by a permanent checkpoint.

Completed milestones:

- v0.4.35 — Exam Prep study session entry polish
  - added Intrare în Modul Studiu
  - clarified that Exam Prep progress updates after answering questions in Modul Studiu
  - kept the action display-only / link-only
  - did not change quiz generation, BKT, scoring, Study, Review, or Progress engine behavior

- v0.4.36 — Exam Prep progress interpretation helper
  - added Cum interpretăm progresul
  - explains Nepornit, În progres, and Consolidat
  - clarifies that the helper does not modify scores, thresholds, or BKT

- v0.4.37 — Exam Prep study/progress copy checkpoint
  - added scripts/dev/check-exam-prep-study-progress-copy.ps1
  - validates Study Mode entry copy and CTA
  - validates progress interpretation copy
  - validates section order and approved Romanian wording
  - integrated the checkpoint into scripts/dev/check-exam-prep-health.ps1

Current protected safety gate:

``powershell
python -m py_compile .\services\api\exam_prep.py .\services\api\web_app.py .\services\api\study_quiz_builder.py
& .\scripts\dev\check-exam-prep-skill-coverage.ps1
& .\scripts\dev\check-exam-prep-learning-path.ps1
& .\scripts\dev\check-exam-prep-study-progress-copy.ps1
& .\scripts\dev\smoke-exam-prep-skill-detail.ps1
& .\scripts\dev\check-exam-prep-health.ps1
``

## Recommended next functional phase after v0.4.37

Recommended next milestones:

### Proposed v0.4.38 — Exam Prep dashboard compactness polish

Small UI/copy polish for dashboard density. Keep order and existing markers stable; no logic changes.

### Proposed v0.4.39 — Exam Prep skill detail compactness polish

Small UI/copy polish for skill detail page density. Keep all sections and reduce duplication between Study entry, progress interpretation, and next action; no Study/Review/Progress or BKT changes.

### Proposed v0.4.40 — Exam Prep post-polish checkpoint refresh

Refresh checkpoint/docs after v0.4.38-v0.4.39 if those UI polish milestones are completed.

Current non-goals remain unchanged: OCR, PDF processing, course generation, quiz generation, Study/Review/Progress BKT engine, scoring thresholds, packaging, ZIP/release assets, and public publishing.

## v0.4.40 post-polish checkpoint update

The compactness polish phase is now protected by a permanent checkpoint.

Completed milestones:

- v0.4.38 — Exam Prep dashboard compactness polish
  - added compact dashboard wrapper/style
  - kept all existing dashboard sections
  - preserved the v0.4.22 dashboard consolidation marker
  - preserved dashboard order: Ce să faci acum → Traseu recomandat → Rezumat progres → Cum interpretăm progresul → Skill-uri Exam Prep → Revizuire concepte slabe
  - did not change runtime logic, scoring, BKT, quiz generation, OCR, PDF processing, or packaging

- v0.4.39 — Exam Prep skill detail compactness polish
  - added compact skill detail wrapper/style
  - kept all existing skill detail sections
  - preserved the v0.4.23 skill detail consolidation marker
  - preserved v0.4.24 cleanup/source compatibility markers
  - preserved skill detail order: Detalii skill → Traseu de învățare → Întrebări asociate din Modul Studiu → Intrare în Modul Studiu → Cum interpretăm progresul → Acțiune recomandată → Revizuire concepte slabe
  - did not change runtime logic, scoring, BKT, quiz generation, OCR, PDF processing, or packaging

- v0.4.40 — Exam Prep compactness checkpoint
  - added scripts/dev/check-exam-prep-compactness.ps1
  - validates dashboard compactness markers and order
  - validates skill detail compactness markers and order
  - validates historical consolidation markers
  - validates approved Romanian wording
  - integrated the checkpoint into scripts/dev/check-exam-prep-health.ps1

Current protected safety gate:

``powershell
python -m py_compile .\services\api\exam_prep.py .\services\api\web_app.py .\services\api\study_quiz_builder.py
& .\scripts\dev\check-exam-prep-skill-coverage.ps1
& .\scripts\dev\check-exam-prep-learning-path.ps1
& .\scripts\dev\check-exam-prep-study-progress-copy.ps1
& .\scripts\dev\check-exam-prep-compactness.ps1
& .\scripts\dev\smoke-exam-prep-skill-detail.ps1
& .\scripts\dev\check-exam-prep-health.ps1
``

## Recommended next functional phase after v0.4.40

Recommended next milestones:

### Proposed v0.4.41 — Exam Prep final consolidation status doc

Documentation-only milestone that summarizes the full v0.4.x Exam Prep stabilization chain and identifies what is safe to build next.

### Proposed v0.4.42 — Exam Prep real progress data audit

Read-only audit of where progress data currently comes from:

- Study Mode answers
- Review weak concepts
- dashboard summaries
- skill detail summaries

No BKT/scoring changes.

### Proposed v0.4.43 — Exam Prep next functional planning checkpoint

Planning-only milestone for the next functional phase, likely around real generated question quality and better practice sessions.

Current non-goals remain unchanged:

- OCR
- PDF processing
- course generation
- quiz generation
- Study/Review/Progress BKT engine
- scoring thresholds
- packaging
- ZIP/release assets
- public publishing

## v0.4.41 final consolidation status

This milestone records the completed Exam Prep v0.4.x stabilization chain and defines what is safe to build next.

### Completed stabilization chain

Exam Prep v0.4.x now includes:

- dashboard progress summary polish
- dashboard skill cards polish
- Romanian wording cleanup
- Modul Studiu wording normalization
- related Study Mode questions on skill detail pages
- next action on skill detail pages
- next action on dashboard
- dashboard section ordering
- dashboard visual polish
- permanent health checkpoint expansion
- dashboard rendering consolidation
- skill detail rendering consolidation
- post-cleanup health expansion
- skill metadata display
- weak concept review entry
- sample skill coverage checkpoint
- skill detail learning path display
- dashboard learning path entry
- learning path checkpoint
- Study Mode entry polish
- progress interpretation helper
- Study/Progress copy checkpoint
- dashboard compactness polish
- skill detail compactness polish
- compactness checkpoint

### Current protected safety gate

``powershell
python -m py_compile .\services\api\exam_prep.py .\services\api\web_app.py .\services\api\study_quiz_builder.py
& .\scripts\dev\check-exam-prep-skill-coverage.ps1
& .\scripts\dev\check-exam-prep-learning-path.ps1
& .\scripts\dev\check-exam-prep-study-progress-copy.ps1
& .\scripts\dev\check-exam-prep-compactness.ps1
& .\scripts\dev\smoke-exam-prep-skill-detail.ps1
& .\scripts\dev\check-exam-prep-health.ps1
``

### Current stable dashboard

The dashboard should preserve:

- Ce să faci acum
- Traseu recomandat
- Rezumat progres
- Cum interpretăm progresul
- Skill-uri Exam Prep
- Revizuire concepte slabe

Important dashboard markers:

- xam-prep-dashboard-consolidated-v0422
- xam-prep-dashboard-compact-v0438

### Current stable skill detail page

The skill detail page should preserve:

- Detalii skill
- Traseu de învățare
- Întrebări asociate din Modul Studiu
- Intrare în Modul Studiu
- Cum interpretăm progresul
- Acțiune recomandată
- Revizuire concepte slabe

Important skill detail markers:

- xam-prep-skill-detail-consolidated-v0423
- xam-prep-skill-detail-compact-v0439

### Approved Romanian terminology

Keep using:

- Pregătire examene
- Modul Studiu
- Consolidat
- Nepornit
- În progres
- Traseu recomandat
- Traseu de învățare
- Întrebări asociate din Modul Studiu
- Revizuire concepte slabe

Avoid reintroducing:

- Study Mode
- Exam Prep as a Romanian navigation label where Pregătire examene is expected
- Stăpânire / Stapanire
- visible ASCII regressions such as Functii or In progres

Technical slugs such as /exam-prep/skill/functii remain allowed.

### Current non-goals

This consolidation chain did not change:

- OCR
- PDF processing
- course generation
- quiz generation
- Study Mode generation
- Review weak concepts engine
- Progress engine
- BKT algorithm
- scoring thresholds
- packaging
- ZIP/release assets
- public publishing

### Safe next phase

The next phase should be read-only first.

Recommended next milestones:

#### Proposed v0.4.42 — Exam Prep real progress data audit

Read-only audit of where progress data currently comes from:

- Study Mode answers
- Review weak concepts
- dashboard summaries
- skill detail summaries
- generated question sources
- weak skill links

No BKT/scoring changes.

#### Proposed v0.4.43 — Exam Prep generated question quality audit

Read-only audit of current generated question quality:

- repetitiveness
- overly simple questions
- missing reasoning steps
- weak distractors
- lack of problem variety
- poor connection between course content and exam-prep skills

No generation engine changes yet.

#### Proposed v0.4.44 — Exam Prep next functional planning checkpoint

Planning-only milestone for the next functional phase.

Likely direction:

- improve real question quality
- improve practice session depth
- add better skill-specific prompts/templates
- keep local/no-API path available

### Final status

Exam Prep is stable enough for the next planning/audit phase.

Do not start a large functional rewrite until the read-only progress data audit and generated question quality audit are complete.

## v0.4.42 real progress data audit

This milestone adds a read-only progress data audit.

Added:

- scripts/dev/audit-exam-prep-progress-data.ps1
- docs/dev/exam-prep-real-progress-data-audit.md

The audit verifies current progress-related surfaces:

- dashboard progress summary
- dashboard learning path
- dashboard weak review entry
- skill detail metadata
- skill detail learning path
- related Study Mode questions
- Study Mode entry
- progress interpretation helper
- next action
- weak review entry
- sample skill tree coverage

The audit is integrated into:

- scripts/dev/check-exam-prep-health.ps1

Current safety gate now includes:

``powershell
& .\scripts\dev\audit-exam-prep-progress-data.ps1 -Mode Check
``

### v0.4.42 result

The audit is read-only and does not change:

- BKT
- scoring thresholds
- quiz generation
- Study/Review/Progress engine
- OCR
- PDF processing
- course generation
- packaging
- ZIP/release assets

### Recommended next milestone

Proceed with:

- v0.4.43 — Exam Prep generated question quality audit

This should be read-only first and should evaluate:

- repetitive questions
- overly simple questions
- weak distractors
- missing reasoning steps
- missing exam-grade variations
- poor mapping between course content and skill-specific practice

## v0.4.43 generated question quality audit

Status: read-only checkpoint.

Purpose: record the safe transition from Exam Prep UI/progress consolidation toward generated question quality improvements.

Scope:

- add `docs/dev/exam-prep-generated-question-quality-audit.md`
- keep current Exam Prep UI and progress behavior unchanged
- do not change question generation logic yet
- do not introduce cloud/API costs
- prepare the next step: `v0.4.44 — Local Pedagogy Engine scaffold`

Recommended next step:

- v0.4.44 — Local Pedagogy Engine scaffold

## v0.4.44 Local Pedagogy Engine scaffold

Status: scaffold checkpoint.

Purpose: add the first local-only content supplier foundation after the v0.4.43 generated question quality audit.

Scope:

- add `services/api/local_pedagogy_engine.py`
- add `scripts/dev/check-local-pedagogy-engine.ps1`
- add `docs/dev/local-pedagogy-engine-scaffold.md`
- generate deterministic scaffold structures for:
  - `course_analysis.local.json`
  - `exercise_bank.local.json`
  - `exam_blueprint.local.json`
- keep Exam Prep UI and progress behavior unchanged
- keep legacy quiz/question fallback
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.45 — Local exercise bank discovery and non-destructive Exam Prep fallback integration

## v0.4.45 Local exercise bank discovery

Status: scaffold integration checkpoint.

Purpose: add a safe discovery and validation layer for `exercise_bank.local.json` after the v0.4.44 Local Pedagogy Engine scaffold.

Scope:

- add `services/api/local_exercise_bank.py`
- add `scripts/dev/check-local-exercise-bank-discovery.ps1`
- add `docs/dev/local-exercise-bank-discovery.md`
- validate minimum local exercise-bank schema
- expose selected valid local bank diagnostics
- keep Exam Prep UI and progress behavior unchanged
- keep legacy quiz/question fallback
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.46 — Non-destructive Exam Prep local exercise bank source preview

## v0.4.46 Exam Prep local bank preview

Status: non-destructive backend/diagnostic preview.

Purpose: preview whether Exam Prep can see a valid `exercise_bank.local.json` source without replacing current legacy quiz/question behavior.

Scope:

- add `services/api/exam_prep_local_bank_preview.py`
- add `scripts/dev/check-exam-prep-local-bank-preview.ps1`
- add `docs/dev/exam-prep-local-bank-preview.md`
- preview source availability:
  - `local_exercise_bank_preview` when a valid local bank exists
  - `legacy_fallback` when no valid local bank exists
- keep Exam Prep UI and progress behavior unchanged
- keep legacy quiz/question fallback
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.47 — Local bank source adapter for Exam Prep

## v0.4.47 Local bank source adapter

Status: read-only adapter checkpoint.

Purpose: normalize local `exercise_bank.local.json` exercises into Exam Prep-compatible question records without changing live Exam Prep behavior.

Scope:

- add `services/api/exam_prep_local_bank_adapter.py`
- add `scripts/dev/check-local-bank-source-adapter.ps1`
- add `docs/dev/local-bank-source-adapter.md`
- normalize fields:
  - `question_id`
  - `skill_id`
  - `question_type`
  - `difficulty`
  - `question`
  - `choices`
  - `correct_answer`
  - `explanation`
  - `source = local_exercise_bank_adapter`
- preserve legacy fallback when no valid local bank exists
- keep Exam Prep UI and progress behavior unchanged
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.48 — Exam Prep local bank adapter diagnostics route/check

## v0.4.48 Exam Prep local bank diagnostics

Status: read-only diagnostics checkpoint.

Purpose: report adapted local exercise bank availability and validation without enabling live Exam Prep consumption.

Scope:

- add `services/api/exam_prep_local_bank_diagnostics.py`
- add `scripts/dev/check-exam-prep-local-bank-diagnostics.ps1`
- add `docs/dev/exam-prep-local-bank-diagnostics.md`
- report:
  - active source adapter
  - local question count
  - question type coverage
  - difficulty coverage
  - skill coverage
  - sample question ids
  - normalized field validation
  - legacy fallback availability
- keep Exam Prep UI and progress behavior unchanged
- keep legacy quiz/question fallback
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.49 — Local bank read-only study preview

## v0.4.49 Local bank read-only study preview

Status: read-only study preview checkpoint.

Purpose: preview normalized local-bank questions for a skill without saving attempts, updating progress, scoring answers, or replacing live study sessions.

Scope:

- add `services/api/exam_prep_local_bank_study_preview.py`
- add `scripts/dev/check-local-bank-study-preview.ps1`
- add `docs/dev/local-bank-read-only-study-preview.md`
- preview local-bank questions for a selected skill
- expose available skill counts for diagnostics
- keep Exam Prep UI and progress behavior unchanged
- keep live study sessions unchanged
- keep legacy quiz/question fallback
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.50 — Local bank study preview diagnostics route or protected UI marker

## v0.4.50 Local bank protected preview route

Status: protected read-only route checkpoint.

Purpose: expose the local-bank read-only study preview through an internal/protected backend route, disabled by default.

Scope:

- add `GET /exam-prep/local-bank-study-preview`
- gate the route with `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE=1`
- add `scripts/dev/check-local-bank-protected-preview-route.ps1`
- add `docs/dev/local-bank-protected-preview-route.md`
- keep Exam Prep UI and progress behavior unchanged
- keep live study sessions unchanged
- keep legacy quiz/question fallback
- do not save attempts, score answers, or update progress
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.51 — Local bank preview UI marker or internal panel

## v0.4.51 Local bank preview internal panel

Status: protected/internal read-only diagnostics panel.

Purpose: expose the local-bank read-only study preview in a minimal internal HTML panel, disabled by default and not linked publicly.

Scope:

- add `GET /exam-prep/local-bank-study-preview/panel`
- gate the panel with `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_PREVIEW_ROUTE=1`
- add `scripts/dev/check-local-bank-preview-internal-panel.ps1`
- add `docs/dev/local-bank-preview-internal-panel.md`
- keep Exam Prep UI and progress behavior unchanged
- keep live study sessions unchanged
- keep legacy quiz/question fallback
- do not save attempts, score answers, or update progress
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.52 — Local bank controlled consumption flag scaffold

## v0.4.52 Local bank controlled consumption flag

Status: disabled-by-default consumption flag scaffold.

Purpose: introduce an explicit flag for future controlled local-bank consumption while preserving legacy fallback as default.

Scope:

- add `services/api/exam_prep_local_bank_consumption_flag.py`
- add `scripts/dev/check-local-bank-consumption-flag.ps1`
- add `docs/dev/local-bank-controlled-consumption-flag.md`
- introduce `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION`
- default OFF selects `legacy_fallback`
- ON selects `local_exercise_bank_adapter` only in diagnostic source-selection snapshot
- keep Exam Prep UI and progress behavior unchanged
- keep live study sessions unchanged
- keep legacy quiz/question fallback
- do not save attempts, score answers, or update progress
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.53 — Local bank source selection adapter for dry-run study sessions

## v0.4.53 Local bank dry-run source selection

Status: dry-run source selection scaffold.

Purpose: model which source a future Exam Prep study session would select while preserving legacy fallback and avoiding live consumption.

Scope:

- add `services/api/exam_prep_local_bank_dry_run_source_selection.py`
- add `scripts/dev/check-local-bank-dry-run-source-selection.ps1`
- add `docs/dev/local-bank-dry-run-source-selection.md`
- use `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION`
- OFF selects `legacy_fallback`
- ON selects `local_exercise_bank_adapter` only for dry-run items
- keep Exam Prep UI and progress behavior unchanged
- keep live study sessions unchanged
- keep legacy quiz/question fallback
- do not save attempts, score answers, or update progress
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.54 — Local bank dry-run question quality gate

## v0.4.54 Local bank dry-run question quality gate

Status: dry-run quality gate.

Purpose: detect repetitive/simple local-bank questions before any future live Exam Prep consumption.

Scope:

- add `services/api/exam_prep_local_bank_question_quality_gate.py`
- add `scripts/dev/check-local-bank-question-quality-gate.ps1`
- add `docs/dev/local-bank-dry-run-question-quality-gate.md`
- detect repetitive concept-recognition wording
- detect insufficient question type diversity
- validate required fields
- mark current scaffold output as `needs_improvement`
- keep Exam Prep UI and progress behavior unchanged
- keep live study sessions unchanged
- keep legacy quiz/question fallback
- do not save attempts, score answers, or update progress
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.55 — Local pedagogy question variety upgrade

## v0.4.55 Local pedagogy question variety upgrade

Status: local-only question variety upgrade.

Purpose: improve deterministic local question generation so the local bank contains varied question types and passes the dry-run quality gate.

Scope:

- update `services/api/local_pedagogy_engine.py`
- update `scripts/dev/check-local-bank-question-quality-gate.ps1`
- add `scripts/dev/check-local-pedagogy-question-variety.ps1`
- add `docs/dev/local-pedagogy-question-variety-upgrade.md`
- generate question types:
  - multiple_choice
  - short_answer
  - evidence_based
  - compare_concepts
  - apply_concept
  - formula_interpretation
  - apply_formula
- preserve legacy fallback
- keep Exam Prep UI and progress behavior unchanged
- keep live study sessions unchanged
- do not save attempts, score answers, or update progress
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.56 — Local-bank dry-run answer evaluation scaffold

## v0.4.56 Local bank dry-run answer evaluation

Status: dry-run answer evaluation scaffold.

Purpose: evaluate answers to local-bank dry-run questions without persisting attempts or updating progress.

Scope:

- add `services/api/exam_prep_local_bank_dry_run_answer_evaluation.py`
- add `scripts/dev/check-local-bank-dry-run-answer-evaluation.ps1`
- add `docs/dev/local-bank-dry-run-answer-evaluation.md`
- support normalized exact matching for multiple-choice
- support keyword overlap for open-answer questions
- generate local feedback previews
- keep Exam Prep UI and progress behavior unchanged
- keep live study sessions unchanged
- keep legacy quiz/question fallback
- do not persist attempts, score live sessions, or update progress
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs
- do not require OpenAI, Mathpix, Ollama, or LM Studio

Recommended next step:

- v0.4.57 — Local-bank dry-run attempt envelope

## v0.4.57 Local bank dry-run attempt envelope

Status: dry-run attempt envelope scaffold.

Purpose: wrap dry-run question, submitted answer, local evaluation, and feedback preview into an attempt-like object without persisting it.

Scope:

- add `services/api/exam_prep_local_bank_dry_run_attempt_envelope.py`
- add `scripts/dev/check-local-bank-dry-run-attempt-envelope.ps1`
- add `docs/dev/local-bank-dry-run-attempt-envelope.md`
- include question snapshot, submitted answer, verdict, score preview, feedback preview, and persistence flags
- keep Exam Prep UI and progress behavior unchanged
- keep live study sessions unchanged
- do not persist attempts, score live sessions, or update progress
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.58 — Local-bank dry-run session summary

## v0.4.58 Local bank dry-run session summary

Status: dry-run session summary scaffold.

Purpose: group non-persistent local-bank dry-run attempt envelopes into a session-like summary.

Scope:

- add `services/api/exam_prep_local_bank_dry_run_session_summary.py`
- add `scripts/dev/check-local-bank-dry-run-session-summary.ps1`
- add `docs/dev/local-bank-dry-run-session-summary.md`
- include dry_run_session_id, total_questions, verdict counts, average_score_preview, feedback_summary, and envelopes
- keep Exam Prep UI and progress behavior unchanged
- keep live study sessions unchanged
- do not persist sessions or attempts
- do not score live sessions or update progress
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.59 — Local-bank dry-run progress impact preview

## v0.4.59 Local bank dry-run progress impact preview

Status: dry-run progress impact preview.

Purpose: simulate how a dry-run local-bank session summary could affect skill mastery without writing progress.

Scope:

- add `services/api/exam_prep_local_bank_dry_run_progress_impact.py`
- add `scripts/dev/check-local-bank-dry-run-progress-impact.ps1`
- add `docs/dev/local-bank-dry-run-progress-impact-preview.md`
- include old_mastery_preview, mastery_delta_preview, new_mastery_preview, and impact_direction
- keep Exam Prep UI and real progress behavior unchanged
- keep live study sessions unchanged
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.60 — Local-bank dry-run integration readiness report

## v0.4.60 Local bank integration readiness report

Status: pre-live readiness report.

Purpose: verify the full local-bank dry-run chain before any future guarded live trial.

Scope:

- add `services/api/exam_prep_local_bank_integration_readiness.py`
- add `scripts/dev/check-local-bank-integration-readiness.ps1`
- add `docs/dev/local-bank-integration-readiness-report.md`
- verify controlled flag, source selection, quality gate, answer evaluation, attempt envelope, session summary, and progress impact preview
- produce `readiness_status`
- keep Exam Prep UI and real progress behavior unchanged
- keep live study sessions unchanged
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.61 — Guarded local-bank live-trial scaffold, disabled by default

## v0.4.61 Local bank guarded live-trial scaffold

Status: disabled-by-default guarded live-trial scaffold.

Purpose: prepare a guarded live-trial plan after v0.4.60 readiness without wiring local-bank questions into live study sessions.

Scope:

- add `services/api/exam_prep_local_bank_guarded_live_trial.py`
- add `scripts/dev/check-local-bank-guarded-live-trial.ps1`
- add `docs/dev/local-bank-guarded-live-trial-scaffold.md`
- introduce `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL`
- default OFF reports disabled
- flag ON + readiness ready reports `guarded_trial_plan_ready`
- keep Exam Prep UI and real progress behavior unchanged
- keep live study sessions unchanged
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.62 — Guarded live-trial adapter boundary, disabled by default

## v0.4.62 Local bank guarded live-trial adapter boundary

Status: disabled-by-default adapter boundary scaffold.

Purpose: create a boundary object between a future study session and the local-bank source without wiring local bank into live study sessions.

Scope:

- add `services/api/exam_prep_local_bank_guarded_adapter_boundary.py`
- add `scripts/dev/check-local-bank-guarded-adapter-boundary.ps1`
- add `docs/dev/local-bank-guarded-adapter-boundary.md`
- flag OFF reports `legacy_fallback_only`
- flag ON + v0.4.61 trial plan ready reports `local_source_candidate_available`
- return `local_source_candidate`
- keep Exam Prep UI and real progress behavior unchanged
- keep live study sessions unchanged
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.63 — Guarded live-trial no-op study-session hook, disabled by default

## v0.4.63 Local bank guarded live-trial no-op study-session hook

Status: disabled-by-default no-op study-session hook scaffold.

Purpose: add a no-op hook-shaped boundary that can report a local-bank candidate while keeping live study sessions on legacy fallback.

Scope:

- add `services/api/exam_prep_local_bank_noop_study_session_hook.py`
- add `scripts/dev/check-local-bank-noop-study-session-hook.ps1`
- add `docs/dev/local-bank-noop-study-session-hook.md`
- flag OFF reports `legacy_path_unchanged`
- flag ON + v0.4.62 candidate reports `local_source_candidate_reported_noop`
- keep effective source as `legacy_fallback`
- do not consume local-bank questions live
- keep Exam Prep UI and real progress behavior unchanged
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.64 — Guarded live-trial route smoke, disabled by default

## v0.4.64 Local bank guarded live-trial route smoke

Status: disabled-by-default internal JSON smoke route.

Purpose: add a protected route that smoke-tests the v0.4.63 no-op study-session hook without consuming local-bank questions live.

Scope:

- add `GET /exam-prep/local-bank/guarded-trial-smoke`
- add `scripts/dev/check-local-bank-guarded-trial-route-smoke.ps1`
- add `docs/dev/local-bank-guarded-trial-route-smoke.md`
- gate the route with `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_SMOKE_ROUTE`
- keep JSON-only output
- keep no public UI link
- report hook_status, effective_source, and candidate availability
- keep effective source as `legacy_fallback`
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.65 — Guarded live-trial route diagnostics panel, JSON-only and disabled by default

## v0.4.65 Local bank guarded live-trial diagnostics route

Status: disabled-by-default internal JSON diagnostics route.

Purpose: add a compact diagnostics report route for the guarded local-bank trial chain without consuming local-bank questions live.

Scope:

- add `GET /exam-prep/local-bank/guarded-trial-diagnostics`
- add `scripts/dev/check-local-bank-guarded-trial-diagnostics-route.ps1`
- add `docs/dev/local-bank-guarded-trial-diagnostics-route.md`
- gate the route with `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE`
- keep JSON-only output
- keep no public UI link
- report hook_status, boundary_status, readiness_status, candidate availability, effective_source, and safety flags
- keep effective source as `legacy_fallback`
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.66 — Guarded live-trial candidate question preview route, disabled by default

## v0.4.66 Local bank guarded live-trial candidate question preview route

Status: disabled-by-default internal JSON candidate question preview route.

Purpose: preview candidate local-bank questions for a future guarded trial without exposing answer previews or consuming local-bank questions live.

Scope:

- add `GET /exam-prep/local-bank/guarded-trial-candidates`
- add `scripts/dev/check-local-bank-guarded-trial-candidates-route.ps1`
- add `docs/dev/local-bank-guarded-trial-candidates-route.md`
- gate the route with `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE`
- require diagnostics and guarded trial flags for candidate readiness
- keep JSON-only output
- hide answer and explanation previews
- keep effective source as `legacy_fallback`
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.67 — Guarded live-trial candidate preview UI panel, hidden/internal and disabled by default

## v0.4.67 Local bank guarded live-trial candidate preview internal panel

Status: disabled-by-default hidden/internal candidate preview panel.

Purpose: preview candidate local-bank questions in an internal panel by reading the v0.4.66 candidate route, without exposing answers or consuming local-bank questions live.

Scope:

- add `GET /exam-prep/local-bank/guarded-trial-candidates-panel`
- add `scripts/dev/check-local-bank-guarded-trial-candidates-panel.ps1`
- add `docs/dev/local-bank-guarded-trial-candidates-panel.md`
- gate the panel with `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL`
- keep noindex/nofollow
- keep hidden/internal status and no public UI link
- fetch candidate questions from v0.4.66
- hide answer and explanation previews
- keep effective source as `legacy_fallback`
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.68 — Guarded live-trial candidate preview panel polish and owner smoke

## v0.4.68 Local bank guarded live-trial candidate panel polish owner smoke

Status: disabled-by-default hidden/internal candidate panel polish and owner smoke.

Purpose: polish the internal candidate preview panel with clearer status, summary, badges, and safe DOM rendering while keeping local-bank consumption disabled.

Scope:

- add `GET /exam-prep/local-bank/guarded-trial-candidates-panel-polish`
- add `scripts/dev/check-local-bank-guarded-trial-candidates-panel-polish.ps1`
- add `docs/dev/local-bank-guarded-trial-candidates-panel-polish.md`
- gate the panel with `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH`
- keep noindex/nofollow
- keep hidden/internal owner-smoke status and no public UI link
- fetch candidate questions from v0.4.66
- add summary cards and badges
- use safe DOM rendering without `innerHTML`
- hide answer and explanation previews
- keep effective source as `legacy_fallback`
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.69 — Guarded local-bank trial explicit owner enablement checklist

## v0.4.69 Guarded local-bank owner enablement checklist

Status: JSON-only local owner enablement checklist.

Purpose: add an explicit owner-facing enablement checklist before any future milestone can attempt real guarded live consumption.

Scope:

- add `services/api/exam_prep_local_bank_owner_enablement_checklist.py`
- add `scripts/dev/check-local-bank-owner-enablement-checklist.ps1`
- add `docs/dev/local-bank-owner-enablement-checklist.md`
- verify readiness, guarded trial plan, adapter boundary, no-op hook, required flags, and preview/panel prerequisites
- define minimum criteria for v0.4.70
- explicitly record what is still not live
- keep effective source as `legacy_fallback`
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.70 — Guarded local-bank live consumption decision gate, still disabled by default

## v0.4.70 Guarded local-bank live consumption decision gate

Status: disabled-by-default decision gate.

Purpose: add an explicit gate after v0.4.69 that can report whether the system is eligible for owner decision, without enabling live local-bank consumption.

Scope:

- add `services/api/exam_prep_local_bank_live_consumption_decision_gate.py`
- add `scripts/dev/check-local-bank-live-consumption-decision-gate.ps1`
- add `docs/dev/local-bank-live-consumption-decision-gate.md`
- introduce `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE`
- report `blocked` or `eligible_for_owner_decision`
- consume v0.4.69 owner enablement checklist output
- list owner decision options
- explicitly record what is still not live
- keep effective source as `legacy_fallback`
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.71 — Guarded live-consumption adapter no-op boundary, still disabled by default

## v0.4.71 Guarded live-consumption adapter no-op boundary

Status: disabled-by-default no-op adapter boundary.

Purpose: add a no-op boundary for a future guarded local-bank live-consumption adapter without enabling live consumption.

Scope:

- add `services/api/exam_prep_local_bank_live_consumption_adapter_noop_boundary.py`
- add `scripts/dev/check-local-bank-live-consumption-adapter-noop-boundary.ps1`
- add `docs/dev/local-bank-live-consumption-adapter-noop-boundary.md`
- introduce `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY`
- consume v0.4.70 decision gate output
- report `legacy_fallback_only` or `live_adapter_candidate_noop`
- define minimum contract for first real live trial
- explicitly record what is still not live
- keep effective source as `legacy_fallback`
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.72 — Guarded live-consumption adapter owner dry-run plan, still disabled by default

## v0.4.72 Guarded local-bank live consumption source selector shadow mode

Status: disabled-by-default shadow source selector.

Purpose: compare local-bank candidate metadata with the legacy fallback path while keeping `effective_source=legacy_fallback`.

Scope:

- add `services/api/exam_prep_local_bank_live_consumption_shadow_selector.py`
- add `scripts/dev/check-local-bank-live-consumption-shadow-selector.ps1`
- add `docs/dev/local-bank-live-consumption-shadow-selector.md`
- introduce `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_SOURCE_SELECTOR`
- consume v0.4.71 adapter no-op boundary output
- report `disabled`, `blocked`, or `shadow_selection_ready`
- produce `shadow_selection_report`
- compare count/type/difficulty/skill coverage
- keep effective source as `legacy_fallback`
- do not deliver local-bank questions live
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.73 — Guarded live-consumption shadow route report, disabled by default

## v0.4.73 Guarded local-bank live consumption shadow route report

Status: disabled-by-default internal JSON-only shadow report route.

Purpose: expose the v0.4.72 shadow selector through a compact sanitized report without raw snapshots, answers, explanations, or preview answer fields.

Scope:

- add `GET /exam-prep/local-bank/live-consumption-shadow-report`
- add `scripts/dev/check-local-bank-live-consumption-shadow-route-report.ps1`
- add `docs/dev/local-bank-live-consumption-shadow-route-report.md`
- introduce `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_ROUTE`
- return selector_status, effective_source, shadow_source, coverage comparison, and safe shadow metadata
- omit correct_answer, correct_answer_preview, explanation, explanation_preview, raw snapshots, selected_questions, and dry_run_items
- keep effective source as `legacy_fallback`
- do not deliver local-bank questions live
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.74 — Guarded live-consumption shadow route owner panel, disabled by default

## v0.4.74 Guarded local-bank live consumption shadow route owner panel

Status: disabled-by-default hidden/internal owner panel.

Purpose: add a hidden owner panel over the v0.4.73 sanitized shadow report route, showing selector/source/coverage and selected shadow metadata without answers, explanations, or raw snapshots.

Scope:

- add `GET /exam-prep/local-bank/live-consumption-shadow-panel`
- add `scripts/dev/check-local-bank-live-consumption-shadow-owner-panel.ps1`
- add `docs/dev/local-bank-live-consumption-shadow-owner-panel.md`
- introduce `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_OWNER_PANEL`
- read v0.4.73 sanitized report route
- render selector_status, effective_source, shadow_source, coverage, and metadata-only shadow items
- use safe DOM rendering without `innerHTML`
- omit correct_answer, correct_answer_preview, explanation, explanation_preview, raw snapshots, selected_questions, and dry_run_items
- keep effective source as `legacy_fallback`
- do not deliver local-bank questions live
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not accept user-provided filesystem roots
- do not introduce cloud/API costs

Recommended next step:

- v0.4.75 — Guarded live-consumption shadow report/panel consolidation status

## v0.4.75 Guarded live-consumption shadow consolidation status

Status: JSON-only consolidation status for the guarded local-bank shadow chain.

Purpose: consolidate v0.4.60-v0.4.74 before any future step toward real live consumption.

Scope:

- add `services/api/exam_prep_local_bank_shadow_consolidation_status.py`
- add `scripts/dev/check-local-bank-shadow-consolidation-status.ps1`
- add `docs/dev/local-bank-shadow-consolidation-status.md`
- confirm all shadow-chain milestones are recorded
- confirm internal routes/panels and flags
- confirm `effective_source=legacy_fallback`
- confirm shadow report and owner panel are sanitized
- confirm answers, explanations, raw snapshots, dry_run_items, and selected_questions stay out of web routes/panels
- confirm no live local-bank question delivery or consumption
- confirm no attempts/progress/session persistence
- confirm no live scoring
- confirm no public UI changes
- define next-phase criteria

Recommended next step:

- v0.4.76 — Guarded local-bank first live trial planning document, still no code-path change

## v0.4.76 Guarded local-bank first live trial planning document

Status: planning-only document; no live code-path change.

Purpose: define what a first real guarded local-bank live trial would mean before any implementation changes the source, session, attempts, progress, or scoring paths.

Scope:

- add `docs/dev/local-bank-first-live-trial-planning-document.md`
- add `scripts/dev/check-local-bank-first-live-trial-planning-document.ps1`
- define the meaning of "live"
- define abort/fallback rules to `legacy_fallback`
- define leakage/XSS/CodeQL risks
- define minimum criteria for attempt persistence
- define minimum criteria for progress updates
- define minimum criteria for live scoring
- confirm `effective_source=legacy_fallback`
- confirm no web route or runtime source path is changed
- keep local-bank questions non-live
- keep attempts/progress/sessions/scoring disabled

Recommended next step:

- v0.4.77 — Guarded first live trial contract skeleton, disabled by default

## v0.4.77 Guarded first live trial contract skeleton

Status: JSON-only contract skeleton; disabled by default.

Purpose: add a contract object for future first live-trial owner review without enabling live local-bank consumption.

Scope:

- add `services/api/exam_prep_local_bank_first_live_trial_contract.py`
- add `scripts/dev/check-local-bank-first-live-trial-contract.ps1`
- add `docs/dev/local-bank-first-live-trial-contract.md`
- introduce `VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT`
- depend on v0.4.75 shadow consolidation status
- define source_selection, session_boundary, attempt_persistence, progress_updates, live_scoring, and sanitization contract sections
- keep `effective_source=legacy_fallback`
- add no web route
- do not patch `services/api/web_app.py`
- do not deliver local-bank questions live
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not introduce cloud/API costs

Recommended next step:

- v0.4.78 — Guarded first live trial contract report route, disabled by default

## v0.4.78 Guarded first live trial contract report route

Status: disabled-by-default internal JSON-only route.

Purpose: expose the v0.4.77 contract skeleton through a compact sanitized route without enabling live local-bank consumption.

Scope:

- add GET /exam-prep/local-bank/first-live-trial-contract-report
- add scripts/dev/check-local-bank-first-live-trial-contract-report-route.ps1
- add docs/dev/local-bank-first-live-trial-contract-report-route.md
- introduce VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_REPORT_ROUTE
- return a sanitized contract report, not the raw contract object
- keep effective_source=legacy_fallback
- do not add public UI
- do not deliver local-bank questions live
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not introduce cloud/API costs

Recommended next step:

- v0.4.79 — Guarded first live trial contract owner panel, disabled by default

## v0.4.79 Guarded first live trial contract owner panel

Status: disabled-by-default hidden/internal owner panel.

Purpose: add an owner-only panel over the v0.4.78 sanitized contract report route without enabling live local-bank consumption.

Scope:

- add GET /exam-prep/local-bank/first-live-trial-contract-panel
- add scripts/dev/check-local-bank-first-live-trial-contract-owner-panel.ps1
- add docs/dev/local-bank-first-live-trial-contract-owner-panel.md
- introduce VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_OWNER_PANEL
- read the v0.4.78 sanitized report route
- use safe DOM rendering without innerHTML
- keep effective_source=legacy_fallback
- do not add public UI
- do not deliver local-bank questions live
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not introduce cloud/API costs

Recommended next step:

- v0.4.80 — Guarded first live trial question envelope sanitizer, disabled by default

## v0.4.80 Guarded first live trial question envelope sanitizer

Status: JSON-only local module; disabled by default.

Purpose: define a safe question envelope sanitizer for future first live-trial delivery without enabling live consumption.

Scope:

- add services/api/exam_prep_local_bank_first_live_trial_question_envelope.py
- add scripts/dev/check-local-bank-first-live-trial-question-envelope.ps1
- add docs/dev/local-bank-first-live-trial-question-envelope.md
- introduce VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_QUESTION_ENVELOPE_SANITIZER
- strip answer, explanation, raw snapshot, raw contract, dry-run, selected-question, and source-excerpt fields
- keep effective_source=legacy_fallback
- add no web route
- do not patch services/api/web_app.py
- do not add public UI
- do not deliver local-bank questions live
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not introduce cloud/API costs

Recommended next step:

- v0.4.81 — Guarded first live trial dry-run session envelope, disabled by default

## v0.4.81 Guarded first live trial dry-run session envelope

Status: JSON-only local module; disabled by default.

Purpose: group sanitized question envelopes into an owner-only dry-run session envelope without enabling live delivery.

Scope:

- add services/api/exam_prep_local_bank_first_live_trial_dry_run_session.py
- add scripts/dev/check-local-bank-first-live-trial-dry-run-session.ps1
- add docs/dev/local-bank-first-live-trial-dry-run-session-envelope.md
- introduce VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_DRY_RUN_SESSION_ENVELOPE
- depend on v0.4.80 question envelope sanitizer
- keep effective_source=legacy_fallback
- add no web route
- do not patch services/api/web_app.py
- do not add public UI
- do not deliver local-bank questions live
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not introduce cloud/API costs

Recommended next step:

- v0.4.82 — Guarded first live trial no-persistence delivery contract, disabled by default

## v0.4.82 Guarded first live trial no-persistence delivery contract

Status: JSON-only local module; disabled by default.

Purpose: define the owner-only no-persistence delivery contract for a future first live trial without enabling delivery yet.

Scope:

- add services/api/exam_prep_local_bank_first_live_trial_delivery_contract.py
- add scripts/dev/check-local-bank-first-live-trial-delivery-contract.ps1
- add docs/dev/local-bank-first-live-trial-delivery-contract.md
- introduce VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_CONTRACT
- depend on v0.4.81 dry-run session envelope
- define no-persistence delivery scope and abort policy
- keep effective_source=legacy_fallback
- add no web route
- do not patch services/api/web_app.py
- do not add public UI
- do not deliver local-bank questions live yet
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not introduce cloud/API costs

Recommended next step:

- v0.4.83 — Guarded first live trial no-persistence delivery adapter no-op, disabled by default

## v0.4.83 Guarded first live trial delivery adapter no-op

Status: JSON-only local module; disabled by default.

Purpose: add a no-op adapter boundary for the future owner-only first live delivery without performing delivery yet.

Scope:

- add services/api/exam_prep_local_bank_first_live_trial_delivery_adapter.py
- add scripts/dev/check-local-bank-first-live-trial-delivery-adapter.ps1
- add docs/dev/local-bank-first-live-trial-delivery-adapter-noop.md
- introduce VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_ADAPTER_NOOP
- depend on v0.4.82 no-persistence delivery contract
- return delivery_performed=false
- keep effective_source=legacy_fallback
- add no web route
- do not patch services/api/web_app.py
- do not add public UI
- do not deliver local-bank questions live yet
- do not consume local-bank questions live
- do not persist progress, sessions, or attempts
- do not score live sessions
- do not introduce cloud/API costs

Recommended next step:

- v0.4.84 — Guarded first live trial no-persistence delivery route scaffold, disabled by default
