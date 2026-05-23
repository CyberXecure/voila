# Voila! Language Pack Release Candidate Build Plan

Milestone: v0.3.0-public-beta-language-pack-release-candidate-build-plan
Status: build planning
Scope: documentation only; no ZIP build, no SHA256 asset, no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish, no LICENSE change

## Purpose

This milestone plans the future build process for a Voila! v0.3.0 language-pack release candidate.

This milestone does not build a ZIP and does not publish release assets.

## Build outputs to create later

A future build milestone may create:

```text
voila-v0.3.0-public-beta-language-pack-rc1.zip
voila-v0.3.0-public-beta-language-pack-rc1.sha256
voila-v0.3.0-public-beta-language-pack-rc1-release-notes.md
voila-v0.3.0-public-beta-language-pack-rc1-final-checklist.md
voila-v0.3.0-public-beta-language-pack-rc1-test-log.md
```

Final names must be confirmed before any build.

## Safe build order

A future build milestone should follow this order:

```text
sync main
confirm clean working tree
confirm no open PRs
run validation commands
run smoke commands
run Python compile
confirm v0.2.81 _html_escape(str(page)) fix
create a clean staging directory
copy approved files only
exclude forbidden files and directories
create ZIP from staging directory
inspect ZIP contents
generate SHA256 from final ZIP
write test log
write final checklist
do not upload until a separate publish milestone
```

## Required validation before build

Run from repository root before staging:

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

## Staging directory plan

A future build should stage files under a new temporary release directory, for example:

```text
D:\dev\releases\voila-v0.3.0-language-pack-rc1-stage
```

The final ZIP should be built from the staging directory only.

## Candidate staging contents

Copy only approved package contents:

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

## Required exclusions

A future build must exclude:

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

## ZIP inspection

After creating the ZIP, inspect contents and verify:

```text
required language-pack files are present
required docs are present
required validation scripts are present
forbidden directories are absent
stale RC ZIPs are absent
old checksum files are absent
no private/commercial-only files are included
```

## SHA256 generation

Generate SHA256 only after the ZIP is final.

Recommended shape for future build milestone:

```powershell
Get-FileHash $ZipPath -Algorithm SHA256
```

Do not generate a final checksum in this planning milestone.

## Test log

A future build milestone should write a test log containing:

```text
date/time
branch
commit SHA
validation commands run
smoke commands run
Python compile results
ZIP path
SHA256
release safety confirmation
```

## Final checklist

A future build milestone should write a final checklist confirming:

```text
clean worktree
no open PRs
validation passed
smokes passed
XSS fix present
ZIP inspected
SHA256 generated from final ZIP
no tag created
no GitHub release uploaded
no public ZIP published
no LICENSE changed
```

## Publishing remains deferred

This build plan does not authorize:

```text
Git tag
GitHub release upload
public ZIP publish
release notes asset upload
checksum asset upload
LICENSE addition or change
```

## Decision

This milestone defines the build plan only.

Actual ZIP creation, checksum generation, and publishing remain deferred to later explicit milestones.
