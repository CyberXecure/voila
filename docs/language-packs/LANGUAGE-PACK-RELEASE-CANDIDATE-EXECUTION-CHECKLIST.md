# Voila! Language Pack Release Candidate Execution Checklist

Milestone: v0.3.0-public-beta-language-pack-release-candidate-checklist
Status: execution checklist
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish, no LICENSE change

## Purpose

This checklist converts the v0.3.0 release-candidate plan into an executable RC checklist.

This milestone does not publish a release.

## RC gate

Before any release-candidate build milestone, confirm:

- [ ] The release candidate version is final.
- [ ] The target release branch is final.
- [ ] The package plan exists.
- [ ] The release notes plan exists.
- [ ] The final ZIP name is defined.
- [ ] The final SHA256 name is defined.
- [ ] GitHub release title/body are drafted.
- [ ] No LICENSE change is required.
- [ ] Publishing is explicitly approved by a later milestone.

## Repository state

Before RC packaging, confirm:

- [ ] `main` is synced.
- [ ] The working tree is clean.
- [ ] There are no open PRs.
- [ ] CodeQL/security checks are passing.
- [ ] There are no unreviewed release-blocker issues.
- [ ] There is no stale RC ZIP staged for upload.

## Required source/docs

Confirm these files exist:

- [ ] `docs/language-packs/LANGUAGE-PACK-RELEASE-CANDIDATE-PLAN.md`
- [ ] `docs/language-packs/LANGUAGE-PACK-RELEASE-CANDIDATE-CHECKLIST.md`
- [ ] `docs/language-packs/LANGUAGE-PACK-RELEASE-READINESS-DOCS.md`
- [ ] `docs/language-packs/LANGUAGE-PACK-RELEASE-READINESS-CHECKLIST.md`
- [ ] `docs/language-packs/LANGUAGE-PACK-RELEASE-READINESS-RUNBOOK.md`
- [ ] `docs/language-packs/LANGUAGE-PACK-UI-ERROR-STATUS-ROLLUP.md`
- [ ] `docs/language-packs/LANGUAGE-PACK-UI-FULL-LOCALIZATION-ROLLUP.md`
- [ ] `language-packs/core/en.language-pack.json`
- [ ] `language-packs/core/ro.language-pack.json`
- [ ] `language-packs/schema/language-pack.schema.json`
- [ ] `language-packs/samples/en.language-pack.sample.json`
- [ ] `language-packs/samples/ro.language-pack.sample.json`
- [ ] `language-packs/runtime/minimal_language_runtime.py`

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

## Security checks

Confirm:

- [ ] v0.2.81 `_html_escape(str(page))` reflected-XSS fix is present.
- [ ] Dynamic values inserted into HTML are escaped.
- [ ] Generated course/OCR/user-authored content is not blindly localized.
- [ ] Route behavior is preserved.
- [ ] HTTP status codes are preserved.
- [ ] Fallback English text remains available.

## Release blocker checks

Stop the RC process if any of these are true:

- [ ] Validation fails.
- [ ] Smoke test fails.
- [ ] Python compile fails.
- [ ] CodeQL/security checks fail.
- [ ] Working tree is dirty.
- [ ] Open PRs exist.
- [ ] Release notes are missing.
- [ ] ZIP contents are undefined.
- [ ] Checksum is missing.
- [ ] LICENSE/commercial-positioning decision is unclear.

## Publishing guard

This checklist milestone must not perform:

- [ ] Git tag creation
- [ ] GitHub release upload
- [ ] public ZIP publish
- [ ] final checksum publish
- [ ] release notes asset upload
- [ ] LICENSE addition or change

## Decision

This is an execution checklist for a future release candidate.

It does not authorize publishing.
