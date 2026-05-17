# Voila! Language Pack RC Final Checklist

Milestone: v0.2.38-public-beta-language-pack-rc-assets-plan
Status: template only; not published

## Repository state

- [ ] main is clean
- [ ] no open PRs
- [ ] no uncommitted files
- [ ] final RC branch is up to date

## Artifact state

- [ ] final ZIP exists
- [ ] SHA256 generated after final ZIP creation
- [ ] RELEASE-NOTES.md complete
- [ ] TEST-LOG.txt complete
- [ ] FINAL-CHECKLIST.md complete

## Required ZIP contents

- [ ] language-packs/core/ro.language-pack.json
- [ ] language-packs/core/en.language-pack.json
- [ ] language-packs/schema/language-pack.schema.json
- [ ] python/python.exe
- [ ] runtime/tesseract/tesseract.exe
- [ ] runtime/java/bin/java.exe
- [ ] runtime/languagetool/languagetool-server.jar
- [ ] Run-Voila.ps1
- [ ] Stop-Voila.ps1

## Automated validation

- [ ] build-output language-pack smoke passed
- [ ] standalone package language-pack smoke passed
- [ ] full standalone runtime smoke passed
- [ ] language-pack validation passed
- [ ] runtime tests passed
- [ ] UI smoke passed
- [ ] core runtime smoke passed
- [ ] PowerShell parse check passed

## Safety

- [ ] no GitHub release upload in this milestone
- [ ] no Git tag in this milestone
- [ ] no public asset publish in this milestone
- [ ] v0.2.0-public-beta assets unchanged
- [ ] no runtime behavior change
- [ ] no UI behavior change
- [ ] no LICENSE change

## Decision

- [ ] Ready for future RC asset preparation
- [ ] Not ready; issues must be fixed first
