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
