# Voila! Language Pack Runtime Minimal Integration Checklist

Milestone: v0.2.14-public-beta-language-pack-runtime-minimal-integration-plan  
Status: pre-implementation checklist / documentation only  
Scope: no application runtime changes, no UI changes, no packaging changes, no licensing changes

## Goal

This checklist defines the go/no-go conditions for the first real runtime language pack integration.

The checklist must be satisfied before touching application runtime files.

## Go criteria

The first runtime implementation can begin only if:

- main branch is clean
- previous language pack PRs are merged
- validator passes
- runtime scaffold tests pass
- preview commands pass
- first key subset is small
- rollback plan is clear
- implementation touches only a few files
- no packaging changes are required
- no release artifacts are modified

## No-go criteria

Do not start runtime implementation if:

- working tree is dirty
- validator fails
- runtime scaffold tests fail
- sample packs are invalid
- packaging changes are needed immediately
- selected language behavior is unclear
- fallback behavior is unclear
- integration would touch many UI files
- implementation requires new dependencies
- implementation requires LICENSE changes
- implementation affects v0.2.0-public-beta release artifacts

## Required pre-check commands

Run from repository root:

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\preview-language-pack-runtime.py --language ro --key lesson.progress --current 2 --total 10
python .\scripts\language-packs\preview-language-pack-runtime.py --language en --key lesson.progress --current 2 --total 10
python .\scripts\language-packs\preview-language-pack-runtime.py --language fr --key button.save

Expected output:

Language pack validation passed.
OK
Lecția 2 din 10
Lesson 2 of 10
Save

## Recommended first key subset

Use only:

- app.title
- app.subtitle
- button.start
- button.cancel
- button.save
- button.export
- status.ready
- status.processing

Do not use:

- all messages keys
- all feedback keys
- all glossary keys
- possible-pro keys
- draft keys that are not yet needed

## Recommended first integration target

Choose one low-risk area.

Preferred:

- app title/subtitle
- small static landing/header area
- non-critical status label

Avoid:

- PDF processing
- OCR logic
- export generation
- file import pipeline
- installer behavior
- standalone startup behavior
- security-sensitive logic

## App-side helper checklist

The first helper should:

- be isolated
- have no external dependencies
- provide safe fallback
- not require language packs to exist
- not crash on invalid JSON
- keep caller default text
- preserve missing placeholders

## Runtime behavior checklist

The first runtime integration should prove:

- app starts with default language
- app starts when language packs are missing
- app starts when selected key is missing
- fallback default text is used
- UI remains usable
- no runtime crash occurs

## Packaging checklist

Do not change packaging in the first implementation unless absolutely necessary.

Before future packaging work, verify:

- bundled language files are included
- packaged app can find them
- app works without dev-only paths
- app starts without internet access
- app starts without remote language files

## Rollback checklist

Rollback must be simple:

- one PR revert should disable the integration
- existing hardcoded fallback strings remain available
- no database migration is involved
- no user settings migration is involved
- no packaging migration is involved

## PR checklist for first implementation

The first implementation PR should state:

- exact files touched
- exact keys integrated
- fallback behavior
- commands run
- rollback approach
- confirmation that v0.2.0-public-beta release artifacts remain unchanged

## Commands to include in first implementation PR

Recommended validation block:

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py

Recommended app smoke test:

Use the existing local run command for Voila!, then verify the app starts normally.

Exact app command should be taken from the current project docs/scripts at implementation time.

## Current decision

For v0.2.14-public-beta-language-pack-runtime-minimal-integration-plan, this checklist is documentation only.

No application runtime files should be modified.
