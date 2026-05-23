# Voila! Language Pack Release Candidate Package Checklist

Milestone: v0.3.0-public-beta-language-pack-release-candidate-package-plan
Status: package checklist
Scope: documentation only; no ZIP build, no Git tag, no GitHub release upload, no public ZIP publish

## Package identity documented

- [x] proposed ZIP naming pattern
- [x] proposed SHA256 naming pattern
- [x] proposed release-notes naming pattern
- [x] proposed final-checklist naming pattern
- [x] proposed test-log naming pattern

## Candidate contents documented

- [x] docs/language-packs/
- [x] language-packs/core/
- [x] language-packs/schema/
- [x] language-packs/samples/
- [x] language-packs/runtime/
- [x] scripts/language-packs/
- [x] scripts/release/inspect-language-pack-packaging.ps1
- [x] services/api/i18n.py
- [x] services/api/web_app.py

## Required files documented

- [x] core English language pack
- [x] core Romanian language pack
- [x] schema
- [x] English sample pack
- [x] Romanian sample pack
- [x] minimal runtime
- [x] validator
- [x] language-pack tests
- [x] language-pack smokes
- [x] packaging inspection script

## Exclusions documented

- [x] .git
- [x] .venv
- [x] node_modules
- [x] __pycache__
- [x] *.pyc
- [x] dist/build output
- [x] local backups
- [x] stale RC ZIPs
- [x] old checksum files
- [x] temporary helper files
- [x] private/commercial-only assets
- [x] unapproved paid supporter assets
- [x] unapproved LICENSE changes

## Asset rules documented

- [x] ZIP only after validation
- [x] SHA256 only after final ZIP
- [x] verify package contents before upload
- [x] avoid stale assets
- [x] avoid accidental overwrite

## Publishing guard

- [x] no ZIP built in this milestone
- [x] no Git tag created in this milestone
- [x] no GitHub release uploaded in this milestone
- [x] no public ZIP published in this milestone
- [x] no checksum published in this milestone
- [x] no release notes asset uploaded in this milestone
- [x] no LICENSE change in this milestone

## Decision

This milestone is package planning only.

Build and publishing remain deferred.
