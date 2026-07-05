# Voila Functional Smoke Map v0.7.9

Milestone: `v0.7.9-owner-local-functional-audit-baseline-no-build-no-distribution`

## Policy

This smoke map is documentation-only and read-only.

Required policy:

- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no feature changes
- no OCR/pages/course/Study/Progress rewrite
- no public UI expansion
- no behavior changes

## Smoke map purpose

The smoke map defines what should be manually checked later without changing behavior in this milestone.

v0.7.9 does not execute the complete smoke test. It only defines the map and separates safe read-only checks from write-generating checks.

## Smoke levels

| Level | Description | Allowed in v0.7.9 |
|---|---|---:|
| S0 Static | Read files as text and validate docs/checklist presence | Yes |
| S1 Read-only route | Use GET-only checks against an already running local server | Optional/manual only |
| S2 Existing artifact read | Open existing generated artifacts without changing them | Optional/manual only |
| S3 Write-generating workflow | Upload/generate/regenerate/OCR/crop/study attempt/progress mutations | No |
| S4 Packaging/distribution | Build/ZIP/package/share/release/upload | No |

## Application smoke map

| Smoke ID | Area | Entry point / route / action | Level | Expected result | v0.7.9 execution policy |
|---|---|---|---:|---|---|
| SM-001 | Health | `/health` | S1 | Returns healthy response if server is already running | Optional GET-only; do not start server automatically |
| SM-002 | Home/library | `/` | S1 | Existing homepage/library shell loads | Optional GET-only; no actions |
| SM-003 | Quick tools | `/quick-tools` | S1 | Existing quick tools page loads | Optional GET-only; no actions |
| SM-004 | Upload PDF | Existing upload UI | S3 | PDF can be selected/uploaded in normal app workflow | Document only; do not automate |
| SM-005 | Generate course | Existing Generate action | S3 | Course artifacts generated in normal app workflow | Document only; do not run |
| SM-006 | Regenerate course | Existing Regenerate/Regenerează action | S3 | Existing course artifacts refreshed in normal app workflow | Document only; do not run |
| SM-007 | Course view | Existing Open course action | S1/S2 | Existing course page opens for existing course | Optional GET-only if URL is known and data already exists |
| SM-008 | Glossary | Existing glossary surface | S1/S2 | Existing glossary loads | Optional GET-only/read-only only |
| SM-009 | Quiz | Existing quiz surface | S1/S2 | Existing quiz loads | Optional GET-only/read-only only; no answer submission |
| SM-010 | Flashcards | Existing flashcards surface | S1/S2 | Existing flashcards load | Optional GET-only/read-only only |
| SM-011 | Figures gallery | Existing figures/gallery surface | S1/S2 | Existing figures display | Optional GET-only/read-only only |
| SM-012 | OCR review | Existing OCR review surface | S1/S2/S3 | Review UI loads; mutation controls remain manual | GET/manual only; no correction save automation |
| SM-013 | Crop editor | Existing crop editor surface | S3 | Crop editor workflow remains available | Document only; do not automate crop saves |
| SM-014 | Study mode | Existing Study surface | S1/S3 | Study page loads; attempts may write | GET/manual only; no answer submission automation |
| SM-015 | Progress dashboard | Existing Progress surface | S1/S2 | Progress page displays existing data | Optional GET-only/read-only only |
| SM-016 | Exam Prep dashboard | `/exam-prep` | S1 | Existing Exam Prep entry/dashboard loads | Optional GET-only; no session start/answer submission automation |
| SM-017 | Owner OCR Math report viewer | `/owner/ocr-math-report/{course_id}/view` | S1/S2 | Existing report renders if already present | Optional GET-only when server/data already exists |
| SM-018 | Owner OCR Math raw Markdown | Existing raw Markdown link | S2 | Existing Markdown report can be opened/read | Manual/read-only only |

## Static validation smoke map

| Smoke ID | Static check | Expected result |
|---|---|---|
| ST-001 | v0.7.9 docs exist | All required docs are present |
| ST-002 | v0.7.9 policy phrases exist | Required no-build/no-distribution policy is explicit |
| ST-003 | v0.7.9 sections exist | Inventory, smoke map, checklist, and policy sections are present |
| ST-004 | No packaging commands in v0.7.9 docs/scripts | No build/package/release/upload command is introduced |
| ST-005 | Optional source route text scan | Route decorators can be listed without executing app code |

## Manual smoke execution guardrails for later milestones

A later manual smoke evidence milestone may use this map, but it must remain separate from v0.7.9.

Before any later write-generating smoke test, the operator should explicitly decide:

- which local fixture course is safe to use
- whether generated artifacts may be created or overwritten
- whether a backup/snapshot is required
- which actions are strictly read-only and which are mutating

v0.7.9 does not make those decisions and does not run those workflows.