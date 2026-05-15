# Voila! Language Pack Sample Expansion

Milestone: v0.2.10-public-beta-language-pack-sample-expansion  
Status: expanded sample language packs / documentation only  
Scope: no runtime changes, no packaging changes, no licensing changes

## Goal

This milestone expands the Romanian and English sample language packs using the stable draft key subset defined in:

- docs/language-packs/TRANSLATION-KEYS-DRAFT.md
- docs/language-packs/LANGUAGE-PACK-KEY-REVIEW.md

The purpose is to make the sample packs more realistic before any runtime localization work begins.

## Non-goals

This milestone does not:

- modify the application runtime
- load language packs in the app
- add a language selector
- add complete translations for every detected string
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- change standalone packaging
- add external dependencies

## Files changed in this milestone

This milestone changes:

- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json

This milestone adds:

- docs/language-packs/LANGUAGE-PACK-SAMPLE-EXPANSION.md

## Expansion policy

The sample packs are expanded conservatively.

Only generic, reusable, user-facing keys are added.

The sample packs still remain examples. They are not full production translations.

## Expanded sections

The following sections are expanded:

- ui
- messages
- feedback
- glossary

## Placeholder-bearing keys

The expanded samples include placeholder-bearing keys:

- lesson.progress
- message.items_processed
- message.exported_lessons
- error.field_required

The placeholders must match across Romanian and English.

Required placeholders:

| Key | Placeholders |
|---|---|
| lesson.progress | {current}, {total} |
| message.items_processed | {count} |
| message.exported_lessons | {count} |
| error.field_required | {field} |

## Validation

After this milestone, the validator should pass:

python .\scripts\language-packs\validate-language-packs.py

Expected result:

Language pack validation passed.

## Safety

This milestone is sample-data only.

No runtime localization should be implemented here.

## Recommended next milestone

v0.2.11-public-beta-language-pack-runtime-plan

Suggested next work:

- document minimal runtime integration plan
- define selected-language storage policy
- define fallback behavior in runtime
- define test plan
- still avoid implementation until the plan is reviewed

## Decision for this milestone

For v0.2.10-public-beta-language-pack-sample-expansion, the correct action is to expand the sample language pack files and document the expansion.

No application runtime files should be modified.
