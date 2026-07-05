# Voila Functional Test Checklist v0.7.9

Milestone: `v0.7.9-owner-local-functional-audit-baseline-no-build-no-distribution`

## Policy

This checklist is a planning artifact only.

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

## Checklist use

Use this checklist to record what should be tested manually later. Do not treat the checklist as permission to execute write-generating workflows during v0.7.9.

## Checklist table

| ID | Feature | Existing route / entry point | Manual smoke action | Expected visible result | Risk level | Writes data? | Safe to automate now? | Notes |
|---|---|---|---|---|---|---:|---:|---|
| TC-001 | Health | `/health` | Open route if server is already running | Health response is returned | Low | No | Yes, GET-only | Do not start server automatically in v0.7.9 |
| TC-002 | Home / Library | `/` | Open homepage/library | Existing library shell and course cards display | Low | No for GET | Yes, GET-only | Do not click mutating actions |
| TC-003 | Quick tools | `/quick-tools` | Open quick tools page | Existing page loads | Low | No for GET | Yes, GET-only | Read-only route smoke |
| TC-004 | Upload PDF | Existing upload form | Select a non-confidential PDF in a later manual run | Upload starts normal workflow | High | Yes | No | Document only in v0.7.9 |
| TC-005 | Generate course | Existing Generate action | Click Generate in a later manual run | Course artifacts are created | High | Yes | No | Forbidden to automate in v0.7.9 |
| TC-006 | Regenerate course | Existing Regenerate/Regenerează action | Click Regenerate in a later manual run | Existing artifacts are refreshed | High | Yes | No | Forbidden to automate in v0.7.9 |
| TC-007 | Course view | Existing Open course link | Open an already generated course | Course content displays | Medium | No for GET | Conditional | Only if existing URL/data is known |
| TC-008 | Glossary | Existing glossary link/surface | Open existing glossary | Terms display | Medium | No for GET | Conditional | Only with existing artifacts |
| TC-009 | Quiz | Existing quiz link/surface | Open quiz without submitting answers | Quiz displays | Medium | No for GET; answer submit may write | Conditional | No answer submission automation |
| TC-010 | Flashcards | Existing flashcards link/surface | Open flashcards without progress mutation | Flashcards display | Medium | Usually no for GET | Conditional | Avoid recording progress/actions |
| TC-011 | Figures gallery | Existing figures/gallery link | Open gallery for existing course | Figures display | Medium | No for GET | Conditional | Existing data only |
| TC-012 | OCR review | Existing OCR review link | Open review UI | OCR review surface displays | Medium/High | Mixed | No for mutating actions | No correction save automation |
| TC-013 | Crop editor | Existing crop editor link | Open editor in a later manual smoke | Crop UI displays | High | May write | No | Document only in v0.7.9 |
| TC-014 | Study mode | Existing Study link | Open Study without submitting answers | Study screen displays | High | May write attempts/progress | No | No answer/action automation |
| TC-015 | Progress dashboard | Existing Progress link | Open progress page for existing data | Progress display loads | Medium | No for GET | Conditional | Read-only display only |
| TC-016 | Exam Prep dashboard | `/exam-prep` | Open dashboard/entry page | Existing dashboard displays | Medium | No for GET | Yes, GET-only | No session/action automation |
| TC-017 | Exam Prep session flow | Existing session actions | Start/answer in later manual smoke only | Session behavior remains current | High | Yes | No | Not allowed in v0.7.9 |
| TC-018 | Owner OCR Math report hook | `VOILA_ENABLE_OCR_MATH_REPORT_HOOK` | Inspect docs/source as text | Flag/path is documented | Low | No | Yes, static only | Do not enable or run generation |
| TC-019 | Owner OCR Math report JSON | `ocr_math_report.json` | Read existing file only | JSON report exists/loads if already generated | Medium | No if existing | Conditional | Do not create report |
| TC-020 | Owner OCR Math report Markdown | `ocr_math_report.md` | Read existing file only | Markdown report exists/loads if already generated | Medium | No if existing | Conditional | Do not create report |
| TC-021 | Owner OCR Math viewer | `/owner/ocr-math-report/{course_id}/view` | Open existing viewer URL only | Report renders if existing report exists | Medium | No for GET | Conditional | Existing data only |
| TC-022 | Owner OCR Math raw Markdown link | Existing viewer link | Open raw Markdown for existing report | Raw report opens | Medium | No | Conditional | Existing data only |
| TC-023 | Static route inventory | Source text scan | Scan route decorators as plain text | Route list is printed | Low | No | Yes | Do not import app |
| TC-024 | Static docs policy validation | v0.7.9 docs/scripts | Run validation script | PASS | Low | No | Yes | No build/package/release commands |

## Required result statuses

When this checklist is later used for manual evidence, each item should be marked with one of:

- PASS
- PASS_WITH_NOTE
- BLOCKED_BY_POLICY
- NOT_RUN
- NEEDS_SEPARATE_MILESTONE

For v0.7.9, write-generating items should remain `NOT_RUN` or `NEEDS_SEPARATE_MILESTONE`.

## Non-destructive execution rules

Allowed now:

- read documentation
- read source as text
- read existing local artifacts
- GET-only route checks against an already running server

Not allowed now:

- upload PDF
- Generate/Regenerează
- OCR report generation
- OCR correction save
- crop save
- quiz/study answer submission
- progress mutation
- Exam Prep session mutation
- package/build/release/upload/share/distribution