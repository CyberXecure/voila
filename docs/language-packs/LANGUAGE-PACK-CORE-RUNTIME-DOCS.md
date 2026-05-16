# Voila! Language Pack Core Runtime Docs

Milestone: v0.2.24-public-beta-language-pack-core-runtime-docs
Status: documentation only
Scope: no runtime changes, no UI changes, no packaging changes, no licensing changes

## Goal

This milestone documents the current state of Voila! language pack runtime support after the core-first helper and smoke test milestones.

## Current state

Current core packs:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json

Current sample packs:

- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json

Current runtime helper:

- language-packs/runtime/minimal_language_runtime.py

## Current runtime behavior

The isolated minimal runtime helper supports:

- core language packs
- sample language packs
- core-first lookup
- sample fallback
- unsupported language fallback
- caller default fallback
- key fallback
- placeholder replacement
- missing placeholder preservation

## Fallback order

1. selected language from core
2. English from core
3. Romanian from core
4. selected language from samples
5. English from samples
6. Romanian from samples
7. caller-provided default text
8. key

## Current validation tools

Run from repository root:

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py
python .\scripts\language-packs\smoke-ui-language-endpoint.py
python .\scripts\language-packs\smoke-core-runtime-helper.py
python -m py_compile .\services\api\i18n.py

Optional, if Node.js is installed:

node --check .\services\api\static\ocr_review_monaco.js

## What is not done yet

- no packaging integration for core packs
- no full runtime switch across the application
- no broad UI localization
- no new language selector
- no paid/pro enforcement
- no external language pack downloads
- no LICENSE addition

## Recommended next milestone

v0.2.25-public-beta-language-pack-packaging-check

## Decision for this milestone

For v0.2.24-public-beta-language-pack-core-runtime-docs, the correct action is documentation only.

Do not change runtime, UI, packaging, or licensing in this milestone.
