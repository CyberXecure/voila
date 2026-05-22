# Voila! Language Pack Release Readiness Inventory

Milestone: v0.2.97-public-beta-language-pack-release-readiness-inventory
Status: inventory
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone inventories what must be checked before any future public release that includes the language-pack workstream.

It does not publish a release. It prepares the checklist surface only.

## Baseline

This inventory builds on:

```text
v0.2.96 cleanup or release-readiness plan
UI error/status localization rollup
full UI localization rollup
core language packs for English and Romanian
language-pack schema
sample language packs
minimal language runtime helper
validator coverage
packaging inspection coverage
v0.2.81 reflected-XSS fix using _html_escape(str(page))
```

## Release-readiness inventory

Before any future language-pack release, inspect these areas:

```text
documentation discoverability
supported languages documentation
schema documentation
core pack contents
sample pack consistency
runtime fallback behavior
validator output
smoke command list
packaging inspection command
security notes
known deferred features
release notes draft
public ZIP contents
GitHub release asset names
SHA256 generation
no-LICENSE/commercial-positioning constraints
```

## Required validation commands

Minimum validation set:

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\test_ui_core_keys.py
python .\scripts\language-packs\test_ui_remaining_core_keys.py
python .\scripts\language-packs\test_ui_error_status_core_keys.py
python .\scripts\language-packs\test_ui_full_localization_core_keys.py
python .\scripts\language-packs\test_ui_full_localization_next_batch_core_keys.py

python .\scripts\language-packs\smoke-ui-full-localization-first-batch.py
python .\scripts\language-packs\smoke-ui-full-localization-next-batch.py
python .\scripts\language-packs\smoke-ui-error-status-final-deferred-integration.py

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
```

## Documentation inventory

Confirm these documentation files are present and still accurate:

```text
docs/language-packs/LANGUAGE-PACK-PLAN.md
docs/language-packs/LANGUAGE-PACK-SCHEMA.md
docs/language-packs/SUPPORTED-LANGUAGES.md
docs/language-packs/LANGUAGE-PACK-UI-ERROR-STATUS-ROLLUP.md
docs/language-packs/LANGUAGE-PACK-UI-FULL-LOCALIZATION-ROLLUP.md
docs/language-packs/LANGUAGE-PACK-CLEANUP-OR-RELEASE-READINESS-PLAN.md
```

## Source inventory

Confirm these source files are present and included where expected:

```text
language-packs/core/en.language-pack.json
language-packs/core/ro.language-pack.json
language-packs/schema/language-pack.schema.json
language-packs/samples/en.language-pack.sample.json
language-packs/samples/ro.language-pack.sample.json
language-packs/runtime/minimal_language_runtime.py
scripts/language-packs/validate-language-packs.py
scripts/release/inspect-language-pack-packaging.ps1
services/api/i18n.py
services/api/web_app.py
```

## Security readiness

Security notes for release-readiness:

```text
preserve _html_escape(str(page)) for dynamic page-not-found output
escape dynamic values inserted into HTML
do not localize generated course/OCR/user-authored content blindly
preserve fallback English text
preserve route behavior and HTTP status codes
```

## Deferred release decisions

Still deferred unless explicitly planned:

```text
GitHub release upload
Git tag
public ZIP publish
release notes asset
final checksum asset
LICENSE addition or change
paid supporter / commercial packaging
language selector
browser-locale detection
persisted language preference
adaptive UI switching
```

## Recommended next milestone

Recommended next milestone:

```text
v0.2.98-public-beta-language-pack-release-readiness-checklist
```

That milestone should turn this inventory into a practical pre-release checklist without uploading release assets.

## Non-goals

This milestone does not:

- modify UI code
- add language-pack JSON keys
- modify schema
- modify runtime behavior
- upload GitHub release assets
- create a Git tag
- publish a ZIP
- modify LICENSE files

## Decision

v0.2.97 is documentation only.

It inventories release-readiness requirements for the language-pack workstream without performing a release.
