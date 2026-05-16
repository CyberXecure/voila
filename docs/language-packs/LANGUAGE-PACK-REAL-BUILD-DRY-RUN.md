# Voila! Language Pack Real Build Dry Run

Milestone: v0.2.36-public-beta-language-pack-real-build-dry-run  
Status: completed local dry-run build  
Scope: local build verification + packaging script fix; no GitHub release upload, no tag, no public release asset change

## Goal

This milestone performs the first controlled local standalone ZIP build after language-pack packaging checks were added.

The goal is to verify that language-pack files are included in the standalone ZIP and that the resulting package still passes standalone runtime smoke testing.

## Build result

Final successful build:

``text
BuildTag: voila-v0236-lpbuild-20260516-1844
ZIP:      D:\dev\releases\voila-v0236-lpbuild-20260516-1844.zip
INFO:     D:\dev\releases\voila-v0236-lpbuild-20260516-1844_RELEASE-INFO.txt
LOG:      D:\dev\releases\voila-v0236-lpbuild-20260516-1844_BUILD-LOG.txt
SIZE MB:  463.08
SHA256:   D63C223CC233438D29176F43E9BA166F5659B04FA2CD11904E72E4A28092CAD3
``

## Verification passed

The following checks passed against the real ZIP:

- staging language-pack inspection before ZIP creation
- build output language-pack smoke against the real ZIP
- standalone package language-pack smoke against the real ZIP
- full standalone runtime smoke test
- /health returned {"status":"ok"}
- LanguageTool runtime responded
- Tesseract runtime listed expected OCR languages: eng, osd, on, us
- Voila and LanguageTool ports were released after shutdown
- working tree remained clean after the build

## Required language-pack files verified

The standalone ZIP contains:

- language-packs/core/ro.language-pack.json
- language-packs/core/en.language-pack.json
- language-packs/schema/language-pack.schema.json

## Issues found and resolved during dry run

### 1. Stale wheelhouse

The first build attempt failed because the existing local wheelhouse still had an older Pillow wheel while equirements.txt required pillow==12.2.0.

Resolution:

- reran the build with -RefreshWheelhouse
- refreshed the local wheelhouse
- confirmed pillow==12.2.0 installed into the embedded runtime

### 2. Long temporary path

A later build attempt failed during Python package installation because the temporary build path was too long.

Resolution:

- used a short temporary root: D:\tmp
- used a shorter build tag: oila-v0236-lpbuild-<timestamp>

### 3. Java version output handling

The build then reached Java runtime verification but failed because java.exe -version writes version information to stderr. With $ErrorActionPreference = "Stop", PowerShell treated that output as a native command error.

Resolution:

- updated scripts/release/build-portable-runtime.ps1
- captured Java version output through cmd /c
- preserved the visible Java version check without failing the build

## Safety

This milestone did not:

- upload assets to GitHub Releases
- create a Git tag
- overwrite the existing v0.2.0-public-beta release
- change runtime application behavior
- change UI behavior
- add a LICENSE
- publish the generated ZIP as an official release

## Decision

v0.2.36 validates that the current language-pack packaging path can produce and verify a real local standalone ZIP.

The generated ZIP remains a local dry-run artifact only.