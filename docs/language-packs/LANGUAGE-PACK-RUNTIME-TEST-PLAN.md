# Voila! Language Pack Runtime Test Plan

Milestone: v0.2.11-public-beta-language-pack-runtime-plan  
Status: runtime test planning / documentation only  
Scope: no runtime changes, no packaging changes, no licensing changes

## Goal

This document defines the test plan that should be used before and during future runtime language pack integration.

The goal is to protect the validated standalone behavior while adding localization support gradually.

## Non-goals

This milestone does not:

- add tests to the runtime
- modify application code
- add a language selector
- change packaging
- add dependencies
- modify the validated v0.2.0-public-beta release

## Test principles

Language pack runtime tests should prove that:

- the app starts without language packs
- the app starts with valid language packs
- the app ignores invalid language packs safely
- fallback works
- placeholders remain intact
- packaging includes required language files
- missing keys do not crash the app

## Current validation command

Existing validator command:

python .\scripts\language-packs\validate-language-packs.py

Expected result:

Language pack validation passed.

## Pre-runtime checklist

Before implementing runtime loading:

- main branch is clean
- validator passes
- ro/en sample packs are valid
- schema exists
- fallback policy is documented
- key subset is small
- rollback plan is clear

## Runtime test cases

### Test 1 - Default startup

Expected behavior:

- app starts normally
- no language setting is required
- no crash occurs
- default text appears

### Test 2 - Valid selected language

Expected behavior:

- selected language loads
- known keys display translated values
- missing keys fall back safely

### Test 3 - Missing selected language pack

Expected behavior:

- app does not crash
- fallback language is used
- developer-safe warning may be logged

### Test 4 - Invalid JSON pack

Expected behavior:

- invalid pack is ignored
- app does not crash
- fallback language is used

### Test 5 - Missing key

Expected behavior:

- missing key falls back to English
- if English is missing, falls back to Romanian
- if Romanian is missing, uses internal safe default

### Test 6 - Placeholder preservation

Example key:

lesson.progress

Expected behavior:

- {current} and {total} are preserved
- values are substituted safely
- untranslated placeholder names are not changed

### Test 7 - Unsupported language code

Expected behavior:

- unsupported language is rejected
- fallback language is used
- app continues normally

### Test 8 - Standalone package smoke test

Expected behavior:

- packaged app starts
- bundled language files are available
- fallback works in packaged mode
- app runs without development-only paths

## Manual verification checklist

After runtime integration, manually verify:

- app launches
- main screen loads
- selected sample strings render
- Romanian and English packs both work
- fallback works after temporarily renaming one pack
- validator still passes
- no dependency change was introduced unexpectedly
- standalone build still works

## Regression risks

Important risks to watch:

- broken startup if language file is missing
- packaging omits language files
- translations become required too early
- missing placeholders break messages
- runtime tries to read development-only paths
- UI text becomes inconsistent
- invalid language pack crashes the app

## Rollback plan

The first runtime implementation should be easy to revert.

Recommended rollback strategy:

- keep translation helper isolated
- keep first UI integration small
- avoid wide refactors
- avoid global replacement of all strings
- do not remove existing fallback text

## CI recommendation

Future CI may run:

python .\scripts\language-packs\validate-language-packs.py

This should happen before runtime language pack support is expanded.

## Decision for this milestone

For v0.2.11-public-beta-language-pack-runtime-plan, this file documents the future runtime test plan only.

No application runtime files should be modified.
