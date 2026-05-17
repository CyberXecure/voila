# Voila! UI Label Inventory

Milestone: v0.2.44-public-beta-language-pack-ui-label-inventory
Status: planning / inventory
Scope: documentation only; no runtime changes, no UI code changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone inventories visible mixed-language UI labels observed after the v0.2.42 manual RC dry run and prepares proposed language-pack keys.

## Policy baseline

From v0.2.43:

```text
Default UI language: Romanian
Fallback language: English
Adaptive/browser-locale behavior: planned later
```

## Current known mixed UI state

The UI currently contains both English and Romanian labels. This is documented as a follow-up issue, not as a blocker for the language-pack packaging RC.

## Label inventory

| Area | Current visible label | Current language | Proposed key | Romanian default | English fallback | Priority | Notes |
|---|---|---:|---|---|---|---:|---|
| Upload | Upload PDF | EN | ui.upload_pdf | ÃŽncarcÄƒ PDF | Upload PDF | High | Main CTA / upload area |
| Upload | Choose File | EN | ui.choose_file | Alege fiÈ™ier | Choose File | High | Native/file action wording |
| Upload | Generated | EN | ui.generated | Generat | Generated | Medium | Status/section label |
| Upload | Source Mode | EN | ui.source_mode | Mod sursÄƒ | Source Mode | Medium | May need context check |
| Course generation | Generate course | EN | ui.generate_course | GenereazÄƒ curs | Generate course | High | Core user action |
| Course/library | Deschide cursul | RO | ui.open_course | Deschide cursul | Open course | High | Already Romanian |
| OCR/Figures | Figures | EN | ui.figures | Figuri | Figures | Medium | Could also mean imagini/figuri |
| OCR/Figures | Edit crops | EN | ui.edit_crops | EditeazÄƒ decupaje | Edit crops | Medium | OCR/image crop workflow |
| Study | Study | EN | ui.study | StudiazÄƒ | Study | Medium | Navigation/action |
| Study | Review weak | EN | ui.review_weak | RepetÄƒ punctele slabe | Review weak | Medium | Better Romanian may need UX pass |
| Progress | Progress | EN | ui.progress | Progres | Progress | Medium | Status/navigation |
| Logs | Logs | EN | ui.logs | Jurnale | Logs | Low | Could remain technical if debug-only |
| Library/actions | Delete from library | EN | ui.delete_from_library | È˜terge din bibliotecÄƒ | Delete from library | High | Destructive action |

## Key naming rules

Use stable, lowercase, dot-separated keys:

```text
ui.upload_pdf
ui.choose_file
ui.generated
ui.source_mode
ui.generate_course
ui.open_course
ui.figures
ui.edit_crops
ui.study
ui.review_weak
ui.progress
ui.logs
ui.delete_from_library
```

## Classification

User-facing labels to localize first:

- Upload PDF
- Choose File
- Generate course
- Deschide cursul
- Delete from library

Workflow/navigation labels to localize next:

- Study
- Review weak
- Progress
- Figures
- Edit crops

Technical/status labels can be reviewed later:

- Logs
- Source Mode
- Generated

## Non-goals

This milestone does not modify JavaScript, Python runtime behavior, selector behavior, browser-locale behavior, packaged ZIP assets, or release artifacts.

## Recommended next milestone

```text
v0.2.45-public-beta-language-pack-ui-key-map-plan
```

## Decision

v0.2.44 is documentation only.

It creates the first visible UI label inventory and proposed translation-key mapping.
