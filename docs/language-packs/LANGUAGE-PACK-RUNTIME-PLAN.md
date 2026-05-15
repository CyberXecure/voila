# Voila! Language Pack Runtime Plan

Milestone: v0.2.11-public-beta-language-pack-runtime-plan  
Status: runtime integration plan / documentation only  
Scope: no runtime changes, no packaging changes, no licensing changes

## Goal

This milestone defines a safe runtime integration plan for Voila! language packs.

The purpose is to prepare implementation without changing application behavior yet.

## Non-goals

This milestone does not:

- modify the application runtime
- load language packs in the app
- add a language selector
- change standalone packaging
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- add external dependencies

## Context

Previous Language Pack milestones established:

- language pack strategy
- supported languages
- translation inventory
- schema
- sample ro/en packs
- validator
- translation key review
- expanded sample packs

This milestone turns those into a safe runtime implementation plan.

## Runtime integration principles

The runtime implementation should be:

- local-first
- deterministic
- optional
- fallback-safe
- testable
- reversible
- compatible with standalone packaging
- safe when language files are missing or invalid

The application must continue to work even if no language pack is loaded.

## Minimal first runtime target

The first runtime implementation should use only a small stable key subset.

Recommended first keys:

- app.title
- app.subtitle
- button.start
- button.cancel
- button.save
- button.export
- status.ready
- status.processing
- message.saved
- message.export_complete
- message.file_loaded
- warning.unsaved_changes
- error.file_not_supported
- lesson.progress
- feedback.correct
- feedback.try_again
- term.lesson
- term.exercise
- term.translation

Do not integrate all draft keys at once.

## Recommended runtime architecture

The runtime integration should use a small translation helper.

Conceptual behavior:

1. Load bundled default language pack.
2. Validate expected structure.
3. Read selected language setting if available.
4. Load selected language pack if present.
5. Fall back safely if a key is missing.
6. Return internal default text if all fallbacks fail.

## Recommended fallback order

Fallback order:

1. selected language
2. English en
3. Romanian ro
4. internal safe default

The app must never crash because of a missing translation key.

## Selected language storage

Recommended first approach:

- store selected language locally
- avoid cloud sync
- avoid remote profile dependency
- use a simple local setting
- default to English or Romanian, depending on current app behavior

Do not introduce accounts, licensing, or remote settings for this milestone family.

## Runtime loading policy

Language packs should be loaded from local bundled files first.

Recommended initial runtime source:

language-packs/samples/

Later this may become:

language-packs/core/

Do not load remote language packs in the first runtime implementation.

## Validation policy

Before a language pack is used at runtime:

- JSON must parse
- required sections must exist
- manifest must be valid
- language_code must be supported
- translation sections must be flat string maps
- placeholders must be preserved

If validation fails, the app should ignore the invalid pack and use fallback language.

## Error handling policy

Runtime language errors should be user-safe.

Developer logs may mention:

- missing key
- invalid pack
- fallback used
- unsupported language code

User-facing errors should stay simple.

Example:

The selected language could not be loaded. The app is using the default language.

## Packaging policy

Standalone packaging must remain stable.

Before implementation, verify:

- bundled language files are included
- validator still passes
- startup works without language pack files
- startup works with invalid language pack ignored
- no runtime dependency is introduced accidentally

## Public vs Pro boundary

Runtime should initially support public bundled packs only.

Do not implement:

- paid language unlock
- license checks
- remote entitlement checks
- subscription logic
- marketplace logic

Possible Pro language packs can be planned later, after the public runtime is stable.

## Security policy

Language packs are data only.

Runtime must not:

- execute language pack content
- evaluate expressions from translations
- load scripts from packs
- fetch packs remotely by default
- allow path traversal
- expose secrets in translations

## Implementation phases

### Phase 1 - Plan only

Current milestone: v0.2.11-public-beta-language-pack-runtime-plan

Deliverables:

- runtime integration plan
- runtime test plan
- no application changes

### Phase 2 - Minimal translation helper

Future milestone.

Tasks:

- add a small translation helper
- load bundled ro/en sample packs
- implement fallback
- keep UI changes minimal

### Phase 3 - Minimal UI integration

Future milestone.

Tasks:

- replace only a small number of stable strings
- do not localize everything
- keep rollback simple
- test standalone packaging

### Phase 4 - Language selector

Future milestone.

Tasks:

- add simple language selector
- store selected language locally
- validate fallback behavior

### Phase 5 - Expanded language packs

Future milestone.

Tasks:

- add fr, de, ru, it, es, pt samples or packs
- validate all packs
- keep community contribution process clear

## Files expected in first implementation milestone

Potential future runtime files may include:

- src/i18n/translator
- src/i18n/load-language-pack
- src/i18n/defaults
- src/i18n/types

Exact paths should be chosen only after reviewing the current runtime structure.

## Decision for this milestone

For v0.2.11-public-beta-language-pack-runtime-plan, the correct action is to document the runtime integration plan only.

No application runtime files should be modified.
