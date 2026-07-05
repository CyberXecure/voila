# Voila v0.7.13 owner-local read-only smoke index consolidation

Milestone: `v0.7.13-owner-local-read-only-smoke-index-consolidation-no-build-no-distribution`

## Purpose

This document consolidates the owner-local audit and smoke documentation created across v0.7.9, v0.7.10, v0.7.11, and v0.7.12 into a single navigation index.

It is intentionally documentation-only and read-only. It does not introduce feature changes, UI changes, runtime changes, route changes, build steps, ZIP packaging, delivery, distribution, or public UI expansion.

## Baseline chain

| Milestone | Purpose | Final state |
| --- | --- | --- |
| v0.7.9 | Functional audit baseline | Inventory, smoke map, checklist, audit policy, static/read-only validation |
| v0.7.10 | Manual smoke evidence baseline | Manual smoke runbook, evidence template, risk register, validation |
| v0.7.11 | Read-only route smoke documentation | GET-only route runbook/map/template/policy, static validation |
| v0.7.12 | Read-only route smoke evidence packet | Evidence index/log/session notes/non-destructive boundary, static validation |
| v0.7.13 | Consolidated index | One navigation surface for the v0.7.9-v0.7.12 audit/smoke packet |

## Policy preserved

- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no behavior changes
- no feature changes
- no OCR/pages/course/Study/Progress rewrite
- no public UI expansion
- read-only GET-only for route-smoke documentation
- no non-GET write requests smoke execution
- no upload/generate/save/delete/reset execution
- no server startup required
- no live HTTP smoke required

## Consolidated document index

### v0.7.9 functional audit baseline

- `docs/dev/voila-functional-audit-inventory-v0.7.9.md`
- `docs/dev/voila-functional-smoke-map-v0.7.9.md`
- `docs/dev/voila-functional-test-checklist-v0.7.9.md`
- `docs/dev/voila-functional-audit-policy-v0.7.9.md`
- `scripts/dev/check-voila-functional-audit-baseline-v0.7.9.ps1`

### v0.7.10 manual smoke evidence baseline

- `docs/dev/voila-manual-smoke-runbook-v0.7.10.md`
- `docs/dev/voila-manual-smoke-evidence-v0.7.10.md`
- `docs/dev/voila-manual-smoke-risk-register-v0.7.10.md`
- `scripts/dev/check-voila-manual-smoke-evidence-v0.7.10.ps1`

### v0.7.11 read-only route smoke documentation

- `docs/dev/voila-read-only-route-smoke-runbook-v0.7.11.md`
- `docs/dev/voila-read-only-route-smoke-map-v0.7.11.md`
- `docs/dev/voila-read-only-route-smoke-evidence-template-v0.7.11.md`
- `docs/dev/voila-read-only-route-smoke-policy-v0.7.11.md`
- `scripts/dev/check-voila-read-only-route-smoke-doc-v0.7.11.ps1`

### v0.7.12 read-only route smoke evidence packet

- `docs/dev/voila-read-only-route-smoke-evidence-index-v0.7.12.md`
- `docs/dev/voila-read-only-route-smoke-evidence-log-v0.7.12.md`
- `docs/dev/voila-read-only-route-smoke-session-notes-v0.7.12.md`
- `docs/dev/voila-read-only-route-smoke-non-destructive-boundary-v0.7.12.md`
- `scripts/dev/check-voila-read-only-route-smoke-evidence-v0.7.12.ps1`

### v0.7.13 consolidation packet

- `docs/dev/voila-read-only-smoke-index-consolidation-v0.7.13.md`
- `docs/dev/voila-read-only-smoke-next-step-gate-v0.7.13.md`
- `docs/dev/voila-read-only-smoke-consolidated-risk-notes-v0.7.13.md`
- `scripts/dev/check-voila-read-only-smoke-index-consolidation-v0.7.13.ps1`

## Consolidated route-smoke scope

The route-smoke scope remains documentation-only and GET-only. The static route references are inherited from v0.7.11 and v0.7.12.

Read-only candidate route families:

- `/health`
- `/`
- `/quick-tools`
- `/course-tools`
- `/view-course`
- `/view-figures`
- `/review`
- `/review-concepts`
- `/review-ocr-text`
- `/review-ocr-corrected`
- `/edit-crops`
- `/progress`
- `/study`
- `/exam-prep`
- `/log`
- `/ocr-page-image`
- `/owner/ocr-math-report/{course_id}/summary.json`
- `/owner/ocr-math-report/{course_id}/ocr_math_report.md`
- `/owner/ocr-math-report/{course_id}/view`

Excluded from route-smoke execution in this milestone:

- non-GET write request routes
- upload
- generate
- save
- delete
- reset
- rebuild
- any write-generating or destructive action

## Validation chain

Run the individual validators when needed:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\dev\check-voila-functional-audit-baseline-v0.7.9.ps1 -RepoRoot .
pwsh -ExecutionPolicy Bypass -File .\scripts\dev\check-voila-manual-smoke-evidence-v0.7.10.ps1 -RepoRoot .
pwsh -ExecutionPolicy Bypass -File .\scripts\dev\check-voila-read-only-route-smoke-doc-v0.7.11.ps1 -RepoRoot .
pwsh -ExecutionPolicy Bypass -File .\scripts\dev\check-voila-read-only-route-smoke-evidence-v0.7.12.ps1 -RepoRoot .
pwsh -ExecutionPolicy Bypass -File .\scripts\dev\check-voila-read-only-smoke-index-consolidation-v0.7.13.ps1 -RepoRoot .
```

These commands are documentation/static validation commands only. They must not build, package, deliver, distribute, upload, generate, save, delete, reset, rebuild, start servers, or perform live HTTP smoke.

## Definition of done

v0.7.13 is done when:

- this consolidation index exists
- the next-step gate exists
- consolidated risk notes exist
- the v0.7.13 check script passes
- previous v0.7.9-v0.7.12 document/check references are present
- no build/ZIP/delivery/distribution behavior is introduced
- no runtime behavior is changed
- protected main receives only docs and read-only validation additions

## Mandatory milestone policy

This milestone preserves the required owner-local safety policy:

- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no behavior changes
- no feature changes
- no public UI expansion
- read-only GET-only
- no non-GET write requests
- no upload
- no generate
- no save
- no delete
- no reset
- no server startup
- no live HTTP smoke

This document is documentation-only and static/read-only validation only.




