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

