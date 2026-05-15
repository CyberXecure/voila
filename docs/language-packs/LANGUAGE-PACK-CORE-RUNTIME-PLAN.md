# Voila! Language Pack Core Runtime Plan

Milestone: v0.2.21-public-beta-language-pack-core-runtime-plan  
Status: core runtime planning only  
Scope: documentation only, no runtime changes, no packaging changes, no licensing changes

## Goal

This milestone defines how Voila! should eventually switch language pack runtime loading from sample packs to core packs.

The purpose is to avoid changing runtime behavior before the core path, fallback behavior, tests, and packaging impact are clear.

## Non-goals

This milestone does not:

- modify application runtime behavior
- switch runtime loading from samples to core
- change OCR Monaco UI behavior
- add a new language selector
- change standalone packaging
- add paid/pro enforcement
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- add external dependencies

## Current state

Core packs now exist:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json

Sample packs still exist:

- language-packs/samples/ro.language-pack.sample.json
- language-packs/samples/en.language-pack.sample.json

The validator supports both samples and optional core packs.

The runtime helper still uses samples unless explicitly changed later.

## Why not switch immediately

Do not switch runtime source paths immediately because:

- packaging behavior has not been verified
- standalone path resolution has not been tested with core packs
- current sample-based tests are stable
- fallback behavior must remain unchanged
- the change should be isolated in a small future PR

## Recommended runtime source policy

Recommended future order:

1. language-packs/core/
2. language-packs/samples/
3. internal fallback text

This means core packs become preferred, but samples remain useful as fallback during the transition.

## Recommended first implementation

The first implementation should be small.

Recommended changes:

- update the isolated Python runtime helper to accept core path
- add tests for core pack loading
- keep sample loading tests
- do not change UI source paths yet
- do not change packaging yet

## Runtime fallback policy

Runtime should fall back safely:

1. selected language from core
2. English from core
3. Romanian from core
4. selected language from samples
5. English from samples
6. Romanian from samples
7. caller-provided default text
8. key

The app must not crash if core packs are missing.

## Path policy

Runtime code must avoid hardcoded development-only paths.

Good:

- resolve paths relative to repository or app base
- accept explicit language pack directory for tests
- tolerate missing directories

Avoid:

- absolute local development paths
- network paths
- remote URLs
- user profile-specific paths

## Packaging policy

This milestone does not change packaging.

Before packaging integration, verify:

- core packs are bundled
- app can locate them in standalone mode
- app starts if core packs are missing
- app starts if one core pack is invalid
- app starts without internet access

## Test policy

Before switching runtime to core, tests should cover:

- core directory exists
- core ro/en packs parse
- core ro/en packs validate
- selected language resolves from core
- unsupported language falls back to en core
- missing core directory falls back safely
- samples remain valid
- placeholders still work

## UI policy

Do not expand UI localization during the runtime source switch.

The source switch should be independent from UI expansion.

Keep UI changes separate and small.

## Public vs Pro boundary

Core packs should remain public/basic.

Do not include:

- paid/pro unlock logic
- license checks
- specialized dictionaries
- private terminology
- enterprise/customer-specific packs

## Risk control

Main risks:

- runtime cannot find core packs in standalone mode
- packaged app omits core packs
- core path breaks local dev
- fallback order becomes confusing
- samples and core diverge unexpectedly
- too many changes land in one PR

Mitigation:

- plan first
- change runtime source in a separate milestone
- add tests before UI expansion
- do not modify packaging in the same PR
- keep samples as fallback

## Recommended next milestone

v0.2.22-public-beta-language-pack-core-runtime-helper

Suggested next work:

- update isolated runtime helper to support core packs
- keep samples fallback
- add tests for core path
- avoid UI changes
- avoid packaging changes

## Decision for this milestone

For v0.2.21-public-beta-language-pack-core-runtime-plan, the correct action is documentation only.

No runtime source paths should be changed in this milestone.
