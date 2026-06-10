# Voila Windows Package ZIP Candidate Plan

Milestone:

```text
v0.3.25-voila-windows-package-zip-candidate-plan
```

## Purpose

Plan the first controlled Voila Windows ZIP package candidate.

This milestone is documentation-only.

It does not:

```text
create a ZIP
create an installer
rebuild runtime files
publish a GitHub release
upload assets
change runtime behavior
change backend behavior
change frontend behavior
change dependencies
change GitHub visibility
add payment or activation
provide final legal approval
```

---

## Background

The package staging flow has already been planned, implemented, smoke-tested, dry-run validated, and documented.

Validated helper scripts:

```text
scripts/release/copy-package-legal-files.ps1
scripts/release/validate-package-staging.ps1
```

Validated dry-run staging files:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

The next logical step is to plan the first ZIP candidate before creating it.

---

## ZIP candidate goal

The ZIP candidate should be a controlled Windows package candidate for review/testing.

It should:

```text
contain staged Voila Windows runtime/package files
contain README-WINDOWS.txt
contain RELEASE-NOTES.txt
contain START-VOILA.bat
contain STOP-VOILA.bat
contain legal/ package files
pass package staging validation
have SHA256 generated after ZIP creation
be smoke-tested before any public release
```

---

## Proposed ZIP name

Recommended pattern:

```text
voila-v0.3.25-public-beta-windows-package-candidate.zip
```

Alternative if this is internal-only:

```text
voila-v0.3.25-windows-package-candidate-internal.zip
```

Do not call it final unless it has passed all gates.

---

## Proposed staging folder

Recommended temporary staging folder:

```text
.release-cache/voila-v0.3.25-windows-package-candidate/
```

or:

```text
$env:TEMP/voila-v0.3.25-windows-package-candidate/
```

The folder should be disposable and should not be committed.

---

## Expected ZIP root structure

The ZIP should open to a single root folder:

```text
voila/
  README-WINDOWS.txt
  RELEASE-NOTES.txt
  START-VOILA.bat
  STOP-VOILA.bat
  legal/
    EULA.txt
    LICENSE.txt
    BETA-TERMS.md
    THIRD-PARTY-NOTICES.md
  ...
```

The `...` represents runtime/package files already required for the Windows package.

---

## Required legal files

Required:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

These should be produced by:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta
```

---

## Required validation

Before ZIP creation:

```powershell
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta `
  -Strict
```

Expected:

```text
Result: PASS
```

If validation is `CONDITIONAL` or `FAIL`, do not create the ZIP candidate.

---

## SHA256 plan

After ZIP creation, generate:

```text
voila-v0.3.25-public-beta-windows-package-candidate.zip.sha256
```

Recommended PowerShell:

```powershell
Get-FileHash .\voila-v0.3.25-public-beta-windows-package-candidate.zip -Algorithm SHA256
```

The checksum should be published beside the ZIP only after the ZIP candidate is frozen.

---

## Release notes fields

`RELEASE-NOTES.txt` should include:

```text
Release type:
Version:
Date:
Intended audience:
Runtime package:
Candidate status:
Known limitations:
Page-count limits:
Commercial use:
Redistribution:
Legal files:
SHA256:
Smoke test status:
```

For candidate builds, clearly mark:

```text
candidate / not final
```

---

## ZIP candidate gates

Do not create the ZIP candidate unless:

```text
[ ] staging folder is prepared
[ ] legal files copied
[ ] package staging validation passes with -Strict
[ ] README-WINDOWS.txt is present
[ ] RELEASE-NOTES.txt is present
[ ] START-VOILA.bat is present
[ ] STOP-VOILA.bat is present
[ ] no private/secrets files are included
[ ] no docs/commercial are included
[ ] no local helper scripts are included accidentally
```

Do not publish the ZIP candidate unless:

```text
[ ] ZIP created
[ ] SHA256 generated
[ ] ZIP extracted on clean location
[ ] START-VOILA.bat smoke-tested
[ ] STOP-VOILA.bat smoke-tested
[ ] local ports/processes cleaned after smoke
[ ] README and legal files verified inside extracted ZIP
```

---

## What is out of scope for this milestone

This milestone does not:

```text
create the staging folder
copy runtime files
create a ZIP
generate SHA256
publish a release
create an installer
sign binaries
add license activation
enable payments
make repo private
```

---

## Recommended next milestone

If this plan is accepted, next milestone:

```text
v0.3.26-voila-windows-package-zip-candidate-build-plan
```

Recommendation: do one more build-plan milestone before creating the ZIP candidate.
