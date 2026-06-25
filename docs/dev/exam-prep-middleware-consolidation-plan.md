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
