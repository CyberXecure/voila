# Voila! Language Pack Validation

Milestone: v0.2.8-public-beta-language-pack-validator  
Status: local validation tooling / documentation only  
Scope: no runtime changes, no packaging changes, no licensing changes

## Goal

This milestone adds a local validation script for Voila! language pack sample files.

The validator is intentionally simple and safe. It uses only the Python standard library and does not affect the application runtime.

## Non-goals

This milestone does not:

- modify the application runtime
- load language packs in the app
- add a language selector
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- change standalone packaging
- add external Python dependencies

## Files added in this milestone

This milestone adds:

- docs/language-packs/LANGUAGE-PACK-VALIDATION.md
- scripts/language-packs/validate-language-packs.py

## What the validator checks

The validator checks:

- schema JSON parses successfully
- sample language pack JSON files parse successfully
- required top-level sections exist
- required manifest fields exist
- supported language codes are used
- language code matches the sample filename prefix
- status values are valid
- fallback values are valid
- version format is valid
- last_updated format is valid
- translation sections are flat string maps
- translation keys follow the expected key format
- placeholders are preserved across matching keys

## Supported sample path

The validator currently checks files matching:

language-packs/samples/*.language-pack.sample.json

## Required sections

Each language pack must include:

- manifest
- ui
- messages
- feedback
- glossary

## Placeholder policy

Placeholders use the format:

{placeholder_name}

Example:

Lesson {current} of {total}

The Romanian equivalent must preserve the same placeholders:

Lecția {current} din {total}

The validator compares placeholders across matching keys and reports errors when they differ.

## Run command

From the repository root:

pwsh command:

python .\scripts\language-packs\validate-language-packs.py

## Expected result

If all checks pass, the script exits with code 0 and prints:

Language pack validation passed.

If validation fails, the script exits with code 1 and prints the detected errors.

## Security note

The validator treats language packs as data only.

It does not execute language pack content.

## Recommended next milestone

v0.2.9-public-beta-language-pack-review

Suggested next work:

- review candidate inventory
- define final translation keys
- reduce false positives
- decide which strings become public language pack keys
- keep runtime unchanged until key review is stable

## Decision for this milestone

For v0.2.8-public-beta-language-pack-validator, the correct action is to add validation documentation and a local validation script only.

No application runtime files should be modified.
