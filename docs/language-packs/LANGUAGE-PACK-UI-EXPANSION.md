# Voila! UI Expansion

Milestone: v0.2.54-public-beta-language-pack-ui-expansion-docs
Status: documentation
Scope: documentation only; no UI code changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the second small UI language-pack integration batch completed in v0.2.53.

The integration continued the controlled UI language-pack rollout after the successful minimal UI integration in v0.2.50.

## Implemented in v0.2.53

Updated file:

```text
services/api/web_app.py
```

Added smoke helper:

```text
scripts/language-packs/smoke-ui-expansion-key-integration.py
```

## Integrated keys

The second UI expansion batch uses:

```text
ui.figures
ui.study
ui.progress
ui.delete_from_library
```

## UI behavior

The following UI labels are now language-pack-backed:

- Figures links/cards
- Study links in selected safe locations
- Progress links/cards
- Delete from library injected button

## Fallback behavior

The implementation preserves existing fallback behavior:

```text
ui.study -> fallback to existing study key -> fallback to "Study"
ui.progress -> fallback to existing progress key -> fallback to "Progress"
ui.figures -> fallback to "Figures"
ui.delete_from_library -> fallback to "Delete from library"
```

## Validation coverage

The new smoke helper verifies that:

- `ui.figures` is used in `web_app.py`
- `ui.study` is used with existing `study` fallback
- `ui.progress` is used with existing `progress` fallback
- `ui.delete_from_library` is used for the injected library delete button
- selected old hardcoded snippets are no longer present where intentionally replaced

## Validation commands

The v0.2.53 implementation passed:

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
python .\scripts\language-packs\smoke-minimal-ui-key-integration.py
python .\scripts\language-packs\smoke-ui-expansion-key-integration.py

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\smoke-ui-expansion-key-integration.py
```

## What was intentionally not changed

v0.2.53 did not add:

- broad UI rewrite
- full UI localization
- language selector
- browser-locale detection
- persisted language preference
- adaptive UI switching
- schema changes
- release asset changes

## Remaining UI work

The UI is still not fully localized.

Remaining future candidates include:

```text
ui.edit_crops
ui.review_weak
ui.generated
ui.source_mode
ui.choose_file
```

`ui.choose_file` was not integrated in v0.2.53 because no simple hardcoded `Choose File` label was found in the inspected UI path.

## Recommended next milestone

```text
v0.2.55-public-beta-language-pack-ui-next-batch-plan
```

Suggested next work:

- inspect remaining visible hardcoded labels
- decide whether `ui.edit_crops`, `ui.review_weak`, `ui.generated`, and `ui.source_mode` are safe for a third small batch
- keep changes narrow and smoke-tested
- avoid full UI localization until the small-batch path is stable

## Safety

This milestone does not:

- modify UI code
- modify runtime behavior
- modify schema
- upload GitHub release assets
- create a Git tag
- publish a ZIP
- modify LICENSE files

## Decision

v0.2.54 documents the v0.2.53 UI expansion implementation.

The language-pack UI integration path now has two controlled implementation batches with focused smoke coverage.
