# Voila! Language Pack RC Assets Plan

Milestone: v0.2.38-public-beta-language-pack-rc-assets-plan
Status: RC asset planning
Scope: documentation/templates only; no GitHub release upload, no tag, no public asset publish, no runtime changes, no UI changes

## Goal

This milestone prepares release-candidate asset templates for the language-pack packaging path.

Validated local dry-run baseline:

`	ext
ZIP:    D:\dev\releases\voila-v0236-lpbuild-20260516-1844.zip
SHA256: D63C223CC233438D29176F43E9BA166F5659B04FA2CD11904E72E4A28092CAD3
`",
",


This milestone prepares template files only:

- RELEASE-NOTES.md
- TEST-LOG.txt
- FINAL-CHECKLIST.md
- SHA256.txt

## Target template location

`	ext
docs/releases/v0.2.38-public-beta-language-pack-rc-assets-plan/
`",
",


This milestone must not:

- upload a ZIP to GitHub Releases
- create a Git tag
- publish a release candidate
- overwrite v0.2.0-public-beta assets
- modify runtime behavior
- modify UI behavior
- add or modify LICENSE files

## Future RC asset naming

Future RC assets should use clear names such as:

`	ext
voila-v0.2.38-public-beta-language-pack-rc1.zip
voila-v0.2.38-public-beta-language-pack-rc1_SHA256.txt
voila-v0.2.38-public-beta-language-pack-rc1_RELEASE-NOTES.md
voila-v0.2.38-public-beta-language-pack-rc1_TEST-LOG.txt
voila-v0.2.38-public-beta-language-pack-rc1_FINAL-CHECKLIST.md
`",
",


Before publishing any future RC artifact:

- build-output language-pack smoke must pass against the final ZIP
- standalone package language-pack smoke must pass against the final ZIP
- full standalone runtime smoke must pass
- source language-pack validation must pass
- SHA256 must be generated after final ZIP creation
- release notes must clearly say Release Candidate
- final checklist must be complete
- no unrelated runtime/UI changes may be included

## Decision for this milestone

v0.2.38 prepares RC asset templates only.

No release assets are published in this milestone.
