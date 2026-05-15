# Voila! Minimal Language Pack Runtime Helper

Milestone: v0.2.15-public-beta-language-pack-minimal-runtime-helper  
Status: minimal runtime helper / no UI integration  
Scope: no UI replacement, no language selector, no packaging changes, no licensing changes

## Goal

This milestone adds a minimal runtime helper for language pack lookup and fallback behavior.

The helper is intentionally small and isolated. It is not wired into the Voila! UI yet.

## Non-goals

This milestone does not:

- replace UI strings
- add a language selector
- change standalone packaging
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- add external dependencies
- localize the whole app

## Files added in this milestone

This milestone adds:

- docs/language-packs/LANGUAGE-PACK-MINIMAL-RUNTIME-HELPER.md
- language-packs/runtime/minimal_language_runtime.py
- scripts/language-packs/test_minimal_language_runtime.py

## Design

The helper uses only the Python standard library.

It supports:

- local language pack loading
- safe fallback order
- translation lookup
- caller-provided default text
- placeholder replacement
- missing placeholder preservation
- invalid or missing language pack tolerance

## Fallback order

The fallback order is:

1. selected language
2. English en
3. Romanian ro
4. caller-provided default text
5. key

The helper must never crash the app because a translation key is missing.

## Placeholder behavior

Example:

Lesson {current} of {total}

If values are provided:

current = 2  
total = 10

Output:

Lesson 2 of 10

If total is missing:

Lesson 2 of {total}

Missing placeholders are preserved rather than causing a crash.

## Why no UI integration yet

This milestone adds the helper only.

UI integration should happen in a later milestone after this helper is tested and reviewed.

The first UI integration should use only a very small key subset.

## Validation commands

Run from repository root:

python .\scripts\language-packs\validate-language-packs.py
python .\scripts\language-packs\test_language_pack_runtime.py
python .\scripts\language-packs\test_minimal_language_runtime.py

## Safety

This helper:

- does not execute language pack content
- does not load remote language packs
- does not require network access
- does not add dependencies
- does not change packaging
- does not modify release artifacts

## Recommended next milestone

v0.2.16-public-beta-language-pack-minimal-ui-proof

Suggested next work:

- integrate only 3-5 safe UI keys
- keep fallback strings inline
- avoid language selector
- verify app startup
- verify standalone remains unaffected
- keep rollback simple

## Decision for this milestone

For v0.2.15-public-beta-language-pack-minimal-runtime-helper, the correct action is to add the minimal helper and isolated tests only.

No UI strings should be replaced in this milestone.
