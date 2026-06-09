# Voila Windows Package Staging Dry-Run Plan

Milestone:

```text
v0.3.22-voila-windows-package-staging-dry-run-plan
```

## Purpose

Plan a complete dry-run for preparing a Voila Windows package staging folder before creating a ZIP or installer.

This milestone is documentation-only.

It does not:

```text
create a package
create a ZIP
create an installer
rebuild runtime files
change runtime behavior
change backend behavior
change frontend behavior
change dependencies
publish a GitHub release
change GitHub visibility
add payment or activation
provide final legal approval
```

---

## Background

Voila now has package helper scripts:

```text
scripts/release/copy-package-legal-files.ps1
scripts/release/validate-package-staging.ps1
```

These scripts are intended to support future controlled Windows package preparation.

The dry-run plan defines how to test the package staging workflow without producing final release assets.

---

## Dry-run goal

A dry-run should prove that a package staging folder can be prepared with:

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

Then it should pass:

```text
copy-package-legal-files.ps1
validate-package-staging.ps1
```

The dry-run should stop before ZIP or installer creation.

---

## Recommended dry-run folder

Use a temporary or local release-cache folder such as:

```text
.release-cache/voila-package-staging-dry-run
```

or:

```text
$env:TEMP/voila-package-staging-dry-run
```

The dry-run folder should be disposable.

---

## Dry-run sequence

Recommended sequence:

```text
1. sync main
2. create dry-run staging folder
3. create or copy README-WINDOWS.txt
4. create or copy RELEASE-NOTES.txt
5. create or copy START-VOILA.bat
6. create or copy STOP-VOILA.bat
7. run copy-package-legal-files.ps1
8. run validate-package-staging.ps1
9. run validate-package-staging.ps1 -Strict
10. inspect dry-run staging folder
11. delete dry-run staging folder
12. document results
```

---

## Dry-run command concept

Legal file copy:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot <dry-run-staging-folder> `
  -ReleaseType PublicBeta
```

Package validation:

```powershell
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot <dry-run-staging-folder> `
  -ReleaseType PublicBeta
```

Strict validation:

```powershell
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot <dry-run-staging-folder> `
  -ReleaseType PublicBeta `
  -Strict
```

---

## Dry-run success criteria

The dry-run passes when:

```text
[ ] staging folder is created
[ ] README-WINDOWS.txt exists
[ ] RELEASE-NOTES.txt exists
[ ] START-VOILA.bat exists
[ ] STOP-VOILA.bat exists
[ ] legal/EULA.txt exists
[ ] legal/LICENSE.txt exists
[ ] legal/BETA-TERMS.md exists
[ ] legal/THIRD-PARTY-NOTICES.md exists
[ ] validate-package-staging.ps1 returns PASS
[ ] validate-package-staging.ps1 -Strict returns PASS
[ ] no ZIP or installer is created
[ ] staging folder is cleaned or clearly marked as temporary
```

---

## What the dry-run should not do

The dry-run must not:

```text
publish anything
create GitHub releases
upload release assets
create final ZIP
create installer
generate official SHA256 for release
modify runtime files
include private documents
include secrets
change repository visibility
```

---

## Recommended next milestone

After this planning milestone:

```text
v0.3.23-voila-windows-package-staging-dry-run
```

That milestone can run and document the actual dry-run result.

A later milestone can package a controlled Windows ZIP only after dry-run validation is clean.
