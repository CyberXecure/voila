# Voila! Language Pack Packaging Script Scaffold

Milestone: v0.2.29-public-beta-language-pack-packaging-script-scaffold
Status: dry-run/readiness scaffold
Scope: documentation and dry-run script only; no real packaging changes, no runtime changes, no UI changes, no licensing changes

## Goal

This milestone adds a safe dry-run scaffold for future language-pack packaging work.

## What changed

- Adds docs/language-packs/LANGUAGE-PACK-PACKAGING-SCRIPT-SCAFFOLD.md
- Adds scripts/release/test-language-pack-packaging-readiness.ps1

## What this milestone does not do

- does not modify scripts/release/build-portable-runtime.ps1
- does not modify scripts/release/test-standalone-runtime.ps1
- does not modify ZIP output
- does not modify real release artifacts
- does not change runtime behavior
- does not change UI behavior
- does not add a LICENSE
- does not modify the validated v0.2.0-public-beta release

## Why this scaffold exists

Before changing real release scripts, Voila! needs a dry-run check that proves the required language-pack files can be copied into a packaged-app-like folder and inspected successfully.

## Dry-run script

Run from repository root:

powershell -ExecutionPolicy Bypass -File .\scripts\release\test-language-pack-packaging-readiness.ps1

Optional with samples:

powershell -ExecutionPolicy Bypass -File .\scripts\release\test-language-pack-packaging-readiness.ps1 -IncludeSamples

## Expected result

Language pack packaging readiness dry-run passed.

## Dry-run behavior

The script:

- creates a temporary packaged-app-like folder
- copies language-packs/core into it
- copies language-packs/schema into it
- optionally copies language-packs/samples into it
- runs inspect-language-pack-packaging.ps1 against the temporary app root
- removes the temporary folder unless -KeepTemp is used

## Safety

This script does not call build-portable-runtime.ps1.

This script does not create or modify a release ZIP.

This script does not modify the real packaging flow.

## Recommended next milestone

v0.2.30-public-beta-language-pack-packaging-script-integration-plan

## Decision for this milestone

For v0.2.29-public-beta-language-pack-packaging-script-scaffold, the correct action is a dry-run scaffold only.

Do not modify real release scripts in this milestone.
