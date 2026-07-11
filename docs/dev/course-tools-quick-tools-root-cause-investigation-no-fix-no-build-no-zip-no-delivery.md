# v0.7.55 Course Tools / Quick Tools root-cause investigation

Status: COMPLETED / ROOT-CAUSE INVESTIGATION ONLY / NO FIX

Marker:
VOILA_V0_7_55_COURSE_TOOLS_QUICK_TOOLS_ROOT_CAUSE_INVESTIGATION_NO_FIX_CHECK=PASS

Evidence root:
D:\dev\tester-runs\voila-v0.7.55-course-tools-quick-tools-root-cause-investigation-no-fix-no-build-no-zip-no-delivery

Evidence files:
- V0.7.55-SOURCE-HITS.json
- V0.7.55-QUICK-TOOLS.html
- V0.7.55-QUICK-TOOLS-SCRIPT-BOUNDARY-AROUND-MARKER.txt
- V0.7.55-COURSE-TOOLS-TIMEOUT-DETAIL.json
- V0.7.55-DIRECT-V2-ROUTE-CALL-RESULTS.json
- V0.7.55-DIRECT-V2-course_tools-TRACE.txt
- V0.7.55-WEBAPP-ocr-math-report-paths-130-190.txt
- V0.7.55-WEBAPP-ocr-math-candidate-roots-90-142.txt
- V0.7.55-OCR-MATH-CANDIDATE-ROOTS-INVENTORY.json
- V0.7.55-CURRENT-PDF-OCR-MATH-FILES.json
- V0.7.55-EXISTING-OCR-MATH-REPORTS-UNDER-DATA.json

## Scope

This milestone investigates the v0.7.54 tester-readiness blockers.

It does not fix behavior.

## Confirmed Course Tools root cause

`/course-tools?pdf=03-pag-30-34-vectori-trigonometrie.pdf` does not respond within 60 seconds.

Direct route tracing shows:

- `quick_tools()` returns normally
- `course_tools()` does not return and is terminated by timeout

The faulthandler trace shows that `course_tools()` is blocked in:

- `services/api/web_app.py`
- `course_tools()`
- `_voila_ocr_math_report_paths(pdf_path.stem)`
- `root.rglob("ocr_math_report.md")`

The blocking code is used to determine OCR Math report availability for the Course Tools card.

## Confirmed excessive OCR Math search scope

`_voila_ocr_math_report_candidate_roots()` builds many candidate roots from `Path.cwd()` and parents of `web_app.py`.

The inventory includes roots above the repo, including:

- `D:\dev\projects`
- `D:\dev`
- `D:\`

For the tested PDF, the direct active output path does not contain:

- `data\output\03-pag-30-34-vectori-trigonometrie\ocr_math_report.md`
- `data\output\03-pag-30-34-vectori-trigonometrie\ocr_math_report.json`

Existing OCR Math reports found under `data` are in `data\trash\courses\...`, not in the active output folder for the tested PDF.

## Quick Tools finding

`quick_tools()` returns normally in a direct route call.

The bottom navigation marker is inside a `<script id="voila-tester-flow-bottom-nav-v0724">` block in the captured `/quick-tools` HTML.

Therefore, the Course Tools blocker is not caused by the Quick Tools route itself.

The v0.7.54 visual observation of raw JavaScript on `/quick-tools` remains recorded, but the strongest confirmed root cause for tester blocking is the Course Tools OCR Math report lookup hang.

## Root-cause summary

The Course Tools route blocks because OCR Math report availability lookup can fall back to an unbounded recursive search across overly broad candidate roots.

Missing OCR Math reports should not cause a full repository / parent-drive recursive search in tester-facing navigation.

## Recommended next fix milestone

Use a separate fix milestone.

Recommended fix direction:

- make OCR Math report lookup bounded
- prefer direct active output folder lookup for `data/output/<course_id>`
- avoid recursive search above the repo root
- avoid scanning `data/trash`
- make missing OCR Math report return quickly as unavailable
- retest `/course-tools`, `/owner/ocr-math-report/<course_id>/view`, `/quick-tools`, and generated course navigation

## Tester decision

DO NOT package for testers.
DO NOT create ZIP.
DO NOT share.
DO NOT deliver.

## Explicitly unchanged

No product fix.
No import click.
No import logic change.
No OCR text rewrite.
No Course rewrite.
No Study rewrite.
No Progress rewrite.
No build.
No ZIP.
No share.
No delivery.
No distribution.
