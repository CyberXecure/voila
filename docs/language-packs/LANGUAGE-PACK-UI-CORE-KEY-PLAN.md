# Voila! UI Core Key Plan

Milestone: v0.2.46-public-beta-language-pack-ui-core-key-plan
Status: planning
Scope: documentation only; no core JSON changes, no runtime changes, no UI code changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the exact follow-up for adding the proposed `ui.*` keys to the core Romanian and English language packs.

It does not modify the JSON files yet.

## Baseline

Previous milestones established:

- v0.2.43: Romanian default, English fallback, adaptive/browser-locale later
- v0.2.44: visible UI label inventory
- v0.2.45: proposed `ui.*` key map and placement in `messages`

## Target files for later implementation

Future implementation should modify only:

```text
language-packs/core/ro.language-pack.json
language-packs/core/en.language-pack.json
```

No UI JavaScript should be changed in the first core-key implementation milestone.

## Target section

The keys should be added to the existing:

```text
messages
```

section.

## Proposed Romanian additions

Add these keys to `language-packs/core/ro.language-pack.json` under `messages`:

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

## Proposed English additions

Add these keys to `language-packs/core/en.language-pack.json` under `messages`:

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

## Required tests for later implementation

When the core JSON files are modified, add or update tests to prove:

- Romanian lookup for `ui.upload_pdf` returns `ÃŽncarcÄƒ PDF`
- English lookup for `ui.upload_pdf` returns `Upload PDF`
- Romanian lookup for `ui.delete_from_library` returns `È˜terge din bibliotecÄƒ`
- English lookup for `ui.delete_from_library` returns `Delete from library`
- unsupported language falls back to English
- missing key behavior remains unchanged

## Recommended test files to update later

Likely target files:

```text
scripts/language-packs/test_language_pack_runtime.py
scripts/language-packs/test_minimal_language_runtime.py
scripts/language-packs/smoke-core-runtime-helper.py
```

## Required validation after later implementation

After adding keys to core JSON, run:

```powershell
python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python .\scripts\language-packs\smoke-language-pack-files.py
python -m py_compile .\services\api\i18n.py
```

Also run packaging inspection:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1
```

## Implementation order for later milestones

Recommended next implementation sequence:

1. Add `ui.*` keys to Romanian core pack.
2. Add matching `ui.*` keys to English core pack.
3. Run language-pack validator.
4. Add runtime lookup tests.
5. Run runtime tests.
6. Add a smoke assertion for at least one UI key.
7. Do not change UI JavaScript yet.
8. Commit as a narrow core-language-pack change.

## Non-goals

This milestone does not:

- edit `language-packs/core/ro.language-pack.json`
- edit `language-packs/core/en.language-pack.json`
- edit `language-packs/schema/language-pack.schema.json`
- edit runtime code
- edit UI JavaScript
- add a language selector
- add browser-locale detection
- publish a release artifact
- create a Git tag
- upload anything to GitHub Releases
- modify LICENSE files

## Recommended next milestone

```text
v0.2.47-public-beta-language-pack-ui-core-keys
```

Suggested next work:

- add the `ui.*` keys to Romanian and English core packs
- add minimal runtime tests
- keep UI JavaScript unchanged
- keep the change small and reversible

## Decision

v0.2.46 is documentation only.

It plans the safe core language-pack key implementation before any JSON/runtime/UI changes are made.
