# Voila! Language Pack RC Release Notes

Milestone: v0.2.40-public-beta-language-pack-rc-build-dry-run
Artifact type: local Release Candidate dry run
Status: local only; not published

## Release candidate summary

This local release-candidate dry run validates the Voila! standalone package after language-pack packaging checks were added.

## Local RC artifact

``text
BuildTag: voila-v0240-lp-rc1-20260517-0914
ZIP:      D:\dev\releases\voila-v0240-lp-rc1-20260517-0914.zip
SHA256:   33DC31243F45AD499A889A12F4140779499EFCC0C6218C5BB011920CF36679BC
``

## Highlights

- includes core Romanian and English language packs
- includes language-pack schema
- validates language-pack files inside the standalone ZIP
- passes standalone package language-pack smoke
- passes full standalone runtime smoke
- keeps language-pack packaging isolated from UI/runtime behavior changes

## Included language-pack files

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

## Validation summary

The local RC ZIP passed:

- build-output language-pack smoke
- standalone package language-pack smoke
- full standalone runtime smoke
- source language-pack inspection
- language-pack validation
- Python compile

## Safety note

This is not a public release announcement.

No GitHub release upload, tag, or public asset publication is performed in v0.2.40.
