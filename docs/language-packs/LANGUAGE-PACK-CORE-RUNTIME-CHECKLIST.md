# Voila! Language Pack Core Runtime Checklist

Milestone: v0.2.21-public-beta-language-pack-core-runtime-plan  
Status: pre-runtime checklist  
Scope: documentation only, no runtime changes, no packaging changes, no licensing changes

## Goal

This checklist defines the go/no-go conditions before Voila! runtime loading can prefer core language packs.

## Go criteria

Runtime source switching can begin only if:

- main branch is clean
- no unrelated PRs are open
- validator passes
- runtime scaffold tests pass
- minimal runtime helper tests pass
- UI smoke test passes
- core ro/en packs exist
- core ro/en packs validate
- samples still validate
- fallback behavior is documented
- packaging impact is not mixed into the same PR

## No-go criteria

Do not switch runtime to core if:

- working tree is dirty
- validator fails
- smoke test fails
- core packs are missing
- sample fallback is not defined
- standalone path behavior is unclear
- implementation would require packaging changes immediately
- UI expansion is being mixed into the same PR
- release v0.2.0-public-beta artifacts would be touched

## Required validation commands

Run from repository root:

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python -m py_compile .\services\api\i18n.py

Optional, if Node.js is installed:

node --check .\services\api\static\ocr_review_monaco.js

## Core files to verify

Required current files:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json

Required sample fallback files:

- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json

## First implementation checklist

The first core runtime helper PR should:

- keep current sample tests passing
- add core path tests
- prefer core when available
- fall back to samples when core is missing
- preserve caller defaults
- preserve missing placeholders
- avoid UI changes
- avoid packaging changes

## Runtime fallback checklist

The future helper should support:

- selected language from core
- English from core
- Romanian from core
- selected language from samples
- English from samples
- Romanian from samples
- caller default
- key fallback

## Manual verification checklist

After future runtime source changes:

- run validator
- run runtime tests
- run minimal helper tests
- run UI smoke test
- compile i18n.py
- check OCR Monaco JS syntax if Node.js exists
- verify no packaging files changed
- verify no release artifacts changed

## Packaging checklist

Do not change packaging until after core runtime helper tests are stable.

Before packaging work, verify:

- core language packs are included in standalone builds
- standalone runtime can locate core packs
- app still starts if core packs are missing
- app still starts if one pack is invalid
- app remains local-first

## Rollback checklist

Core runtime source switching must be reversible in one PR.

Rollback should not require:

- database migration
- user settings migration
- release asset changes
- packaging migration
- license changes

## PR checklist for future implementation

A future core runtime implementation PR should state:

- exact files touched
- whether runtime source changed
- fallback order
- tests added
- validation commands run
- packaging unchanged confirmation
- rollback approach

## Decision for this milestone

For v0.2.21-public-beta-language-pack-core-runtime-plan, this checklist is documentation only.

No runtime files should be changed.
