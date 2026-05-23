# Voila! Language Pack Release Candidate Plan

Milestone: v0.3.0-public-beta-language-pack-release-candidate-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish, no LICENSE change

## Goal

This milestone creates an explicit release-candidate plan for a future public beta release that includes the language-pack workstream.

This milestone does not publish a release.

## Why this plan exists

The language-pack workstream now has:

```text
schema documentation
sample packs
core English and Romanian packs
runtime helper coverage
validator coverage
UI error/status localization
full UI localization
release-readiness inventory
release-readiness checklist and runbook
```

The next safe step is to define what a release candidate would contain before creating tags, ZIPs, checksums, or GitHub release assets.

## Proposed release identity

Proposed release line:

```text
v0.3.0-public-beta-language-pack-release-candidate
```

Proposed release nature:

```text
public beta / prerelease
language-pack readiness release candidate
documentation + validation centered
no licensing change unless explicitly approved
```

## Candidate release goals

A future RC should prove that:

```text
language packs are discoverable
core packs validate
sample packs remain consistent
runtime fallback behavior is tested
UI localization coverage is documented
security constraints are documented and checked
packaging inspection includes language-pack artifacts
release notes clearly describe supported/deferred scope
```

## Candidate release assets to define later

A future release milestone must define final names for:

```text
public ZIP
SHA256 checksum
release notes
final checklist or test log
GitHub release title
GitHub release body
```

Do not publish these assets in this planning milestone.

## Candidate release contents

Potential release contents should include:

```text
language-packs/core/en.language-pack.json
language-packs/core/ro.language-pack.json
language-packs/schema/language-pack.schema.json
language-packs/samples/en.language-pack.sample.json
language-packs/samples/ro.language-pack.sample.json
language-packs/runtime/minimal_language_runtime.py
docs/language-packs/
scripts/language-packs/
scripts/release/inspect-language-pack-packaging.ps1
services/api/i18n.py
services/api/web_app.py
```

The final package contents must be confirmed in a dedicated package-plan milestone before publishing.

## Must not include unless explicitly approved

```text
LICENSE addition or change
paid supporter package assets
private/commercial files
stale release-candidate ZIPs
old checksum files
local virtual environments
node_modules
__pycache__
.git
developer-only backups
```

## Required validation baseline

A future RC must pass:

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

## Security requirements

A future RC must confirm:

```text
v0.2.81 _html_escape(str(page)) reflected-XSS fix remains present
dynamic values inserted into HTML are escaped
generated course/OCR/user-authored content is not blindly localized
route behavior is preserved
HTTP status codes are preserved
fallback English text remains available
```

## Release blockers

Do not proceed to release publishing if any of these are true:

```text
validation fails
smoke test fails
CodeQL/security checks fail
working tree is dirty
open PRs exist
release notes are missing
ZIP contents are undefined
checksum is missing
LICENSE/commercial-positioning decision is unclear
```

## Recommended next milestones

Recommended path:

```text
v0.3.0-public-beta-language-pack-release-candidate-checklist
v0.3.0-public-beta-language-pack-release-candidate-package-plan
v0.3.0-public-beta-language-pack-release-candidate-notes
v0.3.0-public-beta-language-pack-release-candidate-build
```

Only the final build/publish milestone should be allowed to create a tag, ZIP, checksum, and GitHub release assets.

## Non-goals

This milestone does not:

- modify UI code
- add language-pack JSON keys
- modify schema
- modify runtime behavior
- create a Git tag
- upload GitHub release assets
- publish a ZIP
- generate a final checksum asset
- add or change LICENSE files

## Decision

v0.3.0-public-beta-language-pack-release-candidate-plan is documentation only.

It authorizes planning for an RC path, not publishing.
