# Voila! Language Pack Release Candidate Package Plan

Milestone: v0.3.0-public-beta-language-pack-release-candidate-package-plan
Status: package planning
Scope: documentation only; no ZIP build, no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish, no LICENSE change

## Purpose

This milestone defines what a future language-pack release-candidate package should contain and exclude.

This milestone does not build or publish a ZIP.

## Proposed package identity

Recommended future package naming pattern:

```text
voila-v0.3.0-public-beta-language-pack-rc1.zip
voila-v0.3.0-public-beta-language-pack-rc1.sha256
voila-v0.3.0-public-beta-language-pack-rc1-release-notes.md
voila-v0.3.0-public-beta-language-pack-rc1-final-checklist.md
voila-v0.3.0-public-beta-language-pack-rc1-test-log.md
```

Final names must be confirmed in a later build milestone.

## Candidate package contents

The future RC package should include these language-pack and readiness areas:

```text
docs/language-packs/
language-packs/core/
language-packs/schema/
language-packs/samples/
language-packs/runtime/
scripts/language-packs/
scripts/release/inspect-language-pack-packaging.ps1
services/api/i18n.py
services/api/web_app.py
```

## Required language-pack files

Required package files:

```text
language-packs/core/en.language-pack.json
language-packs/core/ro.language-pack.json
language-packs/schema/language-pack.schema.json
language-packs/samples/en.language-pack.sample.json
language-packs/samples/ro.language-pack.sample.json
language-packs/runtime/minimal_language_runtime.py
```

## Required documentation

Required documentation directory:

```text
docs/language-packs/
```

At minimum, it should include:

```text
LANGUAGE-PACK-PLAN.md
LANGUAGE-PACK-SCHEMA.md
SUPPORTED-LANGUAGES.md
LANGUAGE-PACK-UI-ERROR-STATUS-ROLLUP.md
LANGUAGE-PACK-UI-FULL-LOCALIZATION-ROLLUP.md
LANGUAGE-PACK-RELEASE-READINESS-DOCS.md
LANGUAGE-PACK-RELEASE-READINESS-CHECKLIST.md
LANGUAGE-PACK-RELEASE-CANDIDATE-PLAN.md
LANGUAGE-PACK-RELEASE-CANDIDATE-EXECUTION-CHECKLIST.md
LANGUAGE-PACK-RELEASE-CANDIDATE-RUNBOOK.md
```

## Required validation scripts

Required scripts:

```text
scripts/language-packs/validate-language-packs.py
scripts/language-packs/test_language_pack_runtime.py
scripts/language-packs/test_minimal_language_runtime.py
scripts/language-packs/test_ui_core_keys.py
scripts/language-packs/test_ui_remaining_core_keys.py
scripts/language-packs/test_ui_error_status_core_keys.py
scripts/language-packs/test_ui_full_localization_core_keys.py
scripts/language-packs/test_ui_full_localization_next_batch_core_keys.py
scripts/language-packs/smoke-ui-language-endpoint.py
scripts/language-packs/smoke-core-runtime-helper.py
scripts/language-packs/smoke-language-pack-files.py
scripts/language-packs/smoke-ui-core-keys.py
scripts/language-packs/smoke-ui-full-localization-first-batch.py
scripts/language-packs/smoke-ui-full-localization-next-batch.py
scripts/language-packs/smoke-ui-error-status-final-deferred-integration.py
scripts/release/inspect-language-pack-packaging.ps1
```

## Required source integration files

Required source files for language-pack runtime/integration context:

```text
services/api/i18n.py
services/api/web_app.py
```

## Exclusions

The package must exclude:

```text
.git/
.venv/
node_modules/
__pycache__/
*.pyc
dist/
build/
release staging directories
local backup ZIPs
old RC ZIPs
old checksum files
temporary _tmp_*.py helper files
local logs
private/commercial-only assets
unapproved paid supporter package assets
LICENSE changes unless explicitly approved
```

## Asset rules

A future build milestone must:

```text
create the ZIP only after validation passes
generate SHA256 only after final ZIP is built
copy the SHA256 into release notes
verify package contents before upload
avoid uploading stale RC ZIPs
avoid overwriting existing public assets accidentally
```

## Checksum rules

SHA256 must be generated from the final ZIP only.

Recommended PowerShell shape for a future build milestone:

```powershell
Get-FileHash .\voila-v0.3.0-public-beta-language-pack-rc1.zip -Algorithm SHA256
```

Do not generate or publish a checksum in this planning milestone.

## Release notes requirements

A future notes milestone should document:

```text
supported languages
included core/sample packs
schema location
validator commands
runtime fallback behavior
UI localization scope
deferred features
security note for _html_escape(str(page))
no LICENSE change
commercial/licensing status
```

## Publishing remains deferred

This milestone must not perform:

```text
ZIP build
Git tag creation
GitHub release upload
public ZIP publish
checksum publish
release notes upload
LICENSE addition or change
```

## Decision

This milestone defines package contents and packaging rules only.

Actual package build and publishing remain deferred to later explicit milestones.
