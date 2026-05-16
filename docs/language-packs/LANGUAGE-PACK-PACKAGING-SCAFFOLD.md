# Voila! Language Pack Packaging Scaffold

Milestone: v0.2.27-public-beta-language-pack-packaging-scaffold
Status: non-invasive packaging scaffold
Scope: documentation and inspection script only; no packaging changes, no runtime changes, no UI changes, no licensing changes

## Goal

This milestone adds a safe scaffold for inspecting language pack packaging readiness.

## What changed

- Adds docs/language-packs/LANGUAGE-PACK-PACKAGING-SCAFFOLD.md
- Adds scripts/release/inspect-language-pack-packaging.ps1

## What this milestone does not do

- does not modify build-portable-runtime.ps1
- does not modify test-standalone-runtime.ps1
- does not copy language packs into release artifacts
- does not modify standalone ZIP output
- does not change runtime behavior
- does not change UI behavior
- does not add a LICENSE
- does not modify the validated v0.2.0-public-beta release

## Why this scaffold exists

Before changing real packaging scripts, Voila! needs a safe way to inspect which language-pack files exist in the source tree and which files should later be expected in a packaged app folder.

## Inspection script

Run from repository root:

powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1

Optional future packaged-folder check:

powershell -ExecutionPolicy Bypass -File .\scripts\release\inspect-language-pack-packaging.ps1 -PackagedAppRoot D:\dev\release-tests\some-build\app

## Required source files

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

## Optional source files

- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json
- language-packs/runtime/minimal_language_runtime.py

## Recommended next milestone

v0.2.28-public-beta-language-pack-packaging-script-plan

## Decision for this milestone

For v0.2.27-public-beta-language-pack-packaging-scaffold, the correct action is inspection only.

Do not change real packaging scripts in this milestone.
