# Voila! Language Pack Runtime Source Policy

Milestone: v0.2.24-public-beta-language-pack-core-runtime-docs
Status: source policy documentation
Scope: documentation only, no runtime changes, no packaging changes, no licensing changes

## Goal

This document defines the source policy for Voila! language packs.

## Source groups

| Source | Path | Purpose |
|---|---|---|
| core | language-packs/core/ | reviewed public base packs |
| samples | language-packs/samples/ | examples, schema demos, fallback testing |
| schema | language-packs/schema/ | JSON schema and validation support |
| runtime | language-packs/runtime/ | isolated helper code |

## Core packs

Core packs are intended to become bundled, public language resources.

Current core packs:

- ro.language-pack.json
- en.language-pack.json

Core packs should be reviewed, stable, public-safe, validator-compliant, and suitable for future packaging.

Core packs should not contain private data, secrets, paid/pro unlock logic, customer-specific terminology, or unreviewed specialized dictionaries.

## Sample packs

Sample packs remain useful for documentation, schema demonstration, tests, fallback behavior, and contributor guidance.

## Runtime lookup policy

Current isolated helper policy:

1. prefer core
2. fall back to samples
3. fall back to caller default
4. fall back to key

The app must not crash because a language pack is missing.

## Remote loading policy

Remote loading is not allowed by default.

Do not load language packs from remote URLs, user-submitted script files, dynamic JavaScript, or untrusted network locations.

Language packs are data only.

## Packaging policy

Packaging is not changed yet.

Future packaging work should ensure that core packs are included, paths work in standalone mode, fallback works without development-only paths, and missing files fail safely.

## Promotion policy

Promotion from sample to core should be conservative.

Recommended promotion order:

1. ro
2. en
3. fr/de/ru/it/es/pt only after review

Do not promote all packs automatically.

## Current decision

For the current public beta path:

- core ro/en exist
- samples remain
- helper prefers core
- samples remain fallback
- packaging remains unchanged
- Pro logic is not implemented
