# Voila! Language Pack Core Promotion Checklist

Milestone: v0.2.19-public-beta-language-pack-core-promotion-plan  
Status: pre-promotion checklist  
Scope: documentation only, no runtime changes, no packaging changes, no licensing changes

## Goal

This checklist defines the conditions required before sample language packs can be promoted to core language packs.

## Go criteria

Core promotion can begin only if:

- main branch is clean
- no unrelated PRs are open
- language pack validator passes
- runtime scaffold tests pass
- minimal runtime helper tests pass
- UI smoke test passes
- i18n.py compiles
- OCR Monaco JS syntax check passes if Node.js is available
- ro/en samples are reviewed
- fallback behavior is documented
- packaging impact is deferred or planned separately

## No-go criteria

Do not promote to core if:

- working tree is dirty
- validator fails
- smoke test fails
- UI aliases are unstable
- runtime still depends only on samples without a plan
- packaging changes are required immediately
- translations are unreviewed
- possible-pro content is mixed into public packs
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

## Recommended first core files

First promotion should create only:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json

Do not create all eight core packs in the first promotion milestone.

## Files to avoid changing during first promotion

Avoid changing:

- OCR processing files
- PDF processing files
- export logic
- packaging scripts
- release scripts
- installer scripts
- security policy
- monetization docs
- v0.2.0-public-beta release assets

## Validator update checklist

When core packs are introduced, validator should check:

- samples path
- core path
- schema JSON parse
- all core JSON files parse
- required sections exist
- language codes match filenames
- fallback values are valid
- placeholders are preserved
- translation keys follow naming rules

## Runtime update checklist

Do not switch runtime to core packs until:

- core files exist
- validator supports core path
- tests cover core path
- fallback behavior is unchanged
- sample tests still pass

## Packaging checklist

Do not change packaging during first core promotion unless explicitly planned.

Before packaging integration, verify:

- core packs are included in standalone package
- app can locate core packs in packaged mode
- app still starts if core packs are missing
- fallback still works
- no internet access is required

## Manual review checklist for ro/en

Before ro/en are considered ready:

- manifest status is correct
- native names are correct
- placeholders are preserved
- UI text is natural
- tooltips are natural
- feedback messages are useful
- glossary terms are consistent
- no private data exists
- no paid/pro-only content exists

## PR checklist for future core promotion

The future core promotion PR should include:

- exact files created
- validation commands run
- confirmation samples remain unchanged
- confirmation runtime source is unchanged unless explicitly planned
- confirmation packaging is unchanged
- rollback note

## Rollback policy

Core promotion must be reversible in one PR.

Rollback should not require:

- database migration
- settings migration
- packaging migration
- release artifact changes

## Decision for this milestone

For v0.2.19-public-beta-language-pack-core-promotion-plan, this checklist is documentation only.

No core files should be created in this milestone.
