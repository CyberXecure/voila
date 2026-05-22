# Voila! Language Pack Release Readiness Checklist

Milestone: v0.2.98-public-beta-language-pack-release-readiness-checklist
Status: checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Purpose

This checklist converts the v0.2.97 release-readiness inventory into a practical pre-release checklist for the language-pack workstream.

This milestone does not publish a release.

## Pre-release gate

Before any future language-pack release, confirm:

- [ ] The target release milestone explicitly allows publishing release assets.
- [ ] The release branch name and tag name are defined.
- [ ] The release notes filename is defined.
- [ ] The public ZIP filename is defined.
- [ ] The SHA256 filename is defined.
- [ ] Licensing/commercial-positioning decision is still valid.
- [ ] No LICENSE file is added unless explicitly approved.
- [ ] Existing v0.2.0-public-beta assets remain unchanged unless the release milestone says otherwise.

## Documentation readiness

Confirm these docs exist and are current:

- [ ] `docs/language-packs/LANGUAGE-PACK-PLAN.md`
- [ ] `docs/language-packs/LANGUAGE-PACK-SCHEMA.md`
- [ ] `docs/language-packs/SUPPORTED-LANGUAGES.md`
- [ ] `docs/language-packs/LANGUAGE-PACK-UI-ERROR-STATUS-ROLLUP.md`
- [ ] `docs/language-packs/LANGUAGE-PACK-UI-FULL-LOCALIZATION-ROLLUP.md`
- [ ] `docs/language-packs/LANGUAGE-PACK-CLEANUP-OR-RELEASE-READINESS-PLAN.md`
- [ ] `docs/language-packs/LANGUAGE-PACK-RELEASE-READINESS-INVENTORY.md`

## Source readiness

Confirm these files exist and are intended for release packaging or documentation:

- [ ] `language-packs/core/en.language-pack.json`
- [ ] `language-packs/core/ro.language-pack.json`
- [ ] `language-packs/schema/language-pack.schema.json`
- [ ] `language-packs/samples/en.language-pack.sample.json`
- [ ] `language-packs/samples/ro.language-pack.sample.json`
- [ ] `language-packs/runtime/minimal_language_runtime.py`
- [ ] `scripts/language-packs/validate-language-packs.py`
- [ ] `scripts/release/inspect-language-pack-packaging.ps1`
- [ ] `services/api/i18n.py`
- [ ] `services/api/web_app.py`

## Required validation commands

Run from repository root:

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

Expected result:

```text
all validation commands pass
all smoke commands pass
Python compile passes
working tree remains clean
```

## Security readiness

Confirm:

- [ ] The v0.2.81 page-not-found reflected-XSS fix is still present: `_html_escape(str(page))`.
- [ ] Dynamic values inserted into HTML are escaped.
- [ ] Generated course/OCR/user-authored content is not blindly localized.
- [ ] Route behavior is unchanged.
- [ ] HTTP status codes are unchanged.
- [ ] Fallback English text remains available.

## Packaging readiness

Before publishing assets, confirm:

- [ ] Public ZIP contents are explicitly listed.
- [ ] Excluded directories are explicitly listed.
- [ ] SHA256 is generated after the final ZIP is built.
- [ ] The SHA256 value is copied into release notes.
- [ ] GitHub release asset names are final.
- [ ] Release notes are attached as an asset or included in the release body.
- [ ] No stale RC ZIP is published by accident.

## Deferred until explicit release milestone

Do not do these in this checklist milestone:

- [ ] GitHub release upload
- [ ] Git tag
- [ ] public ZIP publish
- [ ] release notes asset
- [ ] checksum asset
- [ ] LICENSE addition or change
- [ ] paid supporter / commercial packaging
- [ ] language selector
- [ ] browser-locale detection
- [ ] persisted language preference
- [ ] adaptive UI switching

## Decision

This checklist is a pre-release readiness tool only.

It should be used before a future release milestone, not as a release milestone itself.
