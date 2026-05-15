# Voila! Language Pack Schema

Milestone: v0.2.6-public-beta-language-pack-schema  
Status: schema definition / documentation only  
Scope: no runtime changes, no packaging changes, no licensing changes

## Goal

This milestone defines the initial schema for Voila! language packs.

The goal is to create a stable structure for future translations before adding any runtime language loading.

## Non-goals

This milestone does not:

- modify the application runtime
- add language pack loading
- add a language selector
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- change standalone packaging
- introduce external services

## Files added in this milestone

This milestone adds:

- docs/language-packs/LANGUAGE-PACK-SCHEMA.md
- language-packs/schema/language-pack.schema.json

## Relationship with previous milestones

This schema builds on:

- docs/language-packs/LANGUAGE-PACK-PLAN.md
- docs/language-packs/SUPPORTED-LANGUAGES.md
- docs/language-packs/LANGUAGE-PACK-INVENTORY.md

The inventory identifies possible strings.  
The schema defines how future language packs should be structured.

## Supported language codes

The initial supported language codes are:

| Language | Code |
|---|---:|
| Romanian | ro |
| English | en |
| French | fr |
| German | de |
| Russian | ru |
| Italian | it |
| Spanish | es |
| Portuguese | pt |

## Future language pack structure

A future language pack should be represented as a structured object with these sections:

- manifest
- ui
- messages
- feedback
- glossary

The repository may later store these sections as separate files:

language-packs/
  ro/
    manifest.json
    ui.json
    messages.json
    feedback.json
    glossary.json

For schema validation, these sections can also be combined into a single object.

## manifest

The manifest contains metadata about the language pack.

Required fields:

| Field | Purpose |
|---|---|
| language_code | language code, for example ro or en |
| language_name | English language name |
| native_name | native language name |
| version | language pack version |
| status | draft, planned, review, ready, or deprecated |
| fallback | fallback language |
| last_updated | update date in YYYY-MM-DD format |

Optional fields:

| Field | Purpose |
|---|---|
| author | translation author or maintainer |
| notes | internal public notes about the pack |

## ui

The ui section contains general interface labels.

Examples:

- buttons
- menu labels
- navigation labels
- headings
- empty states
- status labels

Recommended key style:

app.title  
button.save  
button.cancel  
nav.settings  
status.ready

## messages

The messages section contains user-facing operational messages.

Examples:

- success messages
- warning messages
- validation messages
- import/export messages
- processing messages
- error messages intended for users

Recommended key style:

message.saved  
message.export_complete  
warning.unsaved_changes  
error.file_not_supported

## feedback

The feedback section contains learning and correction feedback.

Examples:

- correct answer feedback
- mistake explanations
- grammar hints
- encouragement messages
- learning progress feedback

Recommended key style:

feedback.correct  
feedback.try_again  
feedback.grammar_hint  
feedback.progress

## glossary

The glossary section contains stable terminology.

Examples:

- PDF
- lesson
- exercise
- translation
- grammar
- vocabulary
- feedback

Recommended key style:

term.pdf  
term.lesson  
term.exercise  
term.translation

## Placeholder policy

Language packs must preserve placeholders exactly.

Example source value:

Lesson {current} of {total}

The translated value must keep:

- {current}
- {total}

A future validation script should detect missing, renamed, or extra placeholders.

## Fallback policy

Recommended fallback order:

1. selected language
2. English en
3. Romanian ro
4. internal safe default

The app should never crash because a translation key is missing.

## Schema limits

The initial schema validates structure, required sections, language codes, status values, and simple string maps.

The schema does not fully validate semantic translation quality.

The schema does not yet fully validate placeholder consistency across languages. That should be handled by a future validation script.

## Security policy

Language packs must be data only.

Future implementation should:

- load JSON only
- reject executable content
- reject unexpected file types
- validate before use
- avoid remote loading by default
- avoid automatic downloads without user consent
- keep Voila! local-first

## Public vs possible Pro content

The schema is public.

Possible future paid content may include:

- professionally reviewed packs
- specialized terminology packs
- domain-specific learning packs
- commercial dictionaries
- custom enterprise packs

This milestone does not add monetization logic.

## Recommended next milestone

v0.2.7-public-beta-language-pack-samples

Suggested next work:

- add sample ro language pack
- add sample en language pack
- keep samples small
- validate samples against this schema
- avoid runtime changes

## Decision for this milestone

For v0.2.6-public-beta-language-pack-schema, the correct action is to add schema documentation and the JSON schema only.

No application runtime files should be modified.
