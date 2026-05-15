# Voila! Language Pack Samples

Milestone: v0.2.7-public-beta-language-pack-samples  
Status: sample language packs / documentation only  
Scope: no runtime changes, no packaging changes, no licensing changes

## Goal

This milestone adds small sample language packs for Romanian and English.

The samples are intended to demonstrate the structure defined in:

- docs/language-packs/LANGUAGE-PACK-SCHEMA.md
- language-packs/schema/language-pack.schema.json

## Non-goals

This milestone does not:

- modify the application runtime
- add language pack loading
- add a language selector
- add complete translations
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- change standalone packaging

## Files added in this milestone

This milestone adds:

- docs/language-packs/LANGUAGE-PACK-SAMPLES.md
- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json

## Sample scope

The sample packs are intentionally small.

They include examples for:

- manifest metadata
- common UI labels
- user-facing messages
- learning feedback
- glossary terms

They are not full production translations.

## Relationship with previous milestones

This milestone builds on:

- v0.2.4-public-beta-language-pack-plan
- v0.2.5-public-beta-language-pack-inventory
- v0.2.6-public-beta-language-pack-schema

The plan defined the strategy.  
The inventory identified candidate strings.  
The schema defined the structure.  
The samples demonstrate the structure using Romanian and English.

## Sample files

Romanian sample:

language-packs/samples/ro.language-pack.sample.json

English sample:

language-packs/samples/en.language-pack.sample.json

## Validation expectation

At this stage, the samples should:

- be valid JSON
- follow the language pack schema structure
- include manifest, ui, messages, feedback, and glossary sections
- preserve placeholder names exactly
- avoid executable content
- avoid remote references
- avoid secrets or private data

A future milestone should add an automated validation script.

## Placeholder example

The sample packs include:

lesson.progress

The Romanian and English versions both preserve:

- {current}
- {total}

Future validation tooling should ensure placeholders are not removed, renamed, or added incorrectly.

## Security note

Language packs are data only.

They must not include:

- executable code
- scripts
- remote loading instructions
- API keys
- credentials
- private customer data

## Recommended next milestone

v0.2.8-public-beta-language-pack-validator

Suggested next work:

- add a local validation script
- validate sample packs against the JSON schema
- check required sections
- check placeholder preservation
- keep runtime unchanged

## Decision for this milestone

For v0.2.7-public-beta-language-pack-samples, the correct action is to add sample language pack JSON files and this documentation only.

No application runtime files should be modified.
