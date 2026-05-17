# Voila! Language Pack RC Build Checklist

Milestone: v0.2.39-public-beta-language-pack-rc-build-plan
Status: RC build checklist
Scope: documentation only; no GitHub release upload, no tag, no public ZIP publish, no runtime changes, no UI changes

## Before RC build

- [ ] main is clean
- [ ] no open PRs
- [ ] no uncommitted files
- [ ] RC asset templates exist
- [ ] baseline ZIP still exists
- [ ] baseline SHA256 still matches
- [ ] build-output language-pack smoke passes against baseline ZIP
- [ ] standalone package language-pack smoke passes against baseline ZIP
- [ ] source language-pack inspection passes
- [ ] language-pack validation passes
- [ ] runtime tests pass
- [ ] UI smoke passes
- [ ] core runtime smoke passes
- [ ] PowerShell parse check passes

## RC build command

- [ ] run build-portable-runtime.ps1 intentionally
- [ ] use a clear RC version tag
- [ ] write output to D:\dev\releases
- [ ] do not overwrite existing validated artifacts

## After RC build

- [ ] final RC ZIP exists
- [ ] SHA256 generated after final ZIP creation
- [ ] build-output language-pack smoke passes against RC ZIP
- [ ] standalone package language-pack smoke passes against RC ZIP
- [ ] full standalone runtime smoke passes against RC ZIP
- [ ] extracted ZIP contains required language-pack files
- [ ] extracted ZIP contains required runtime files
- [ ] Voila starts locally
- [ ] /health returns ok
- [ ] LanguageTool responds
- [ ] Tesseract lists expected OCR languages
- [ ] Voila port is released after stop
- [ ] LanguageTool port is released after stop

## RC docs/assets

- [ ] RELEASE-NOTES.md updated with RC values
- [ ] TEST-LOG.txt updated with RC checks
- [ ] FINAL-CHECKLIST.md updated
- [ ] SHA256.txt updated with final RC ZIP hash

## Do not proceed if

- [ ] wrong ZIP is selected
- [ ] SHA256 does not match
- [ ] language-pack smoke fails
- [ ] standalone runtime smoke fails
- [ ] runtime files are missing
- [ ] language-pack files are missing
- [ ] working tree becomes dirty unexpectedly
- [ ] GitHub release upload would happen accidentally
- [ ] tag creation would happen accidentally

## Decision

This checklist prepares the future RC build only.

No RC build is performed in v0.2.39.
