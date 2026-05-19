# Voila! UI Remaining Labels Inventory

Milestone: v0.2.59-public-beta-language-pack-ui-remaining-labels-inventory
Status: inventory
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone creates a precise inventory of remaining visible UI labels after the controlled UI language-pack batches from v0.2.50, v0.2.53, and v0.2.56.

The purpose is to decide what can safely reuse existing keys, what needs new keys, and what should remain untouched.

## Baseline

Completed UI language-pack batches:

- v0.2.50: `ui.upload_pdf`, `ui.generate_course`, `ui.open_course`
- v0.2.53: `ui.figures`, `ui.study`, `ui.progress`, `ui.delete_from_library`
- v0.2.56: `ui.edit_crops`, `ui.review_weak`, `ui.generated`, `ui.source_mode`, extra `ui.progress` fallback
- v0.2.58: remaining-label classification plan

## Scan method

The inventory is based on a precise scan of `services/api/web_app.py` for UI surfaces:

```text
<a
<button
<h1
<h2
<title>
class="notice"
class="meta"
card(
```

This avoids broad false positives such as matching `Back` inside CSS `background`.

## Inventory summary

### Already language-pack-backed

These labels already use `ui.*` or existing translation fallback keys.

| Label | Current handling | Status |
|---|---|---|
| Upload PDF | `ui.upload_pdf` | done |
| Generate course | `ui.generate_course` | done |
| Open course | `ui.open_course` with `open_course` fallback | done |
| Figures | `ui.figures` | done |
| Study | `ui.study` with `study` fallback in selected places | partly done |
| Progress | `ui.progress` with `progress` fallback in selected places | partly done |
| Edit crops | `ui.edit_crops` | done |
| Review weak | `ui.review_weak` | done |
| Generated | `ui.generated` | done |
| Source Mode | `ui.source_mode` | done |
| Library | existing `library` fallback in selected places | partly done |
| Back | existing `back` fallback in selected places | partly done |
| Lessons | existing `lessons` fallback in selected places | partly done |

## Remaining short UI labels

These are short visible labels and are good candidates for future `ui.*` or existing-key alignment.

| Label | Example area | Recommended action |
|---|---|---|
| Logs | home PDF action button | add `ui.logs` or reuse exact existing key if added |
| Course Tools | course tools links/buttons/title | add `ui.course_tools` |
| Quick Tools | quick tools page/title | add `ui.quick_tools` |
| Tools | course tools bar | add `ui.tools` |
| Course | tools bar / quick tools | add `ui.course` |
| Lessons | tools/cards/lesson links | consider `ui.lessons` or keep existing `lessons` |
| Study mode | card/title | add `ui.study_mode` |
| Review OCR Text | nav/card/page title | add `ui.review_ocr_text` |
| Review Concepts | nav/link | add `ui.review_concepts` |
| Review Study Concepts | card/page title | add `ui.review_study_concepts` |
| Correct OCR Text | page heading | add `ui.correct_ocr_text` |
| Top / Bottom | fixed navigation buttons | existing `top` / `bottom` fallback exists |
| Continue Study | progress action | add `ui.continue_study` |
| Toggle theme | theme button | add `ui.toggle_theme` |
| Open lesson | lesson list button | existing `open_lesson` fallback exists |
| Study lesson | lesson list button | existing `study_lesson` fallback exists |
| Read lesson | lesson study link | existing `read_lesson` fallback exists |
| General study | lesson study link | existing `general_study` fallback exists |

## Remaining button labels

| Label | Area | Recommended action |
|---|---|---|
| Save title override | review concepts | new key needed |
| Save page correction | OCR review | new key needed |
| Save reviewed page | OCR review | new key needed |
| Save as needs review | OCR review | new key needed |
| Apply corrected OCR to pages.json | OCR review | new key needed; long/destructive action |
| 100% | zoom control | leave unchanged |
| Fit width | zoom control | new key optional |
| + / - | zoom control | leave unchanged |

## Remaining headings

| Heading | Recommended action |
|---|---|
| Voila! Review | new heading key optional |
| Voila! Review weak concepts | can align with `ui.review_weak` later, but not exact |
| Voila! Progress | existing progress fallback may be enough |
| Voila! Progress Dashboard | new key needed |
| Study Mode | new `ui.study_mode` key |
| Review Study Concepts | new `ui.review_study_concepts` key |
| Review OCR Text | new `ui.review_ocr_text` key |
| Correct OCR Text | new `ui.correct_ocr_text` key |
| Course Tools | new `ui.course_tools` key |
| Quick Tools | new `ui.quick_tools` key |
| Missing PDF name | error/status text; not short UI label |
| No OCR pages found | error/status text |
| Save title override failed | error/status text |
| Save OCR text failed | error/status text |
| Rebuild complete | status text |
| Rebuild failed | status text |

## Remaining helper and description text

These are not good candidates for short `ui.*` labels. They need message/helper keys.

| Text | Recommended future key group |
|---|---|
| Choose a PDF from your computer. It will be saved locally in data/input. | `message.choose_pdf_helper` |
| No PDF files found. Put a PDF in data/input, then refresh this page. | `message.no_pdf_files_found` |
| Read the generated course with navigation. | `message.open_course_description` |
| Choose a lesson, read it, then study only that lesson. | `message.lessons_description` |
| Practice questions generated from the course. | `message.study_mode_description` |
| Correct OCR text page by page. | `message.review_ocr_text_description` |
| Correct lesson and concept titles. | `message.review_concepts_description` |
| Manually edit figure crops. | `message.edit_crops_description` |
| View study progress. | `message.progress_description` |
| Return to the main course library. | `message.return_to_library_description` |

## Remaining status/meta text

These should become `status.*` or `message.*` keys, not short `ui.*` labels.

| Text | Recommended key |
|---|---|
| Uploaded | `status.uploaded` |
| Not generated yet | `status.not_generated_yet` |
| No suspicious pages detected. | `status.no_suspicious_pages_detected` |
| Focused concept | `status.focused_concept` |
| Attempts | `status.attempts` |
| Status | `status.status` |
| Study coverage | existing `study_coverage` or future `status.study_coverage` |
| Overall mastery | `status.overall_mastery` |
| Concept status | `status.concept_status` |

## Keep untouched for now

These should not be part of UI label batches:

- generated course/document content
- OCR output text
- logs
- traceback/debug output
- CSS
- JavaScript diagnostics
- internal command names
- scanner false positives

## Recommended next milestone

```text
v0.2.60-public-beta-language-pack-ui-remaining-key-plan
```

Suggested work:

- plan the exact new keys needed
- separate `ui.*`, `message.*`, and `status.*`
- update core language-pack JSON only after the key plan is reviewed
- keep runtime/UI unchanged until keys exist and tests are ready

## Non-goals

This milestone does not:

- modify UI code
- modify language-pack JSON
- modify runtime behavior
- modify schema
- add a language selector
- add browser-locale detection
- add persisted language preference
- upload GitHub release assets
- create a Git tag
- publish a ZIP
- modify LICENSE files

## Decision

v0.2.59 is documentation only.

It creates the remaining-label inventory needed before adding new UI/message/status keys.
