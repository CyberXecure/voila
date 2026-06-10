# Voila Windows Package ZIP Candidate Build Script Specification

## Purpose

Specify behavior for the future ZIP candidate build script.

This is not the implementation.

---

## Proposed script

```text
scripts/release/build-windows-zip-candidate.ps1
```

---

## Primary behavior

The script should automate:

```text
runtime source validation
staging folder creation
runtime file copy
README/release notes/launcher copy
legal file copy
package staging validation
ZIP creation
SHA256 generation
post-extract validation
build summary generation
```

---

## Input validation

The script should validate:

```text
RuntimeSource exists
RuntimeSource is directory
OutputRoot can be created
Version is not empty
ReleaseType is valid
required legal source files exist
copy-package-legal-files.ps1 exists
validate-package-staging.ps1 exists
```

---

## Safe output handling

The script should:

```text
create OutputRoot if missing
remove/recreate staging only with explicit Force or clean staging path
avoid deleting repository folders
avoid deleting user folders outside configured OutputRoot
write all outputs under OutputRoot
```

---

## Required staging files

Before validation, staging should include:

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

---

## Required helper calls

Legal copy:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot <staging-root> `
  -ReleaseType <ReleaseType>
```

Validation:

```powershell
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot <staging-root> `
  -ReleaseType <ReleaseType> `
  -Strict
```

---

## ZIP creation behavior

The script should create ZIP only if:

```text
DryRun is false
staging validation passes
staging root exists
output ZIP path is selected
```

Use:

```powershell
Compress-Archive
```

The ZIP should contain one root folder:

```text
voila/
```

---

## SHA256 behavior

The script should generate SHA256 only after ZIP creation.

Expected output:

```text
<zip-name>.sha256
```

The file should contain:

```text
SHA256 hash
ZIP filename
generated timestamp
```

---

## Extract validation behavior

After ZIP creation, the script should extract to:

```text
extract-smoke/
```

Then verify:

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

---

## DryRun behavior

In `-DryRun` mode, the script should:

```text
create staging
copy runtime/docs/launchers/legal files
run validation
write dry-run summary
not create ZIP
not create SHA256
not extract ZIP
```

---

## Result statuses

Use:

```text
PASS
CONDITIONAL
FAIL
```

For a successful candidate build:

```text
Result: PASS
```

---

## Exit behavior

Recommended:

```text
0 = PASS
1 = FAIL
2 = CONDITIONAL or warnings when Strict mode applies
```
