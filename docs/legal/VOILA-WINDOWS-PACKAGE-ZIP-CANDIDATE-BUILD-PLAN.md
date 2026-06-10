# Voila Windows Package ZIP Candidate Build Plan

Milestone:

```text
v0.3.26-voila-windows-package-zip-candidate-build-plan
```

## Purpose

Plan the concrete build process for the first controlled Voila Windows ZIP package candidate.

This milestone is documentation-only.

It does not:

```text
create a ZIP
create an installer
rebuild runtime files
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

The previous milestone planned the ZIP candidate:

```text
v0.3.25-voila-windows-package-zip-candidate-plan
```

This milestone plans how the ZIP candidate should be built safely when the project is ready.

Validated helpers:

```text
scripts/release/copy-package-legal-files.ps1
scripts/release/validate-package-staging.ps1
```

---

## Build candidate goal

The future build should produce a candidate ZIP only after:

```text
package staging is prepared
runtime/package files are copied
README and release notes are included
START/STOP launchers are included
legal files are copied
package staging validation passes
Strict validation passes
ZIP is created
SHA256 is generated
ZIP is extracted and smoke-tested
```

---

## Candidate ZIP name

Recommended:

```text
voila-v0.3.26-public-beta-windows-package-candidate.zip
```

If internal-only:

```text
voila-v0.3.26-windows-package-candidate-internal.zip
```

The final filename should match the release notes and SHA256 file.

---

## Candidate SHA256 name

Recommended:

```text
voila-v0.3.26-public-beta-windows-package-candidate.zip.sha256
```

---

## Staging folder

Recommended:

```text
.release-cache/voila-v0.3.26-windows-package-candidate/staging/voila/
```

Recommended output folder:

```text
.release-cache/voila-v0.3.26-windows-package-candidate/out/
```

These folders should not be committed.

---

## Runtime source decision

Before building the ZIP candidate, decide exactly which runtime source is used:

```text
existing validated Windows tester package
latest package staging folder
fresh runtime staging generated from repository
previous public beta runtime package
```

The selected source must be documented.

Do not mix runtime sources.

---

## Required package files

The staging folder should contain:

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

It should also contain the required Voila runtime files.

---

## Required helper sequence

After staging runtime and documentation files:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot <staging-root> `
  -ReleaseType PublicBeta

.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot <staging-root> `
  -ReleaseType PublicBeta `
  -Strict
```

Expected validation result:

```text
Result: PASS
```

If validation does not pass, stop.

---

## ZIP creation plan

Use PowerShell `Compress-Archive` only after validation passes.

Recommended pattern:

```powershell
Compress-Archive `
  -Path <staging-root> `
  -DestinationPath <out-folder>\voila-v0.3.26-public-beta-windows-package-candidate.zip `
  -Force
```

Before accepting the ZIP candidate:

```text
extract ZIP to a clean folder
verify root folder
verify README
verify release notes
verify launchers
verify legal files
run smoke test
```

---

## SHA256 plan

After ZIP creation:

```powershell
Get-FileHash `
  <zip-path> `
  -Algorithm SHA256
```

Write the result to:

```text
voila-v0.3.26-public-beta-windows-package-candidate.zip.sha256
```

The SHA256 should not be generated before the final ZIP candidate is frozen.

---

## Smoke test plan

After ZIP extraction:

```text
[ ] open extracted folder
[ ] verify README-WINDOWS.txt
[ ] verify RELEASE-NOTES.txt
[ ] verify legal/ folder
[ ] run START-VOILA.bat
[ ] verify app starts locally
[ ] verify expected local URL opens
[ ] run STOP-VOILA.bat
[ ] verify processes/ports are cleaned
```

---

## Exclusion rules

Do not include:

```text
.git/
.github/
.release-cache/
docs/commercial/
private documents
customer PDFs
.env
*.pem
*.key
*.pfx
local helper scripts from repo root
node_modules source cache unless explicitly required
development-only caches
temporary staging logs unless intentionally included
```

---

## Out of scope

This milestone does not create:

```text
ZIP
installer
SHA256
GitHub release
published asset
payment flow
license activation
commercial release
```

---

## Recommended next milestone

If this plan is accepted, next milestone can be:

```text
v0.3.27-voila-windows-package-zip-candidate-build-script-plan
```

or, if the runtime source is already confirmed:

```text
v0.3.27-voila-windows-package-zip-candidate-build
```

Recommendation: add a build script plan before creating the ZIP.
