# Voila! Minimal UI Key Integration

Milestone: v0.2.51-public-beta-language-pack-minimal-ui-key-docs
Status: documentation
Scope: documentation only; no UI code changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the minimal UI key integration completed in v0.2.50.

The integration proved that a small number of visible UI labels can use existing language-pack `ui.*` keys without a broad UI rewrite.

## Implemented in v0.2.50

Updated file:

```text
services/api/web_app.py
```

Added smoke helper:

```text
scripts/language-packs/smoke-minimal-ui-key-integration.py
```

## Integrated keys

The first minimal UI integration uses:

```text
ui.upload_pdf
ui.generate_course
ui.open_course
```

## UI behavior

The following labels are now language-pack-backed:

- upload heading
- upload button
- generate course button
- open course link, with safe fallback to the previous `open_course` key

## Fallback behavior

`ui.open_course` uses the existing `open_course` key as fallback.

This keeps behavior safe if the new `ui.open_course` key is missing.

## Validation coverage

The new smoke helper verifies that:

- `ui.upload_pdf` is used in `web_app.py`
- `ui.generate_course` is used in `web_app.py`
- `ui.open_course` is used with safe fallback
- old hardcoded `Upload PDF` heading/button text is no longer present
- old hardcoded `Generate course` button text is no longer present

## Validation commands

The v0.2.50 implementation passed:

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

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\smoke-minimal-ui-key-integration.py
```

## What was intentionally not changed

v0.2.50 did not add:

- broad UI localization
- language selector
- browser-locale detection
- persisted language preference
- adaptive UI switching
- schema changes
- release asset changes

## Remaining UI work

The UI is not fully localized yet.

Remaining visible labels should be integrated in later small milestones, for example:

```text
ui.choose_file
ui.generated
ui.source_mode
ui.figures
ui.edit_crops
ui.study
ui.review_weak
ui.progress
ui.logs
ui.delete_from_library
```

## Recommended next milestone

```text
v0.2.52-public-beta-language-pack-ui-expansion-plan
```

Suggested next work:

- plan a second small UI key integration batch
- include only safe visible labels
- avoid a broad UI rewrite
- keep validation narrow and repeatable

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

v0.2.51 documents the v0.2.50 minimal UI key integration.

The language-pack UI path is now proven in a small, controlled way.
