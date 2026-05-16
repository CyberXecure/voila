# Voila! Language Pack Packaging Plan Checklist

Milestone: v0.2.26-public-beta-language-pack-packaging-plan
Status: packaging planning checklist
Scope: documentation only; no packaging changes, no runtime changes, no UI changes, no licensing changes

## Goal

This checklist defines go/no-go conditions before changing standalone packaging for language packs.

## Go criteria

Packaging work can begin only if:

- main branch is clean
- no unrelated PRs are open
- language pack validator passes
- runtime tests pass
- UI smoke test passes
- core runtime smoke test passes
- language pack file smoke test passes
- core ro/en packs exist
- schema exists
- runtime source policy is documented

## No-go criteria

Do not modify packaging if:

- working tree is dirty
- validator fails
- smoke tests fail
- packaged path strategy is unclear
- runtime fallback is unclear
- changes would touch v0.2.0-public-beta release assets
- changes require LICENSE updates
- changes mix packaging with broad UI localization

## Required pre-check commands

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python .\scripts\language-packs\smoke-language-pack-files.py
python -m py_compile .\services\api\i18n.py

Optional:

node --check .\services\api\static\ocr_review_monaco.js

## Future packaging PR checklist

A future packaging PR should clearly state:

- files added to packaged output
- source directories copied
- destination directories used
- whether samples are included
- validation commands run
- manual packaged smoke test result
- rollback approach

## Files that should be considered

Required future packaged data:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

Optional future packaged data:

- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json

## Decision for this milestone

For v0.2.26-public-beta-language-pack-packaging-plan, this checklist is documentation only.

No packaging scripts should be changed.
