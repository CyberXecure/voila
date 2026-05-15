# Voila! Language Pack Core Promotion Plan

Milestone: v0.2.19-public-beta-language-pack-core-promotion-plan  
Status: core promotion planning only  
Scope: documentation only, no runtime changes, no packaging changes, no licensing changes

## Goal

This milestone defines the plan for promoting Voila! language packs from sample files to future core language packs.

The goal is to prepare a stable structure for production-ready public language packs without changing runtime behavior yet.

## Non-goals

This milestone does not:

- move sample files into a core directory
- modify the application runtime
- change OCR Monaco UI behavior
- add a language selector
- change standalone packaging
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- add external dependencies

## Current state

Current language pack assets include:

- language-packs/schema/language-pack.schema.json
- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json
- language-packs/runtime/minimal_language_runtime.py

Current validation and smoke tools include:

- scripts/language-packs/validate-language-packs.py
- scripts/language-packs/test_language_pack_runtime.py
- scripts/language-packs/test_minimal_language_runtime.py
- scripts/language-packs/smoke-ui-language-endpoint.py

Current UI proof includes language-pack-style aliases in:

- services/api/i18n.py
- services/api/static/ocr_review_monaco.js

## Why promote from samples to core

Sample packs are useful for schema demonstration and tests.

Core packs should be used later as real bundled language resources.

The promotion should happen only when:

- schema is stable enough
- validator passes
- smoke tests pass
- key naming is reviewed
- fallback behavior is documented
- packaging strategy is clear

## Recommended future core structure

Recommended future structure:

language-packs/
  core/
    ro.language-pack.json
    en.language-pack.json
    fr.language-pack.json
    de.language-pack.json
    ru.language-pack.json
    it.language-pack.json
    es.language-pack.json
    pt.language-pack.json

  samples/
    ro.language-pack.sample.json
    en.language-pack.sample.json

  schema/
    language-pack.schema.json

  runtime/
    minimal_language_runtime.py

## Initial core promotion strategy

The first core promotion should be conservative.

Recommended first core packs:

- ro.language-pack.json
- en.language-pack.json

Do not promote all languages at once.

French, German, Russian, Italian, Spanish, and Portuguese should remain planned until their packs are reviewed.

## What should be promoted first

The first core packs should include:

- manifest
- ui
- messages
- feedback
- glossary

Initial keys should come from the reviewed sample packs.

Do not include possible-pro keys in public core packs.

## What should stay in samples

Samples should remain small and useful for documentation.

Samples may continue to demonstrate:

- placeholder usage
- schema shape
- fallback behavior
- minimal translation maps

Samples should not become the only runtime source forever.

## Core pack naming

Recommended names:

- ro.language-pack.json
- en.language-pack.json

Avoid:

- ro.json
- romanian.json
- language-ro.json
- production-ro.json

The name should make the file purpose obvious.

## Manifest policy

When promoted to core, manifest status should move from review to ready only after manual review.

Possible transition:

sample pack:

status = review

core pack draft:

status = review

core pack after review:

status = ready

## Runtime source policy

For the first runtime integration, samples may continue to be used.

Before public production language pack support, runtime should switch from:

language-packs/samples/

to:

language-packs/core/

This switch should be done in a separate milestone with tests.

## Packaging policy

Core language packs must eventually be included in standalone builds.

However, this milestone does not change packaging.

Packaging should be handled only after:

- core path exists
- validator supports core path
- runtime can load core packs
- smoke tests pass locally

## Validator policy

Future validator should support both:

- language-packs/samples/*.language-pack.sample.json
- language-packs/core/*.language-pack.json

The validator should report which group it validated.

Core validation should be stricter than sample validation.

## Smoke test policy

Future smoke tests should verify:

- samples still validate
- core packs validate
- UI aliases still resolve
- fallback remains stable
- no missing placeholders
- no invalid language codes

## Public vs Pro boundary

Public core packs may include:

- basic UI labels
- generic operational messages
- generic learning feedback
- generic glossary terms

Do not include in public core packs yet:

- advanced teacher feedback
- specialized technical dictionaries
- legal/medical/enterprise packs
- commercial templates
- paid/pro unlock logic

## Risk control

Main risks:

- samples accidentally become production source without review
- packaging misses core packs
- runtime path changes break standalone
- all languages are promoted too early
- unreviewed translations become public
- paid/pro content leaks into public packs

Mitigation:

- promote only ro/en first
- keep samples
- validate before and after promotion
- do not change packaging in the same milestone
- keep runtime fallback safe
- keep PRs small

## Recommended next milestone

v0.2.20-public-beta-language-pack-core-promotion

Suggested next work:

- create language-packs/core/
- copy ro/en sample packs into core pack names
- keep samples unchanged
- update validator to include core packs
- add tests for core pack loading
- avoid packaging changes

## Decision for this milestone

For v0.2.19-public-beta-language-pack-core-promotion-plan, the correct action is to document the core promotion strategy only.

No files should be moved into core in this milestone.
