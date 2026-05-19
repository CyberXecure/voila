# Voila! UI Remaining Integration

Milestone: v0.2.66-public-beta-language-pack-ui-remaining-integration-docs
Status: documentation
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone documents the UI remaining integration implementation completed in v0.2.65.

The implementation used existing core language-pack keys from v0.2.62 and integrated a first small batch of low-risk visible UI labels.

## Implemented in v0.2.65

Updated file:

```text
services/api/web_app.py
```

Added smoke helper:

```text
scripts/language-packs/smoke-ui-remaining-integration.py
```

## Integrated keys

v0.2.65 integrated selected existing `ui.*` keys:

```text
ui.logs
ui.course_tools
ui.quick_tools
ui.review_ocr_text
ui.review_concepts
ui.review_study_concepts
ui.correct_ocr_text
ui.study_mode
ui.toggle_theme
ui.save_title_override
ui.fit_width
```

## UI surfaces covered

The implementation covered low-risk visible labels found in the v0.2.64 scan:

```text
Logs
Course Tools
Quick Tools
Review OCR Text
Review Concepts
Review Study Concepts
Correct OCR Text
Study Mode / Study mode
Toggle theme
Save title override
Fit width
```

## Safety choices

The implementation intentionally avoided:

```text
Save title override failed
Study Mode inside longer helper text
Course tools lowercase text unless intentionally normalized
generated content
debug/log variables
error/status headings not selected for this batch
```

## Validation coverage

The new smoke helper verifies that selected `ui.*` keys are used in `services/api/web_app.py`, selected old hardcoded snippets are no longer present where intentionally replaced, and intentionally deferred text remains unchanged.

## Validation commands

v0.2.65 passed:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\test_ui_core_keys.py
python .\scripts\language-packs\test_ui_remaining_core_keys.py

python .\scripts\language-packs\smoke-ui-language-endpoint.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python .\scripts\language-packs\smoke-language-pack-files.py
python .\scripts\language-packs\smoke-ui-core-keys.py
python .\scripts\language-packs\smoke-minimal-ui-key-integration.py
python .\scripts\language-packs\smoke-ui-expansion-key-integration.py
python .\scripts\language-packs\smoke-ui-next-batch-key-integration.py
python .\scripts\language-packs\smoke-ui-remaining-core-keys.py
python .\scripts\language-packs\smoke-ui-remaining-integration.py

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
python -m py_compile .\scripts\language-packs\smoke-ui-remaining-integration.py
```

## What was intentionally not changed

v0.2.65 did not add language-pack JSON changes, schema changes, broad UI rewrite, language selector, browser-locale detection, persisted language preference, adaptive UI switching, GitHub release upload, Git tag, public ZIP publish, or LICENSE changes.

## Remaining work

The UI is still not fully localized. Remaining work should continue in small controlled batches.

Potential future batches:

```text
message.* card/helper descriptions
status.* notice/meta labels
additional exact short UI labels
remaining headings only where semantically exact
```

## Recommended next milestone

```text
v0.2.67-public-beta-language-pack-ui-status-message-integration-plan
```

Suggested next work:

- plan a small status/message integration batch
- keep implementation deferred
- avoid changing generated/log/debug text
- avoid full UI rewrite

## Decision

v0.2.66 documents the completed v0.2.65 UI remaining integration batch.
