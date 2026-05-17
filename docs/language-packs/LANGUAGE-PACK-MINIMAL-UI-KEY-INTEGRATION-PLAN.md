# Voila! Minimal UI Key Integration Plan

Milestone: v0.2.49-public-beta-language-pack-minimal-ui-key-integration-plan
Status: planning
Scope: documentation only; no UI JavaScript changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans a minimal and safe UI integration path for the `ui.*` language-pack keys added in v0.2.47.

The goal is not to localize the entire UI at once.

The goal is to prove that a few visible labels can be served from core language-pack keys without destabilizing the existing UI.

## Baseline

Previous milestones established:

- v0.2.43: Romanian default, English fallback, adaptive/browser-locale later
- v0.2.44: visible UI label inventory
- v0.2.45: `ui.*` key map plan
- v0.2.46: core key implementation plan
- v0.2.47: real `ui.*` keys added to Romanian and English core packs
- v0.2.48: documentation for implemented UI core keys

## Existing implemented keys

The following keys already exist under `messages` in both Romanian and English core packs:

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

## Minimal UI integration target

Recommended first UI labels:

```text
ui.upload_pdf
ui.generate_course
ui.open_course
```

Optional fourth label, only if the change remains simple:

```text
ui.delete_from_library
```

## Why these labels first

These labels are good first candidates because:

- they are user-facing
- they are visible in the current UI
- they are high-value labels
- they have straightforward Romanian and English values
- they do not require UI layout redesign
- they do not require schema changes
- they can be tested visually and with a small smoke check

## Non-goals

The next implementation milestone should not:

- rewrite the whole UI
- add a language selector
- add browser-locale detection
- add persisted language preference
- change adaptive language behavior
- refactor the full frontend
- modify schema
- modify release packaging
- upload release assets
- create a Git tag

## Recommended integration strategy

### Phase 1: locate UI label source

Find where the visible labels are currently hardcoded.

Likely candidates:

```text
services/api/static/
services/api/templates/
services/api/
```

Focus only on labels corresponding to:

```text
Upload PDF
Generate course
Deschide cursul / Open course
```

### Phase 2: expose existing language-pack values safely

Use the existing language-pack runtime/helper path if already exposed.

If a UI endpoint already returns language data, extend minimally.

Do not introduce a new broad i18n framework in this milestone.

### Phase 3: replace only 2-3 labels

Replace only the selected labels with language-pack-backed values.

Recommended first pass:

```text
Upload PDF -> ui.upload_pdf
Generate course -> ui.generate_course
Deschide cursul / Open course -> ui.open_course
```

### Phase 4: preserve fallback behavior

Required fallback behavior:

- Romanian key exists: use Romanian value
- English key exists: use English fallback
- unsupported language: fallback to English
- missing key: safe fallback to current hardcoded label

### Phase 5: add focused smoke validation

Add a smoke check that confirms the language-pack-backed labels are reachable.

The smoke should be narrow and stable.

Suggested checks:

- `ui.upload_pdf` returns `Încarcă PDF` for Romanian
- `ui.upload_pdf` returns `Upload PDF` for English
- unsupported language returns English fallback

### Phase 6: manual UI check

After implementation, manually verify:

- app opens
- upload section still works
- visible label changed correctly
- course generation button still works
- no broken navigation
- no layout break

## Recommended files to inspect before implementation

```text
services/api/i18n.py
services/api/static/
services/api/templates/
scripts/language-packs/smoke-ui-language-endpoint.py
scripts/language-packs/smoke-ui-core-keys.py
```

## Validation required after implementation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\test_ui_core_keys.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python .\scripts\language-packs\smoke-language-pack-files.py
python .\scripts\language-packs\smoke-ui-core-keys.py
python -m py_compile .\services\api\i18n.py
```

If a new UI smoke helper is added, run it too.

## Safety rules

The next implementation milestone must keep the change narrow:

- maximum 2-3 UI labels in first integration
- no broad UI refactor
- no language selector
- no browser-locale detection
- no schema change
- no release asset upload
- no Git tag
- no LICENSE change

## Recommended next milestone

```text
v0.2.50-public-beta-language-pack-minimal-ui-key-integration
```

Suggested next work:

- inspect current UI label locations
- integrate `ui.upload_pdf`, `ui.generate_course`, and `ui.open_course`
- add narrow smoke validation
- keep fallback behavior safe

## Decision

v0.2.49 is documentation only.

It prepares a safe minimal UI integration plan for existing `ui.*` core keys.
