# Voila Package Legal Files Release Workflow

## Purpose

Define where legal file copying fits into a future Voila Windows package release workflow.

This is documentation-only and does not rebuild a package.

---

## Release workflow summary

Future controlled package flow:

```text
source repo
  -> package staging folder
  -> runtime files
  -> README / release notes
  -> legal file copy helper
  -> package validation
  -> ZIP / installer
  -> SHA256
  -> smoke test
  -> controlled release
```

---

## Legal file copy step

Run:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta
```

Optional validation-only check after copy:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta `
  -ValidateOnly
```

---

## Required output

The package staging folder should contain:

```text
legal/
  EULA.txt
  LICENSE.txt
  BETA-TERMS.md
  THIRD-PARTY-NOTICES.md
```

---

## Release type guidance

### PublicBeta

Use for:

```text
public beta runtime package
evaluation and feedback
controlled public release
```

Required:

```text
legal folder
release notes
SHA256
known limitations
public download wording
```

### TesterDemo

Use for:

```text
selected testers
limited page-count builds
focused feedback
```

Required:

```text
legal folder
tester README
page limit wording
no redistribution wording
feedback instructions
```

### Supporter / Pro

Do not use for paid packages until:

```text
Supporter / Pro terms are ready
EULA is reviewed for paid use
third-party notices are reviewed enough for distribution
commercial readiness gate passes
```

---

## What remains outside this workflow

This workflow does not implement:

```text
payment
license keys
activation
installer EULA UI
code signing
private repo transition
third-party audit completion
```

---

## Recommended future package validation

Future validation should check:

```text
[ ] legal/EULA.txt exists
[ ] legal/LICENSE.txt exists
[ ] legal/BETA-TERMS.md exists
[ ] legal/THIRD-PARTY-NOTICES.md exists
[ ] README references legal/
[ ] release notes reference legal/
[ ] package type is clear
[ ] SHA256 generated
[ ] package starts/stops cleanly
```
