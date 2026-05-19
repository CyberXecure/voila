# Voila! UI Remaining Integration Plan

Milestone: v0.2.64-public-beta-language-pack-ui-remaining-integration-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the first small UI integration batch using the remaining core keys added in v0.2.62.

The goal is to select low-risk visible UI labels before making any UI code changes.

## Baseline

This plan builds on:

- v0.2.62 remaining `ui.*`, `message.*`, and `status.*` core keys
- v0.2.63 documentation for the remaining core keys
- existing UI smoke helpers and language-pack validation

## Candidate scan

The scan reviewed these visible hardcoded labels in `services/api/web_app.py`:

```text
Logs
Course Tools
Quick Tools
Review OCR Text
Review Concepts
Review Study Concepts
Correct OCR Text
Study mode
Toggle theme
Save title override
Fit width
```

## Recommended first integration batch

The first implementation batch should stay small and patch only short, visible labels.

Recommended candidates:

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

## Candidate classification

### Low-risk action/navigation labels

```text
Logs
Course Tools
Quick Tools
Review OCR Text
Review Concepts
Review Study Concepts
Correct OCR Text
Study mode
Toggle theme
Fit width
```

Recommended action:

```text
safe for a small future UI integration batch
```

### Medium-risk action labels

```text
Save title override
```

Recommended action:

```text
safe only if patched in the exact button location, not in error headings
```

### Do not patch in the first batch

```text
Save title override failed
Study Mode inside longer helper text
Course tools with lowercase spelling unless normalized intentionally
log/debug variables
```

Recommended action:

```text
defer or patch in a later status/message batch
```

## Future implementation rules

The next implementation milestone should:

- patch only exact visible UI labels
- use existing `_ut(...)` helper
- preserve current fallback text
- avoid changing generated content
- avoid changing error/debug/log text
- avoid broad UI rewrite
- add a focused smoke helper
- keep language-pack JSON unchanged
- keep schema unchanged

## Suggested future smoke helper

```text
scripts/language-packs/smoke-ui-remaining-integration.py
```

It should verify that:

- selected `ui.*` keys are used in `services/api/web_app.py`
- selected old hardcoded snippets were removed only where intentionally replaced
- no generated/log/debug strings were patched accidentally

## Recommended validation after future implementation

Run:

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

## Recommended next milestone

```text
v0.2.65-public-beta-language-pack-ui-remaining-integration
```

Suggested next work:

- patch the first small group of low-risk UI labels
- add `smoke-ui-remaining-integration.py`
- keep core language-pack JSON unchanged
- keep schema unchanged
- avoid full UI localization

## Non-goals

This milestone does not:

- modify UI code
- modify language-pack JSON
- modify runtime behavior
- modify schema
- add language selector
- add browser-locale detection
- add persisted language preference
- upload GitHub release assets
- create a Git tag
- publish a ZIP
- modify LICENSE files

## Decision

v0.2.64 is documentation only.

It plans the first small UI integration batch using the remaining core keys added in v0.2.62.
