# Voila! UI Core Keys

Milestone: v0.2.48-public-beta-language-pack-ui-core-key-docs
Status: documentation
Scope: documentation only; no UI JavaScript changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the real `ui.*` core language-pack keys added in v0.2.47.

The implementation added user-facing UI translation keys to the Romanian and English core language packs, without changing UI JavaScript or runtime behavior.

## Implemented files

Core language packs updated in v0.2.47:

```text
language-packs/core/ro.language-pack.json
language-packs/core/en.language-pack.json
```

Validation/test files added in v0.2.47:

```text
scripts/language-packs/test_ui_core_keys.py
scripts/language-packs/smoke-ui-core-keys.py
```

## Key placement

The `ui.*` keys are stored under the existing `messages` section. No new schema section was introduced.

## Implemented keys

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

## Romanian values

```json
{
  "ui.upload_pdf": "ÃŽncarcÄƒ PDF",
  "ui.choose_file": "Alege fiÈ™ier",
  "ui.generated": "Generat",
  "ui.source_mode": "Mod sursÄƒ",
  "ui.generate_course": "GenereazÄƒ curs",
  "ui.open_course": "Deschide cursul",
  "ui.figures": "Figuri",
  "ui.edit_crops": "EditeazÄƒ decupaje",
  "ui.study": "StudiazÄƒ",
  "ui.review_weak": "RepetÄƒ punctele slabe",
  "ui.progress": "Progres",
  "ui.logs": "Jurnale",
  "ui.delete_from_library": "È˜terge din bibliotecÄƒ"
}
```

## English fallback values

```json
{
  "ui.upload_pdf": "Upload PDF",
  "ui.choose_file": "Choose File",
  "ui.generated": "Generated",
  "ui.source_mode": "Source Mode",
  "ui.generate_course": "Generate course",
  "ui.open_course": "Open course",
  "ui.figures": "Figures",
  "ui.edit_crops": "Edit crops",
  "ui.study": "Study",
  "ui.review_weak": "Review weak",
  "ui.progress": "Progress",
  "ui.logs": "Logs",
  "ui.delete_from_library": "Delete from library"
}
```

## Validation coverage

The new tests verify Romanian and English `ui.*` keys, matching key sets, unsupported-language English fallback, and safe missing-key behavior.

The smoke helper verifies representative keys:

- Romanian and English `ui.upload_pdf`
- Romanian and English `ui.delete_from_library`

## Current limitation

The keys now exist in core language packs, but the UI JavaScript still contains hardcoded labels.

This means the UI may still display mixed English/Romanian until the next UI integration milestone.

## Recommended next milestone

```text
v0.2.49-public-beta-language-pack-minimal-ui-key-integration-plan
```

Suggested next work:

- plan minimal UI usage of the existing `ui.*` keys
- start with 2-3 safe labels only
- avoid broad UI rewrite
- keep runtime behavior stable
- add a focused UI smoke check

## Safety

This milestone does not modify UI JavaScript, runtime behavior, schema, release assets, Git tags, public ZIPs, or LICENSE files.

## Decision

v0.2.48 documents the completed v0.2.47 core-key implementation.

The next implementation step should be a minimal UI integration plan, not a broad UI rewrite.
