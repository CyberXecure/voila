# Voila! Language Pack Plan

Milestone: v0.2.4-public-beta-language-pack-plan  
Status: planning / documentation only  
Scope: no runtime changes, no licensing changes, no changes to the validated public beta release

## Goal

The goal of this milestone is to define a pragmatic Language Pack strategy for Voila! without changing the validated runtime.

This milestone prepares the project for future localization work, community contributions, and possible commercial language features, while keeping the current public beta stable.

## Non-goals for this milestone

This milestone does not:

- modify the validated v0.2.0-public-beta release
- change the application runtime
- introduce new dependencies
- change packaging or standalone behavior
- add a LICENSE
- add paid/pro logic to the application
- require external services or API keys

## Initial supported language set

| Language | Code | Status |
|---|---:|---|
| Romanian | ro | planned core language |
| English | en | planned core language |
| French | fr | planned language pack |
| German | de | planned language pack |
| Russian | ru | planned language pack |
| Italian | it | planned language pack |
| Spanish | es | planned language pack |
| Portuguese | pt | planned language pack |

## Strategy

Voila! should treat languages as structured resources, not as hardcoded text scattered through the app.

Recommended strategy:

1. Keep the current runtime stable.
2. Document the language model first.
3. Introduce language packs later behind small, testable changes.
4. Start with simple JSON-based packs.
5. Validate language packs before loading them.
6. Keep the public beta usable even if a translation is incomplete.
7. Use fallback rules so missing text does not break the app.

## Public repository content

The public repository can safely include:

- supported language list
- language pack plan
- future language pack schema
- sample language pack files
- public translation guidelines
- contribution instructions
- validation rules
- non-commercial community translations
- basic UI strings
- generic user-facing messages
- generic educational labels and explanations

Public repo content should avoid:

- paid feature enforcement logic
- private commercial roadmap details
- license activation logic
- private prompts intended for commercial differentiation
- API keys or provider-specific secrets
- customer-specific terminology
- private datasets

## Possible future Pro / paid content

The following can become Pro or paid later, but is not implemented in this milestone:

- premium language packs
- specialized terminology packs
- domain-specific educational packs
- advanced teacher / tutor templates
- batch translation workflows
- export templates per language
- commercial dictionaries
- professionally reviewed translations
- priority updates for paid language packs
- enterprise/custom language packs

Important: this milestone only documents the possibility. It does not add monetization logic.

## Future file structure

Recommended future structure:

docs/
  language-packs/
    LANGUAGE-PACK-PLAN.md
    SUPPORTED-LANGUAGES.md
    LANGUAGE-PACK-SCHEMA.md
    CONTRIBUTING-TRANSLATIONS.md

language-packs/
  schema/
    language-pack.schema.json

  ro/
    manifest.json
    ui.json
    messages.json
    feedback.json
    glossary.json

  en/
    manifest.json
    ui.json
    messages.json
    feedback.json
    glossary.json

  fr/
    manifest.json
    ui.json
    messages.json
    feedback.json
    glossary.json

  de/
    manifest.json
    ui.json
    messages.json
    feedback.json
    glossary.json

  ru/
    manifest.json
    ui.json
    messages.json
    feedback.json
    glossary.json

  it/
    manifest.json
    ui.json
    messages.json
    feedback.json
    glossary.json

  es/
    manifest.json
    ui.json
    messages.json
    feedback.json
    glossary.json

  pt/
    manifest.json
    ui.json
    messages.json
    feedback.json
    glossary.json

This structure is intentionally documented only. It is not added in this milestone, to avoid risky runtime changes.

## Recommended language pack files

Each future language pack should contain:

### manifest.json

Metadata about the language pack.

Suggested fields:

- language_code
- language_name
- native_name
- version
- status
- author
- fallback
- last_updated

### ui.json

General app interface labels:

- buttons
- menus
- navigation labels
- status labels
- empty states

### messages.json

User-facing messages:

- success messages
- warnings
- validation messages
- import/export messages
- runtime status messages

### feedback.json

Learning and correction feedback:

- correct answer feedback
- error explanations
- grammar hints
- encouragement messages

### glossary.json

Stable terminology:

- PDF
- lesson
- exercise
- translation
- grammar
- vocabulary
- feedback

## Fallback policy

Recommended fallback order:

1. selected language
2. English en
3. Romanian ro
4. internal safe default

The app should never crash because of a missing translation key.

Missing translations should be visible during development, but non-breaking for users.

## Quality policy

A language pack should be considered ready only when:

- all required keys exist
- JSON files are valid
- placeholders are preserved
- terminology is consistent
- UI text fits reasonably well
- feedback messages are natural and useful
- no machine-translation artifacts are obvious
- no sensitive or private data is included

## Placeholder policy

Language packs must preserve placeholders exactly.

Example key:

lesson.progress

Example value:

Lesson {current} of {total}

The translated value must keep:

- {current}
- {total}

## Versioning policy

Language packs should follow the app version where they were introduced or updated.

Example:

Voila app: v0.2.x  
Language pack: ro-v0.2.x

Future paid packs may use separate versioning, but must remain compatible with the public schema.

## Recommended implementation phases

### Phase 1 - Documentation only

Current milestone: v0.2.4-public-beta-language-pack-plan

Deliverables:

- language pack strategy
- supported language list
- future structure
- public vs paid boundary

### Phase 2 - Translation inventory

Future milestone.

Tasks:

- identify hardcoded user-facing text
- group strings by category
- define translation keys
- decide fallback behavior

### Phase 3 - Schema and sample packs

Future milestone.

Tasks:

- add JSON schema
- add sample ro and en packs
- add validation script
- keep runtime unchanged or minimally touched

### Phase 4 - Runtime integration

Future milestone.

Tasks:

- load selected language safely
- add fallback handling
- add tests
- keep standalone packaging stable

### Phase 5 - Community and Pro split

Future milestone.

Tasks:

- document public contribution flow
- decide which packs remain public
- decide what becomes Pro
- avoid adding paid enforcement until the product model is clear

## Security and stability notes

Language packs should be treated as data, not executable code.

Future runtime implementation should:

- load only JSON files
- validate schema before use
- reject unexpected file types
- avoid executing language pack content
- avoid remote loading by default
- avoid downloading packs automatically without user consent
- keep all local-first guarantees intact

## Decision for this milestone

For v0.2.4-public-beta-language-pack-plan, the correct action is to commit documentation only.

No application runtime files should be modified.
