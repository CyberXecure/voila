# Voila! Language Pack Real Build Verification Checklist

Milestone: v0.2.35-public-beta-language-pack-real-build-verification-plan
Status: real build verification checklist
Scope: documentation only; no build execution, no packaging script changes, no runtime changes, no UI changes, no licensing changes

## Before real build

- main is clean
- no open PRs
- no uncommitted files
- source language-pack inspection passes
- packaging readiness dry-run passes
- packaging readiness dry-run with samples passes
- standalone language-pack source smoke passes
- standalone language-pack source smoke with samples passes
- build output smoke safe mode skips cleanly
- language-pack validation passes
- runtime tests pass
- minimal runtime tests pass
- UI smoke passes
- core runtime helper smoke passes
- language-pack file smoke passes
- Python compile passes
- PowerShell parse check passes

## During real build

- build is run intentionally
- output ZIP path is captured
- existing v0.2.0-public-beta assets are not modified
- build fails before ZIP creation if staged language-pack files are missing

## After real build

- smoke-language-pack-build-output.ps1 passes against the new ZIP
- smoke-language-pack-standalone-package.ps1 passes against the new ZIP
- extracted ZIP contains language-packs/core
- extracted ZIP contains language-packs/schema
- test-standalone-runtime.ps1 passes
- no runtime/UI changes are included accidentally

## Required ZIP files

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

## Do not proceed if

- old ZIP is accidentally selected
- build output smoke fails
- standalone package smoke fails
- language-pack files are missing from ZIP
- runtime test fails
- working tree becomes dirty unexpectedly
- release assets would be overwritten

## Decision

This checklist documents the future real build verification flow.

No real build is performed in v0.2.35.
