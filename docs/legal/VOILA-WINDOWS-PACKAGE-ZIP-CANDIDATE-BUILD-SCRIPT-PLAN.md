# Voila Windows Package ZIP Candidate Build Script Plan

Milestone:

```text
v0.3.27-voila-windows-package-zip-candidate-build-script-plan
```

## Purpose

Plan a future release helper script that will automate creation of a controlled Voila Windows ZIP package candidate.

This milestone is documentation-only.

It does not add the build script yet.

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

Previous milestones planned the ZIP candidate and the concrete build process:

```text
v0.3.25-voila-windows-package-zip-candidate-plan
v0.3.26-voila-windows-package-zip-candidate-build-plan
```

Existing validated helper scripts:

```text
scripts/release/copy-package-legal-files.ps1
scripts/release/validate-package-staging.ps1
```

The future build script should orchestrate these helpers safely.

---

## Proposed future script path

```text
scripts/release/build-windows-zip-candidate.ps1
```

---

## Proposed command

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <runtime-source-folder> `
  -OutputRoot .\.release-cache\voila-v0.3.27-windows-package-candidate `
  -Version "v0.3.27" `
  -ReleaseType PublicBeta
```

Dry-run mode:

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <runtime-source-folder> `
  -OutputRoot .\.release-cache\voila-v0.3.27-windows-package-candidate `
  -Version "v0.3.27" `
  -ReleaseType PublicBeta `
  -DryRun
```

---

## Proposed parameters

### RuntimeSource

Required.

Purpose:

```text
Source folder containing the validated Voila runtime/package files.
```

Rules:

```text
must exist
must be a directory
must not be repository root
must not be docs/
must not be scripts/
must be explicitly selected
```

### OutputRoot

Required.

Purpose:

```text
Local output root where staging, ZIP, SHA256, and extracted smoke folders are created.
```

Expected children:

```text
staging/
out/
extract-smoke/
```

### Version

Required.

Example:

```text
v0.3.27
```

### ReleaseType

Required.

Allowed values:

```text
PublicBeta
TesterDemo
Supporter
Pro
Internal
```

### ZipName

Optional.

Default pattern:

```text
voila-<Version>-public-beta-windows-package-candidate.zip
```

### DryRun

Optional.

Purpose:

```text
Prepare and validate staging, but do not create ZIP or SHA256.
```

### SkipSmoke

Optional later.

Purpose:

```text
Allow candidate build without running post-extract smoke checks.
```

Default should be false for shareable candidates.

---

## Future script responsibilities

The future script should:

```text
sync/validate inputs
create clean output root
create staging/voila folder
copy runtime files from RuntimeSource
copy README-WINDOWS.txt
copy RELEASE-NOTES.txt
copy START-VOILA.bat
copy STOP-VOILA.bat
run copy-package-legal-files.ps1
run validate-package-staging.ps1 -Strict
create ZIP candidate if not DryRun
generate SHA256 if not DryRun
extract ZIP to clean smoke folder
verify required files after extract
write build summary
```

---

## Future script must not

The script must not:

```text
publish GitHub release
upload assets
change GitHub visibility
change runtime source code
install dependencies
create installer
sign binaries
enable payments
add license activation
claim final legal approval
```

---

## Expected output tree

```text
.release-cache/voila-v0.3.27-windows-package-candidate/
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
    voila-v0.3.27-public-beta-windows-package-candidate.zip
    voila-v0.3.27-public-beta-windows-package-candidate.zip.sha256
  extract-smoke/
    voila/
      ...
```

---

## Validation sequence

Before ZIP:

```text
copy-package-legal-files.ps1 PASS
validate-package-staging.ps1 -Strict PASS
```

After ZIP:

```text
ZIP exists
SHA256 exists
ZIP extracts cleanly
required extracted files exist
legal files exist
README exists
release notes exist
launchers exist
```

---

## Build summary

The future script should write a summary file such as:

```text
out/BUILD-SUMMARY.txt
```

Suggested contents:

```text
Version
ReleaseType
RuntimeSource
OutputRoot
ZipPath
Sha256Path
StagingValidationResult
ExtractValidationResult
SmokeStatus
CreatedAt
```

---

## Failure behavior

The future script should stop if:

```text
RuntimeSource missing
required source files missing
legal copy fails
package staging validation fails
ZIP creation fails
SHA256 generation fails
extract validation fails
forbidden files are detected
```

---

## Next milestone

After this planning milestone, a safe next step is:

```text
v0.3.28-voila-windows-package-zip-candidate-build-script
```

That milestone can implement the actual script while still avoiding any official release publication.
