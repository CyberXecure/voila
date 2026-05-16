# Voila! Language Pack Packaging Plan

Milestone: v0.2.26-public-beta-language-pack-packaging-plan
Status: packaging planning only
Scope: documentation only; no packaging changes, no runtime changes, no UI changes, no licensing changes

## Goal

This milestone defines how Voila! language packs should be included in future standalone packaging.

## Non-goals

This milestone does not:

- modify packaging scripts
- modify release scripts
- modify installer scripts
- modify runtime startup scripts
- change OCR processing
- change PDF processing
- change export behavior
- change UI behavior
- add a language selector
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release

## Current packaging-relevant files

Core language packs:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json

Sample language packs:

- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json

Schema:

- language-packs/schema/language-pack.schema.json

Runtime helper:

- language-packs/runtime/minimal_language_runtime.py

Smoke checks:

- scripts/language-packs/smoke-language-pack-files.py
- scripts/language-packs/smoke-core-runtime-helper.py
- scripts/language-packs/smoke-ui-language-endpoint.py

## Future packaging principle

Language packs should be packaged as data files, not executable logic.

Future standalone builds should include at minimum:

- language-packs/core/
- language-packs/schema/

Samples may be included only if needed for diagnostics, documentation, or fallback testing.

## Recommended future package layout

Recommended packaged layout:

language-packs/
  core/
    ro.language-pack.json
    en.language-pack.json
  schema/
    language-pack.schema.json

Optional diagnostic layout:

language-packs/
  samples/
    ro.language-pack.sample.json
    en.language-pack.sample.json

## Runtime path policy

Future packaged runtime should avoid development-only absolute paths.

Acceptable path sources:

- application base directory
- packaged resources directory
- explicit environment override for testing
- repository root during development

Do not rely on:

- local developer path D:\dev\projects\voila
- user-specific profile paths
- remote URLs
- current working directory alone

## Packaging smoke requirement

Before any future packaging change is merged, this command must pass:

python .\scripts\language-packs\smoke-language-pack-files.py

After packaging changes, a future packaged-mode smoke test should verify:

- core packs exist in the packaged output
- schema exists in the packaged output
- app starts if core packs are present
- app fails safely if language packs are missing
- app does not require internet access for language packs

## Rollback policy

Packaging changes must be reversible in one PR.

Rollback should not require:

- database migration
- user settings migration
- release asset mutation
- license changes
- remote service changes

## Recommended next milestone

v0.2.27-public-beta-language-pack-packaging-scaffold

Suggested next work:

- inspect existing standalone/release packaging scripts
- identify where data files are copied
- add a non-invasive packaging scaffold or checklist
- avoid changing release artifacts until the scaffold is reviewed

## Decision for this milestone

For v0.2.26-public-beta-language-pack-packaging-plan, the correct action is documentation only.

Do not modify packaging in this milestone.
