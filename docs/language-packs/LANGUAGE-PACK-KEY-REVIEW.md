# Voila! Language Pack Key Review

Milestone: v0.2.9-public-beta-language-pack-review  
Status: translation key review / documentation only  
Scope: no runtime changes, no packaging changes, no licensing changes

## Goal

This milestone reviews the previous language pack inventory and defines a safer process for deciding which strings should become stable translation keys.

The goal is to avoid moving every detected string into language packs automatically.

Only clear, user-facing, reusable strings should become language pack keys.

## Non-goals

This milestone does not:

- modify the application runtime
- load language packs in the app
- add a language selector
- add complete translations
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- change standalone packaging
- add external dependencies

## Files added in this milestone

This milestone adds:

- docs/language-packs/LANGUAGE-PACK-KEY-REVIEW.md
- docs/language-packs/TRANSLATION-KEYS-DRAFT.md

## Context

Previous milestones created:

- docs/language-packs/LANGUAGE-PACK-PLAN.md
- docs/language-packs/SUPPORTED-LANGUAGES.md
- docs/language-packs/LANGUAGE-PACK-INVENTORY.md
- docs/language-packs/LANGUAGE-PACK-SCHEMA.md
- docs/language-packs/LANGUAGE-PACK-SAMPLES.md
- docs/language-packs/LANGUAGE-PACK-VALIDATION.md
- language-packs/schema/language-pack.schema.json
- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json
- scripts/language-packs/validate-language-packs.py

The inventory is intentionally broad and may contain false positives.

This review step narrows the inventory into a future stable key list.

## Review principle

Do not translate everything.

Translate only strings that are:

- visible to the user
- stable enough to become public keys
- reusable across the app
- meaningful outside a single implementation detail
- safe to expose in a public repository
- not secret, private, or customer-specific

## Classification categories

Each candidate string should be classified as one of the following:

| Category | Meaning | Goes into language pack? |
|---|---|---:|
| user-facing | visible in UI or user messages | yes |
| learning-feedback | educational feedback shown to users | yes |
| glossary-term | stable product or learning terminology | yes |
| validation-message | user-safe error or warning | yes |
| developer-only | comments, internals, helper labels | no |
| log-debug | logs, debug traces, technical diagnostics | no |
| config-value | URLs, IDs, paths, flags, constants | no |
| test-fixture | test data or generated sample text | usually no |
| false-positive | detected by static scan but not useful | no |
| possible-pro | valuable specialized content for future paid packs | not now |

## Recommended key groups

The language pack key list should remain grouped into the same sections defined by the schema:

- ui
- messages
- feedback
- glossary

## ui keys

Use ui keys for short interface labels.

Examples:

- app.title
- app.subtitle
- button.start
- button.cancel
- button.save
- button.export
- nav.home
- nav.settings
- status.ready
- status.processing

## messages keys

Use messages keys for user-facing operational messages.

Examples:

- message.saved
- message.export_complete
- message.file_loaded
- warning.unsaved_changes
- error.file_not_supported
- lesson.progress

## feedback keys

Use feedback keys for educational correction and learning feedback.

Examples:

- feedback.correct
- feedback.try_again
- feedback.good_progress
- feedback.grammar_hint
- feedback.review_needed

## glossary keys

Use glossary keys for stable terminology.

Examples:

- term.pdf
- term.lesson
- term.exercise
- term.translation
- term.grammar
- term.vocabulary
- term.feedback

## Naming rules

Translation keys should:

- use lowercase
- use dot notation
- avoid spaces
- avoid hyphens
- avoid camelCase
- be stable and descriptive
- avoid implementation-specific names
- avoid file names or component names
- avoid temporary wording

Recommended pattern:

section.name

Examples:

- button.save
- message.file_loaded
- feedback.correct
- term.lesson

## Placeholder rules

Placeholders must be preserved exactly.

Allowed example:

Lesson {current} of {total}

Romanian equivalent:

Lecția {current} din {total}

The placeholder names must not be translated.

Correct:

- {current}
- {total}

Incorrect:

- {curent}
- {totalul}
- {number}
- {count}

## Public repository boundary

Safe public content:

- language schema
- sample language packs
- public translation keys
- generic UI labels
- generic learning feedback
- generic glossary terms
- validator tooling

Avoid public content:

- paid feature enforcement
- private commercial roadmap details
- license activation logic
- private prompts
- customer-specific terminology
- API keys
- secrets
- private datasets

## Possible future Pro boundary

Possible future paid or Pro content may include:

- professionally reviewed translations
- specialized terminology packs
- domain-specific educational packs
- advanced feedback packs
- teacher/tutor templates
- enterprise/custom terminology

This milestone does not implement monetization.

## Review workflow

Recommended workflow before runtime localization:

1. Start from LANGUAGE-PACK-INVENTORY.md.
2. Ignore obvious false positives.
3. Select only stable user-facing strings.
4. Assign each selected string to ui, messages, feedback, or glossary.
5. Give each string a stable key.
6. Add the key to TRANSLATION-KEYS-DRAFT.md.
7. Update sample ro/en packs later.
8. Run the validator.
9. Only after review is stable, plan runtime integration.

## Current decision

For v0.2.9-public-beta-language-pack-review, the correct action is to document the review policy and draft translation keys.

No application runtime files should be modified.
