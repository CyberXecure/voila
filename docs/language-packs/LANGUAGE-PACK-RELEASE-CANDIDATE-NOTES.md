# Voila! Language Pack Release Candidate Notes

Milestone: v0.3.0-public-beta-language-pack-release-candidate-notes
Status: release notes planning
Scope: documentation only; no ZIP build, no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish, no LICENSE change

## Purpose

This milestone drafts the release notes structure for a future Voila! v0.3.0 language-pack release candidate.

This milestone does not publish a release and does not create a release asset.

## Proposed release title

```text
Voila! v0.3.0 Public Beta — Language Pack Release Candidate
```

## Proposed release type

```text
GitHub prerelease
language-pack readiness release candidate
documentation + validation focused
```

## Summary for future release notes

This release candidate prepares the Voila! language-pack workstream for public testing.

It includes the language-pack schema, English and Romanian core packs, sample packs, validation tools, runtime helper coverage, UI localization documentation, release-readiness documentation, and release-candidate planning documentation.

## Included language-pack assets

Future release notes should list:

```text
language-packs/core/en.language-pack.json
language-packs/core/ro.language-pack.json
language-packs/schema/language-pack.schema.json
language-packs/samples/en.language-pack.sample.json
language-packs/samples/ro.language-pack.sample.json
language-packs/runtime/minimal_language_runtime.py
```

## Included documentation areas

Future release notes should summarize:

```text
language-pack plan
supported languages
schema documentation
UI error/status localization rollup
full UI localization rollup
release-readiness inventory/checklist/runbook
release-candidate plan/checklist/package plan
```

## Included validation tools

Future release notes should list:

```text
scripts/language-packs/validate-language-packs.py
scripts/release/inspect-language-pack-packaging.ps1
language-pack runtime tests
minimal runtime tests
UI key tests
UI smoke tests
full UI localization smoke tests
error/status integration smoke tests
```

## Required validation before publishing

Future release notes should state that the RC passed:

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

python .\scripts\language-packs\smoke-ui-language-endpoint.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python .\scripts\language-packs\smoke-language-pack-files.py
python .\scripts\language-packs\smoke-ui-core-keys.py
python .\scripts\language-packs\smoke-ui-full-localization-first-batch.py
python .\scripts\language-packs\smoke-ui-full-localization-next-batch.py
python .\scripts\language-packs\smoke-ui-error-status-final-deferred-integration.py

python -m py_compile .\services\api\i18n.py
python -m py_compile .\services\api\web_app.py
```

## Security note

Future release notes must include:

```text
The v0.2.81 reflected-XSS fix is preserved: dynamic page-not-found values are escaped with _html_escape(str(page)).
```

Future notes should also state that dynamic values inserted into HTML must remain escaped.

## Deferred features

Future release notes should clearly defer:

```text
language selector
browser-locale detection
persisted language preference
adaptive UI switching
automatic translation generation
paid supporter package assets
commercial packaging
LICENSE addition or change
```

## Known non-goals

Future release notes should say the RC does not:

```text
change runtime behavior
change schema compatibility
change existing v0.2.0 public-beta assets
publish paid/private assets
add a LICENSE
```

## Proposed asset names

Future release notes should reference asset names only after final confirmation.

Draft naming pattern:

```text
voila-v0.3.0-public-beta-language-pack-rc1.zip
voila-v0.3.0-public-beta-language-pack-rc1.sha256
voila-v0.3.0-public-beta-language-pack-rc1-release-notes.md
voila-v0.3.0-public-beta-language-pack-rc1-final-checklist.md
voila-v0.3.0-public-beta-language-pack-rc1-test-log.md
```

## Checksum section

Future release notes should include:

```text
SHA256: <final checksum generated from final ZIP>
```

Do not insert a checksum until the ZIP is final.

## Publishing guard

This milestone must not:

```text
build a ZIP
create a Git tag
upload GitHub release assets
publish a public ZIP
publish checksum assets
publish release notes assets
add or change LICENSE
```

## Decision

This milestone defines the release notes content and structure only.

Actual release notes asset creation and publishing remain deferred.
