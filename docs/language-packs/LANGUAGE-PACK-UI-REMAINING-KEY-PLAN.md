# Voila! UI Remaining Key Plan

Milestone: v0.2.60-public-beta-language-pack-ui-remaining-key-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the exact remaining UI/message/status keys needed after the v0.2.59 remaining-label inventory.

The goal is to prepare a safe future language-pack JSON update without changing UI code yet.

## Baseline

This plan builds on:

- v0.2.50 minimal UI integration
- v0.2.53 UI expansion
- v0.2.56 UI next-batch integration
- v0.2.58 remaining-label classification plan
- v0.2.59 remaining-label inventory

## Key groups

The remaining keys should be split into three groups:

```text
ui.*       short visible labels
message.*  longer helper/description text
status.*   state, notice, and meta labels
```

## Proposed ui.* keys

### Navigation and top-level labels

```text
ui.back
ui.tools
ui.course
ui.lessons
ui.library
ui.logs
ui.course_tools
ui.quick_tools
```

### Study/review labels

```text
ui.study_mode
ui.review_ocr_text
ui.review_concepts
ui.review_study_concepts
ui.correct_ocr_text
ui.continue_study
```

### Buttons and actions

```text
ui.toggle_theme
ui.save_title_override
ui.save_page_correction
ui.save_reviewed_page
ui.save_as_needs_review
ui.apply_corrected_ocr
ui.fit_width
```

## Proposed message.* keys

These should be used for longer helper text and card descriptions.

```text
message.choose_pdf_helper
message.no_pdf_files_found
message.open_course_description
message.lessons_description
message.study_mode_description
message.review_ocr_text_description
message.review_concepts_description
message.edit_crops_description
message.figures_description
message.progress_description
message.return_to_library_description
message.source_mode_description
message.apply_corrected_ocr_warning
```

## Proposed status.* keys

These should be used for status/meta text.

```text
status.uploaded
status.not_generated_yet
status.no_suspicious_pages_detected
status.focused_concept
status.attempts
status.status
status.study_coverage
status.overall_mastery
status.concept_status
status.missing_pdf_name
status.no_ocr_pages_found
status.rebuild_complete
status.rebuild_failed
status.save_title_override_failed
status.save_ocr_text_failed
```

## Legacy keys to preserve

Do not remove existing legacy keys yet.

Examples:

```text
back
study
progress
review
reset
library
lessons
back_to_lessons
open_lesson
study_lesson
read_lesson
general_study
study_coverage
reset_study_progress
```

Future implementation should keep these as fallback where already used.

## Romanian default values

Suggested Romanian values for the new `ui.*` keys:

```text
ui.back = ÃŽnapoi
ui.tools = Instrumente
ui.course = Curs
ui.lessons = LecÈ›ii
ui.library = BibliotecÄƒ
ui.logs = Jurnale
ui.course_tools = Instrumente curs
ui.quick_tools = Instrumente rapide
ui.study_mode = Mod studiu
ui.review_ocr_text = Revizuire text OCR
ui.review_concepts = Revizuire concepte
ui.review_study_concepts = Revizuire concepte de studiu
ui.correct_ocr_text = Corectare text OCR
ui.continue_study = ContinuÄƒ studiul
ui.toggle_theme = SchimbÄƒ tema
ui.save_title_override = SalveazÄƒ titlul modificat
ui.save_page_correction = SalveazÄƒ corecÈ›ia paginii
ui.save_reviewed_page = SalveazÄƒ pagina revizuitÄƒ
ui.save_as_needs_review = SalveazÄƒ ca necesitÄƒ revizuire
ui.apply_corrected_ocr = AplicÄƒ OCR-ul corectat
ui.fit_width = PotriveÈ™te la lÄƒÈ›ime
```

## English fallback values

Suggested English values for the new `ui.*` keys:

```text
ui.back = Back
ui.tools = Tools
ui.course = Course
ui.lessons = Lessons
ui.library = Library
ui.logs = Logs
ui.course_tools = Course Tools
ui.quick_tools = Quick Tools
ui.study_mode = Study mode
ui.review_ocr_text = Review OCR Text
ui.review_concepts = Review Concepts
ui.review_study_concepts = Review Study Concepts
ui.correct_ocr_text = Correct OCR Text
ui.continue_study = Continue Study
ui.toggle_theme = Toggle theme
ui.save_title_override = Save title override
ui.save_page_correction = Save page correction
ui.save_reviewed_page = Save reviewed page
ui.save_as_needs_review = Save as needs review
ui.apply_corrected_ocr = Apply corrected OCR to pages.json
ui.fit_width = Fit width
```

## Message key policy

Long messages should not be stored as short `ui.*` keys.

Examples:

```text
Choose a PDF from your computer. It will be saved locally in data/input.
No PDF files found. Put a PDF in data/input, then refresh this page.
Read the generated course with navigation.
```

These should use `message.*`.

## Status key policy

State labels and meta labels should not be mixed with action labels.

Examples:

```text
Uploaded
Not generated yet
Focused concept
Attempts
Overall mastery
```

These should use `status.*`.

## Recommended implementation order

Future implementation should happen in small milestones:

```text
1. add remaining keys to core ro/en language packs
2. add key parity tests
3. add smoke test for new key presence
4. integrate a small UI subset
5. document the integration
```

## Recommended next milestone

```text
v0.2.61-public-beta-language-pack-ui-remaining-core-key-plan
```

Suggested next work:

- plan safe addition of these keys to core Romanian and English language packs
- keep UI code unchanged
- add tests only after key plan is reviewed

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

v0.2.60 is documentation only.

It defines the remaining key plan before any language-pack JSON or UI implementation changes.
