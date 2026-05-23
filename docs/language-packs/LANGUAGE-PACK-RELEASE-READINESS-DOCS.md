# Voila! Language Pack Release Readiness Docs

Milestone: v0.2.99-public-beta-language-pack-release-readiness-docs
Status: documentation rollup
Scope: documentation only; no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no GitHub release upload, no tag, no public ZIP publish

## Goal

This milestone summarizes the release-readiness documentation sequence for the language-pack workstream.

It connects the v0.2.97 release-readiness inventory with the v0.2.98 checklist and runbook.

This milestone does not publish a release.

## Sequence summarized

```text
v0.2.96 cleanup or release-readiness plan
v0.2.97 release-readiness inventory
v0.2.98 release-readiness checklist and runbook
v0.2.99 release-readiness docs rollup
```

## Current readiness documentation

The language-pack release-readiness documentation now includes:

```text
docs/language-packs/LANGUAGE-PACK-RELEASE-READINESS-INVENTORY.md
docs/language-packs/LANGUAGE-PACK-RELEASE-READINESS-INVENTORY-CHECKLIST.md
docs/language-packs/LANGUAGE-PACK-RELEASE-READINESS-CHECKLIST.md
docs/language-packs/LANGUAGE-PACK-RELEASE-READINESS-RUNBOOK.md
```

## What v0.2.97 provides

v0.2.97 inventories release-readiness requirements, including:

```text
documentation discoverability
supported languages and schema docs
core and sample pack consistency
runtime fallback behavior
validator command coverage
smoke command coverage
packaging inspection coverage
security notes
deferred release decisions
release notes, ZIP, asset, and checksum requirements
licensing and commercial-positioning constraints
```

## What v0.2.98 provides

v0.2.98 converts the inventory into a practical checklist and runbook, including:

```text
pre-release gate
documentation readiness
source readiness
required validation commands
security readiness
packaging readiness
deferred publishing actions
future release milestone guardrails
```

## Current validation baseline

The readiness docs point to these required validation areas:

```text
language-pack packaging inspection
language-pack validation
runtime tests
minimal runtime tests
UI core key tests
UI remaining core key tests
UI error/status core key tests
full UI localization core key tests
full UI localization next-batch core key tests
UI language endpoint smoke
core runtime helper smoke
language-pack file smoke
UI core key smoke
full UI localization first-batch smoke
full UI localization next-batch smoke
error/status final deferred smoke
Python compile
```

## Security baseline

The readiness docs preserve the v0.2.81 reflected-XSS fix as a required security check:

```text
_html_escape(str(page))
```

Future release work must continue to verify that dynamic values inserted into HTML are escaped.

## Release actions still deferred

The following remain deferred until a dedicated release milestone explicitly approves them:

```text
GitHub release upload
Git tag
public ZIP publish
release notes asset
checksum asset
LICENSE addition or change
paid supporter / commercial packaging
language selector
browser-locale detection
persisted language preference
adaptive UI switching
```

## Recommended next step

Recommended next step depends on product direction:

```text
docs-only path:
v0.2.100-public-beta-language-pack-readiness-rollup

release-candidate path:
v0.3.0-public-beta-language-pack-release-candidate-plan
```

A release-candidate path should only start if publishing release assets is explicitly approved.

## Non-goals

This milestone does not:

- modify UI code
- add language-pack JSON keys
- modify schema
- modify runtime behavior
- upload GitHub release assets
- create a Git tag
- publish a ZIP
- modify LICENSE files

## Decision

v0.2.99 is documentation only.

It summarizes the release-readiness documentation set and keeps actual publishing deferred to a future explicit release milestone.
