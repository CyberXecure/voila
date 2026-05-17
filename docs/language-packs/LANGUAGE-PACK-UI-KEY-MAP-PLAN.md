# Voila! UI Key Map Plan

Milestone: v0.2.45-public-beta-language-pack-ui-key-map-plan
Status: planning
Scope: documentation only; no runtime changes, no UI code changes, no language-pack JSON changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone defines the proposed mapping for visible UI labels into language-pack keys.

It uses the v0.2.44 UI label inventory and prepares the next implementation step without changing runtime or UI code yet.

## Policy baseline

From v0.2.43:

```text
Default UI language: Romanian
Fallback language: English
Adaptive/browser-locale behavior: planned later
```

## Inventory baseline

From v0.2.44, the visible mixed UI labels are mapped to proposed `ui.*` keys.

## Proposed key placement

Recommended initial placement:

```text
language-packs/core/ro.language-pack.json
language-packs/core/en.language-pack.json
```

Recommended section:

```text
messages
```

Recommended key format:

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

## Why use `messages`

The current language-pack runtime already supports message-style lookup and placeholder handling.

Using `messages` with flat `ui.*` keys avoids introducing a new top-level schema section before the validator, schema, and runtime are updated intentionally.

## Proposed Romanian values

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

## Proposed English fallback values

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

## Implementation strategy for later milestones

### Phase 1: add keys to core packs

Add the proposed keys to:

- `language-packs/core/ro.language-pack.json`
- `language-packs/core/en.language-pack.json`

Do not change UI code yet.

### Phase 2: validate packs

Run:

```powershell
python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
```

### Phase 3: add runtime lookup tests

Add tests proving that:

- Romanian `ui.upload_pdf` returns `ÃŽncarcÄƒ PDF`
- English `ui.upload_pdf` returns `Upload PDF`
- unsupported language falls back to English
- missing key behavior remains unchanged

### Phase 4: minimal UI integration

Replace only a small number of high-priority hardcoded labels first:

- Upload PDF
- Choose File
- Generate course
- Deschide cursul
- Delete from library

### Phase 5: UI smoke validation

Add or extend smoke tests so the UI endpoint/runtime path can return the new `ui.*` keys.

### Phase 6: broader UI cleanup

After the minimal integration is stable, continue with:

- Figures
- Edit crops
- Study
- Review weak
- Progress
- Logs
- Generated
- Source Mode

## Priority order

High priority:

- `ui.upload_pdf`
- `ui.choose_file`
- `ui.generate_course`
- `ui.open_course`
- `ui.delete_from_library`

Medium priority:

- `ui.figures`
- `ui.edit_crops`
- `ui.study`
- `ui.review_weak`
- `ui.progress`
- `ui.generated`
- `ui.source_mode`

Low priority:

- `ui.logs`

## Safety rules

This milestone must not:

- modify `language-packs/core/*.json`
- modify runtime code
- modify UI JavaScript
- modify schema
- create a language selector
- add browser-locale detection
- upload GitHub release assets
- create a Git tag
- publish a ZIP
- modify LICENSE files

## Recommended next milestone

```text
v0.2.46-public-beta-language-pack-ui-core-key-plan
```

Suggested next work:

- plan the exact core JSON edit
- confirm whether `messages` remains the correct section
- prepare tests before modifying UI code
- keep the change narrow and reversible

## Decision

v0.2.45 is documentation only.

It defines the proposed `ui.*` key map and recommends adding those keys to the existing `messages` section in the Romanian and English core language packs in a later milestone.
