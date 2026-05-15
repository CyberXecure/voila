# Voila! Language Pack Runtime Minimal Integration Plan

Milestone: v0.2.14-public-beta-language-pack-runtime-minimal-integration-plan  
Status: minimal runtime integration plan / documentation only  
Scope: no application runtime changes, no UI changes, no packaging changes, no licensing changes

## Goal

This milestone defines the safest first runtime integration step for Voila! language packs.

The goal is to decide exactly what should be integrated first, where the integration should happen, how fallback should work, and how to roll back if needed.

This milestone does not implement runtime localization.

## Non-goals

This milestone does not:

- modify the Voila! application runtime
- replace UI strings
- add a language selector
- change standalone packaging
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- add external dependencies

## Context

Previous milestones established:

- language pack plan
- supported languages
- language inventory
- schema
- sample packs
- validation script
- key review
- expanded samples
- runtime integration plan
- runtime scaffold
- runtime scaffold tests

The next implementation milestone should be small and reversible.

## Minimal integration principle

Do not localize the whole app at once.

The first runtime integration should:

- touch as few app files as possible
- use a small stable key subset
- keep existing fallback text
- avoid wide refactors
- avoid changing data models
- avoid changing packaging
- avoid changing release artifacts
- be easy to revert

## Recommended first implementation scope

The first implementation should add a minimal language helper and use it in one safe area only.

Recommended first target:

- application title/subtitle or a small non-critical UI area
- no business logic
- no document processing logic
- no export logic
- no installer/standalone logic

Recommended first keys:

- app.title
- app.subtitle
- button.start
- button.cancel
- button.save
- button.export
- status.ready
- status.processing

Do not integrate all sample keys in the first runtime implementation.

## Recommended first files to add

Potential new files:

- src/i18n/language-packs.ts
- src/i18n/translate.ts
- src/i18n/defaults.ts

Exact paths must be adapted to the current Voila! runtime structure.

If the app structure differs, choose the smallest equivalent location.

## Recommended first files to avoid

Avoid touching:

- PDF processing logic
- OCR/runtime pipeline
- packaging scripts
- release scripts
- installer/shortcut logic
- standalone runtime startup scripts
- security hardening files
- monetization/commercial positioning docs
- validated release artifacts

## Runtime helper behavior

The helper should expose one simple function:

translate(key, options)

Expected behavior:

1. Try selected language.
2. Fall back to English.
3. Fall back to Romanian.
4. Fall back to caller-provided default text.
5. Fall back to the key itself only as a last resort.

## Selected language policy

For the first runtime implementation, do not add a full language selector.

Recommended first approach:

- hardcode default selected language for development testing, or
- read from a local constant, or
- read from an existing local setting only if one already exists

Avoid:

- accounts
- cloud sync
- remote config
- license-based language unlock
- paid/pro gating
- automatic downloads

## Language pack source policy

For first integration, use local bundled files only.

Recommended source:

language-packs/samples/

Later, samples may be promoted to:

language-packs/core/

Do not load remote language packs.

## Fallback policy

Fallback order:

1. selected language
2. en
3. ro
4. default text provided by caller
5. key

The app must never crash because a translation is missing.

## Placeholder policy

Placeholders must remain explicit.

Example:

lesson.progress

English:

Lesson {current} of {total}

Romanian:

Lecția {current} din {total}

Runtime replacement must preserve missing placeholders instead of crashing.

Example:

Input:

Lesson {current} of {total}

Provided:

current = 2

Output:

Lesson 2 of {total}

## Error handling policy

Translation failure must not block app startup.

If language pack loading fails:

- ignore the invalid pack
- use fallback language
- optionally log a developer-safe warning
- show normal UI with fallback text

User-facing error is not required for the first minimal integration.

## Test requirements before implementation

Before the first implementation PR, these commands must pass:

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\preview-language-pack-runtime.py --language ro --key lesson.progress --current 2 --total 10
python .\scripts\language-packs\preview-language-pack-runtime.py --language en --key lesson.progress --current 2 --total 10
python .\scripts\language-packs\preview-language-pack-runtime.py --language fr --key button.save

## Test requirements after implementation

After minimal runtime integration, verify:

- app starts normally
- no startup crash
- default language displays expected text
- fallback text appears when a key is missing
- validator still passes
- scaffold tests still pass
- existing public beta release artifacts are untouched
- packaging files are untouched unless explicitly planned later

## Rollback policy

The first runtime implementation must be easy to revert.

Rollback should be possible by reverting one PR.

Do not spread translation calls across the whole app in the first implementation.

## Risk control

Main risks:

- app startup fails because language files are missing
- packaged app cannot find language files
- UI strings become inconsistent
- missing placeholders break messages
- integration touches too many files
- fallback order is unclear
- runtime starts depending on sample files too strongly

Mitigation:

- keep first integration tiny
- keep fallback defaults in code
- keep language files optional
- do not remove existing hardcoded strings yet
- test before and after
- avoid packaging changes

## Recommended next milestone

v0.2.15-public-beta-language-pack-minimal-runtime-helper

Suggested next work:

- add minimal app-side translation helper
- use a very small key subset
- keep runtime fallback text
- no language selector yet
- no full UI localization yet
- no packaging changes yet

## Decision for this milestone

For v0.2.14-public-beta-language-pack-runtime-minimal-integration-plan, the correct action is to document the minimal integration plan only.

No application runtime files should be modified.
