# Voila! Language Pack Runtime Tests

Milestone: v0.2.13-public-beta-language-pack-runtime-tests  
Status: isolated runtime scaffold tests  
Scope: no application runtime integration, no UI changes, no packaging changes, no licensing changes

## Goal

This milestone adds isolated tests for the Voila! language pack runtime scaffold.

The tests verify the standalone Python scaffold added in:

- scripts/language-packs/language_pack_runtime.py
- scripts/language-packs/preview-language-pack-runtime.py

The scaffold remains disconnected from the Voila! application runtime.

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

- docs/language-packs/LANGUAGE-PACK-RUNTIME-TESTS.md
- scripts/language-packs/test_language_pack_runtime.py

## What the tests cover

The tests cover:

- loading sample language packs
- available languages
- Romanian translation lookup
- English translation lookup
- fallback from unsupported language to English
- fallback default text for missing keys
- placeholder substitution
- preserving missing placeholders
- direct runtime lookup
- glossary key lookup

## Commands

Run the existing validator:

python .\scripts\language-packs\validate-language-packs.py

Run the runtime scaffold tests:

python .\scripts\language-packs\test_language_pack_runtime.py

Run preview checks manually:

python .\scripts\language-packs\preview-language-pack-runtime.py --language ro --key lesson.progress --current 2 --total 10
python .\scripts\language-packs\preview-language-pack-runtime.py --language en --key lesson.progress --current 2 --total 10
python .\scripts\language-packs\preview-language-pack-runtime.py --language fr --key button.save

## Expected results

Validator:

Language pack validation passed.

Runtime tests:

OK

Preview:

Lecția 2 din 10  
Lesson 2 of 10  
Save

## Safety

The tests use only Python standard library.

The tests do not import the Voila! application.

The tests do not modify sample packs.

The tests do not access remote resources.

## Recommended next milestone

v0.2.14-public-beta-language-pack-runtime-minimal-integration-plan

Suggested next work:

- decide exact app files to integrate first
- keep first integration very small
- use only a few stable keys
- define rollback commands
- do not localize the full UI at once

## Decision for this milestone

For v0.2.13-public-beta-language-pack-runtime-tests, the correct action is to add isolated scaffold tests only.

No application runtime files should be modified.
