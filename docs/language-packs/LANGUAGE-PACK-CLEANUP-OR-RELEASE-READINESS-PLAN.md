# Voila! Language Pack Cleanup or Release Readiness Plan

Milestone: v0.2.96-public-beta-language-pack-cleanup-or-release-readiness-plan
Status: planning
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone plans the next step after the completed UI error/status and full UI localization documentation sequences.

The decision point is whether to do a small cleanup pass or move toward release-readiness documentation for the language-pack workstream.

## Baseline

This plan builds on:

```text
UI error/status localization rollup
full UI localization rollup
core language-pack validation
runtime helper tests
language-pack packaging inspection
v0.2.81 reflected-XSS fix using _html_escape(str(page))
```

## Current state

The language-pack workstream now has:

```text
schema documentation
sample packs
core packs for ro and en
validator coverage
runtime helper coverage
minimal runtime helper coverage
UI core key coverage
UI error/status integration coverage
full UI localization integration coverage
documentation rollups
```

The current public beta release assets remain unchanged.

## Recommended path

Recommended next direction:

```text
release-readiness documentation before any new public release assets
```

Reasoning:

```text
the language-pack implementation and documentation stream is now broad enough to require a readiness review
cleanup should be limited to documentation and validation inventory first
runtime/schema/release packaging should not be changed without a dedicated plan
```

## Release-readiness areas to inspect next

Recommended next milestone should inspect:

```text
language-pack docs index and discoverability
validation command list
smoke command list
packaging inspection command list
known unsupported items
remaining deferred UI localization strategy
security notes, especially dynamic HTML escaping
release notes draft requirements
public ZIP readiness requirements
GitHub release asset requirements
no-LICENSE/commercial-positioning constraints
```

## Cleanup areas to inspect next

Possible cleanup candidates:

```text
duplicate documentation phrasing
outdated deferred wording
old smoke expectations that no longer apply
missing rollup cross-links
unclear command lists
long-term naming consistency for ui.* keys
```

Cleanup should be documentation-only unless a later milestone explicitly approves code or test maintenance.

## Recommended next milestone

Recommended next milestone:

```text
v0.2.97-public-beta-language-pack-release-readiness-inventory
```

That milestone should be documentation-only and should inventory release-readiness requirements without publishing a release.

## Optional alternative path

If cleanup is preferred before readiness, use:

```text
v0.2.97-public-beta-language-pack-docs-cleanup-inventory
```

That path should only inspect documentation and smoke helper naming, with no runtime/schema/release changes.

## Safety rules

Future work must preserve:

```text
existing v0.2.0-public-beta release assets
no GitHub release upload without explicit release milestone
no Git tag without explicit release milestone
no public ZIP publish without explicit release milestone
no LICENSE change until monetization/licensing decision is explicit
v0.2.81 _html_escape(str(page)) reflected-XSS fix
existing language-pack schema compatibility
existing runtime fallback behavior
```

## Non-goals

This milestone does not:

- modify UI code
- add language-pack JSON keys
- modify schema
- modify runtime behavior
- create a release checklist asset
- upload GitHub release assets
- create a Git tag
- publish a ZIP
- modify LICENSE files

## Decision

v0.2.96 is documentation only.

It recommends moving next to a release-readiness inventory milestone, while keeping cleanup as a documentation-only optional path.
