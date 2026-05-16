# Voila! Language Pack Packaging Script Plan

Milestone: v0.2.28-public-beta-language-pack-packaging-script-plan
Status: packaging script planning only
Scope: documentation only; no packaging script changes, no runtime changes, no UI changes, no licensing changes

## Goal

This milestone documents where language-pack packaging support should be added in a future packaging implementation milestone.

## Non-goals

This milestone does not:

- modify scripts/release/build-portable-runtime.ps1
- modify scripts/release/test-standalone-runtime.ps1
- copy language packs into release artifacts
- modify ZIP output
- modify runtime startup scripts
- modify application runtime behavior
- modify UI behavior
- add a LICENSE
- modify the validated v0.2.0-public-beta release

## Current release script observations

The current standalone build flow is centered in:

- scripts/release/build-portable-runtime.ps1

The current standalone smoke test is centered in:

- scripts/release/test-standalone-runtime.ps1

Current build behavior:

- creates a staging app directory
- copies the project into the app staging directory
- removes local-only/generated folders
- creates runtime directories
- writes launchers
- prepares Python runtime
- prepares Tesseract runtime
- prepares Java and LanguageTool runtime
- performs cleanup
- creates the ZIP

Current standalone test behavior:

- extracts the ZIP into a clean folder
- verifies required runtime files
- starts Voila
- checks health
- checks LanguageTool
- checks Tesseract languages
- stops Voila and LanguageTool

## Future build-portable-runtime.ps1 insertion point

Future language-pack packaging should happen after the project copy into the staging app directory and before final ZIP cleanup.

Recommended future action:

- verify language-packs/core exists in staging
- verify language-packs/schema exists in staging
- optionally remove language-packs/samples if not intended for packaged output
- run a packaged-staging inspection before ZIP creation

Do not add this behavior in v0.2.28.

## Future test-standalone-runtime.ps1 insertion point

Future standalone test updates should add language-pack required files to the standalone required files list.

Recommended future required files:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

Recommended future optional files:

- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json
- language-packs/runtime/minimal_language_runtime.py

Do not add these required files in v0.2.28.

## Future packaged inspection command

After a future build creates a staged app folder, this command should be usable:

powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1 -PackagedAppRoot <PACKAGED_APP_ROOT>

Example:

powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1 -PackagedAppRoot D:\dev\release-tests\voila-test\app

## Risk control

Main risks:

- language packs are omitted from ZIP
- schema is omitted from ZIP
- runtime relies on development-only paths
- samples are packaged unintentionally
- packaging changes are mixed with UI/runtime changes
- v0.2.0-public-beta release assets are touched accidentally

Mitigation:

- keep script changes separate
- inspect source before packaging
- inspect packaged app after build
- update standalone smoke test in a separate PR
- avoid changing runtime/UI in the packaging PR

## Recommended next milestone

v0.2.29-public-beta-language-pack-packaging-script-scaffold

Suggested next work:

- add a small non-invasive helper/check inside release flow, or
- add a dry-run packaging verification step,
- still avoid changing final ZIP content until tested separately

## Decision for this milestone

For v0.2.28-public-beta-language-pack-packaging-script-plan, the correct action is documentation only.

Do not modify release scripts in this milestone.
