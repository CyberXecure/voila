# Voila Windows ZIP Candidate First Real ZIP Plan

Milestone:

```text
v0.3.35-voila-windows-zip-candidate-first-real-zip-plan
```

## Purpose

Plan the first real Voila Windows ZIP candidate build.

This milestone is documentation/release planning only.

It does not:

```text
create a ZIP
create an installer
generate SHA256
publish a GitHub release
upload release assets
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

The packaging pipeline has reached this state:

```text
build-windows-zip-candidate.ps1 implemented
build script DryRun smoke passed
runtime source approach planned
runtime source DryRun passed
real runtime source plan completed
real runtime source DryRun passed
```

The next step is to plan the first ZIP candidate that will actually be created by the build helper without `-DryRun`.

---

## First ZIP candidate goal

Create a controlled local ZIP candidate from the approved real runtime source.

The ZIP candidate should include:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
runtime/application files
```

The build should also generate:

```text
ZIP file
SHA256 file
BUILD-SUMMARY.txt
extract validation folder
```

---

## Proposed version

Recommended:

```text
v0.3.35
```

---

## Proposed ZIP name

Recommended:

```text
voila-v0.3.35-public-beta-windows-package-candidate.zip
```

Expected SHA256 file:

```text
voila-v0.3.35-public-beta-windows-package-candidate.zip.sha256
```

---

## Proposed output root

Recommended local output root:

```text
.release-cache/voila-v0.3.35-first-real-zip-candidate/
```

Expected children:

```text
staging/voila/
out/
extract-smoke/voila/
```

---

## Required preconditions

Do not create the ZIP unless:

```text
[ ] protected main synced
[ ] working tree clean
[ ] real runtime source selected
[ ] real runtime source path documented
[ ] real runtime source is not repository root
[ ] real runtime source is not docs/
[ ] real runtime source is not scripts/
[ ] real runtime source DryRun has passed
[ ] package staging validation with -Strict has passed in DryRun
[ ] no forbidden/private files are present
```

---

## Required command

After selecting the real runtime source:

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <real-runtime-source> `
  -OutputRoot .\.release-cache\voila-v0.3.35-first-real-zip-candidate `
  -Version "v0.3.35" `
  -ReleaseType PublicBeta `
  -Force
```

This command is expected to create ZIP and SHA256 because it does not use `-DryRun`.

---

## Expected build output

Expected:

```text
.release-cache/voila-v0.3.35-first-real-zip-candidate/
  staging/
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
  out/
    voila-v0.3.35-public-beta-windows-package-candidate.zip
    voila-v0.3.35-public-beta-windows-package-candidate.zip.sha256
    BUILD-SUMMARY.txt
  extract-smoke/
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

---

## Required validation during build

The build helper must complete:

```text
runtime source copy
legal file copy
package staging validation with -Strict
ZIP creation
SHA256 generation
extract validation
BUILD-SUMMARY.txt creation
```

Expected result:

```text
Result: PASS
```

---

## Required post-build checks

After build:

```text
[ ] ZIP exists
[ ] ZIP size recorded
[ ] SHA256 file exists
[ ] SHA256 hash recorded
[ ] BUILD-SUMMARY.txt exists
[ ] extracted folder exists
[ ] extracted README-WINDOWS.txt exists
[ ] extracted RELEASE-NOTES.txt exists
[ ] extracted START-VOILA.bat exists
[ ] extracted STOP-VOILA.bat exists
[ ] extracted legal files exist
[ ] no EXE/MSI installer created
[ ] no GitHub release created
```

---

## Smoke gate after first ZIP

Before sharing the ZIP candidate:

```text
[ ] extract ZIP to a clean folder
[ ] read README-WINDOWS.txt
[ ] verify legal/ folder
[ ] run START-VOILA.bat
[ ] verify Voila starts locally
[ ] run STOP-VOILA.bat
[ ] verify ports/processes cleaned
[ ] document result
```

---

## Publication boundary

The first real ZIP candidate build must not automatically:

```text
publish GitHub release
upload assets
mark candidate final
enable paid distribution
create installer
sign binaries
```

Publishing should remain a separate milestone after ZIP smoke validation.

---

## Out of scope

This milestone does not create the ZIP.

It only plans the first real ZIP candidate build.

---

## Recommended next milestone

After this plan:

```text
v0.3.36-voila-windows-zip-candidate-first-real-zip-build
```

That milestone can create the first local ZIP candidate and document ZIP/SHA256/extract validation results.
