# Voila! Language Pack Runtime Scaffold

Milestone: v0.2.12-public-beta-language-pack-runtime-scaffold  
Status: isolated runtime scaffold / no app integration  
Scope: no application runtime integration, no UI changes, no packaging changes, no licensing changes

## Goal

This milestone adds an isolated language pack runtime scaffold for Voila!.

The scaffold demonstrates how language packs can be loaded, validated at a basic level, and queried with fallback behavior.

It is intentionally not connected to the application runtime yet.

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

## Files added in this milestone

This milestone adds:

- docs/language-packs/LANGUAGE-PACK-RUNTIME-SCAFFOLD.md
- scripts/language-packs/language_pack_runtime.py
- scripts/language-packs/preview-language-pack-runtime.py

## Design

The scaffold is implemented as standalone Python tooling using only the Python standard library.

It can:

- load sample language packs from language-packs/samples
- read manifest metadata
- flatten translation sections
- translate a key
- apply placeholder values
- fall back safely when a key is missing
- avoid crashing when a selected language is unavailable

## Fallback order

The scaffold uses this fallback order:

1. selected language
2. English en
3. Romanian ro
4. internal safe default

## Example

Command:

python .\scripts\language-packs\preview-language-pack-runtime.py --language ro --key lesson.progress --current 2 --total 10

Expected output:

Lecția 2 din 10

Command:

python .\scripts\language-packs\preview-language-pack-runtime.py --language en --key lesson.progress --current 2 --total 10

Expected output:

Lesson 2 of 10

## Safety

This scaffold is not imported by the app.

It does not change UI behavior.

It does not introduce dependencies.

It does not load remote language packs.

It does not execute language pack content.

## Validation

Before using this scaffold, run:

python .\scripts\language-packs\validate-language-packs.py

Expected result:

Language pack validation passed.

## Recommended next milestone

v0.2.13-public-beta-language-pack-runtime-tests

Suggested next work:

- add isolated tests for the runtime scaffold
- test fallback behavior
- test missing keys
- test placeholder replacement
- keep application runtime untouched until scaffold tests pass

## Decision for this milestone

For v0.2.12-public-beta-language-pack-runtime-scaffold, the correct action is to add an isolated runtime scaffold only.

No application runtime files should be modified.
