# Voila! Language Pack Release Candidate Plan

Milestone: v0.2.37-public-beta-language-pack-release-candidate-plan
Status: release candidate planning
Scope: documentation only; no GitHub release upload, no tag, no public asset publish, no runtime changes, no UI changes

## Goal

This milestone documents the safe path from the validated local v0.2.36 ZIP dry run to a future release candidate.

Validated local dry-run ZIP:

`	ext
ZIP:    D:\dev\releases\voila-v0236-lpbuild-20260516-1844.zip
SHA256: D63C223CC233438D29176F43E9BA166F5659B04FA2CD11904E72E4A28092CAD3
`",
",


The v0.2.36 dry-run build proved that:

- a real standalone ZIP can be built locally
- required language-pack files are included in the ZIP
- build-output language-pack smoke passes
- standalone package language-pack smoke passes
- full standalone runtime smoke passes
- LanguageTool runtime responds
- Tesseract runtime includes expected OCR languages
- the generated ZIP remains a local dry-run artifact only

## Release candidate objective

A release candidate should be a controlled artifact prepared for final manual review before any public release upload.

The RC should not be published automatically.

## Proposed future RC artifact naming

Recommended naming:

`	ext
voila-v0.2.37-public-beta-language-pack-rc1.zip
voila-v0.2.37-public-beta-language-pack-rc1_SHA256.txt
voila-v0.2.37-public-beta-language-pack-rc1_RELEASE-NOTES.md
voila-v0.2.37-public-beta-language-pack-rc1_TEST-LOG.txt
voila-v0.2.37-public-beta-language-pack-rc1_FINAL-CHECKLIST.md
`",
",


Before creating a future RC:

- main must be clean
- no PRs should be open
- all language-pack packaging checks must pass
- a fresh standalone ZIP must be built intentionally
- the ZIP must be validated by smoke-language-pack-build-output.ps1
- the ZIP must be validated by smoke-language-pack-standalone-package.ps1
- the ZIP must pass test-standalone-runtime.ps1
- SHA256 must be generated after final ZIP creation
- release notes must clearly mark the artifact as RC

## What must not happen in this milestone

This milestone must not:

- upload ZIP assets to GitHub Releases
- create a Git tag
- replace the v0.2.0-public-beta release assets
- publish the RC publicly
- modify runtime behavior
- modify UI behavior
- add or modify LICENSE files

## Manual review before public release

Before converting an RC into a public release candidate or beta asset, perform manual validation:

- extract ZIP on a clean folder
- run Voila from Run-Voila.ps1
- confirm browser opens correctly
- upload a small PDF
- run OCR review flow
- confirm Romanian and English language-pack-backed labels behave as expected
- confirm LanguageTool starts locally
- confirm Tesseract OCR works for expected languages
- stop Voila and verify ports are released

## Promotion decision

A release candidate can be promoted only if:

- automated checks pass
- manual review passes
- SHA256 matches the documented hash
- release notes are complete
- final checklist is complete
- no unrelated runtime/UI changes are included

## Recommended next milestone

v0.2.38-public-beta-language-pack-rc-assets-plan

Suggested next work:

- prepare RC release notes
- prepare RC final checklist
- prepare RC test log template
- keep generated ZIP local until final approval

## Decision for this milestone

v0.2.37 is documentation only.

Do not publish or tag anything in this milestone.
