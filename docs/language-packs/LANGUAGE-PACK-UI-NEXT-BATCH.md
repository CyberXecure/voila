# Voila! UI Next Batch

Milestone: v0.2.57-public-beta-language-pack-ui-next-batch-docs
Status: documentation
Scope: documentation only; no UI code changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the UI next-batch integration completed in v0.2.56.

The implementation continued the controlled language-pack UI rollout after the v0.2.50 minimal integration and the v0.2.53 UI expansion batch.

## Implemented in v0.2.56

Updated file:

```text
services/api/web_app.py
```

Added smoke helper:

```text
scripts/language-packs/smoke-ui-next-batch-key-integration.py
```

## Integrated keys

The v0.2.56 batch uses:

```text
ui.edit_crops
ui.review_weak
ui.generated
ui.source_mode
ui.progress
```

## UI behavior

The following labels are now language-pack-backed:

- Edit crops action link
- Edit crops navigation/card label
- Review weak action link
- Generated status/notice label
- Source Mode notice label
- Progress action link fallback in the home action block

## Deferred key

```text
ui.choose_file
```

`ui.choose_file` remains deferred because no simple visible hardcoded `Choose File` label was found in the inspected UI path.

The existing visible text is a longer sentence:

```text
Choose a PDF from your computer. It will be saved locally in data/input.
```

This should not be replaced with `ui.choose_file` because it is not the same label.

## Fallback behavior

The implementation preserves existing fallback behavior:

```text
ui.edit_crops -> "Edit crops"
ui.review_weak -> "Review weak"
ui.generated -> "Generated"
ui.source_mode -> "Source Mode"
ui.progress -> existing progress key -> "Progress"
```

## Validation coverage

The new smoke helper verifies that:

- `ui.edit_crops` is used in `web_app.py`
- `ui.review_weak` is used in `web_app.py`
- `ui.generated` is used in `web_app.py`
- `ui.source_mode` is used in `web_app.py`
- `ui.progress` remains backed by the existing progress fallback
- selected old hardcoded snippets are no longer present where intentionally replaced

## Validation commands

The v0.2.56 implementation passed:

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
python .\scripts\language-packs\smoke-ui-next-batch-key-integration.py

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\smoke-ui-next-batch-key-integration.py
```

## What was intentionally not changed

v0.2.56 did not add:

- broad UI rewrite
- full UI localization
- language selector
- browser-locale detection
- persisted language preference
- adaptive UI switching
- schema changes
- release asset changes
- `ui.choose_file` integration

## Remaining UI work

The UI is still not fully localized.

Remaining work should continue in small, controlled batches only.

Possible future candidates:

```text
ui.logs
ui.open_course in remaining card/navigation areas
ui.study in remaining hardcoded headings
ui.choose_file only if a matching visible label is found
additional long-message keys for longer helper text
```

## Recommended next milestone

```text
v0.2.58-public-beta-language-pack-ui-remaining-labels-plan
```

Suggested next work:

- inspect remaining visible hardcoded labels
- separate short labels from long helper text
- avoid forcing existing `ui.*` keys onto mismatched sentences
- plan any missing keys before implementation

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

v0.2.57 documents the v0.2.56 UI next-batch implementation.

The language-pack UI integration path now has three controlled implementation batches with focused smoke coverage.
