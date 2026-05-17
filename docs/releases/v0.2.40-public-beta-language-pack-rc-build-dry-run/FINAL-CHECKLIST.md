# Voila! Language Pack RC Final Checklist

Milestone: v0.2.40-public-beta-language-pack-rc-build-dry-run
Status: completed local RC dry run; not published

## Repository state

- [x] branch is release/v0.2.40-public-beta-language-pack-rc-build-dry-run
- [x] no uncommitted files before RC build
- [x] RC build docs repaired/updated
- [x] RC dry-run documentation added
- [x] RC asset files updated with real RC values

## Artifact state

- [x] final local RC ZIP exists
- [x] RELEASE-INFO exists
- [x] BUILD-LOG exists
- [x] SHA256 generated after final ZIP creation
- [x] RELEASE-NOTES.md complete
- [x] TEST-LOG.txt complete
- [x] FINAL-CHECKLIST.md complete
- [x] SHA256.txt complete

## Required ZIP contents

- [x] language-packs/core/ro.language-pack.json
- [x] language-packs/core/en.language-pack.json
- [x] language-packs/schema/language-pack.schema.json
- [x] python/python.exe
- [x] runtime/tesseract/tesseract.exe
- [x] runtime/java/bin/java.exe
- [x] runtime/languagetool/languagetool-server.jar
- [x] Run-Voila.ps1
- [x] Stop-Voila.ps1

## Automated validation

- [x] build-output language-pack smoke passed
- [x] standalone package language-pack smoke passed
- [x] full standalone runtime smoke passed
- [x] language-pack validation passed
- [x] Python compile passed
- [x] PowerShell parse check passed

## Safety

- [x] no GitHub release upload in this milestone
- [x] no Git tag in this milestone
- [x] no public asset publish in this milestone
- [x] v0.2.0-public-beta assets unchanged
- [x] no runtime behavior change
- [x] no UI behavior change
- [x] no LICENSE change

## Decision

- [x] Local RC dry run validated
- [x] Keep RC artifact local until final approval
