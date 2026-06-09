# Voila Release Workflow Validation Usage

## Purpose

Provide release workflow guidance for using Voila package helper scripts together.

This document is documentation-only.

---

## Helper scripts

Voila currently has these release/package helper scripts:

```text
scripts/release/copy-package-legal-files.ps1
scripts/release/validate-package-staging.ps1
```

---

## Recommended usage sequence

After the package staging folder exists and after runtime/readme/release-note files are staged:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta

.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta
```

---

## Validate strict mode

Use strict mode when preparing a controlled public release:

```powershell
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta `
  -Strict
```

Strict mode treats warnings as failures.

---

## Validate legal only

Use legal-only validation when checking whether the `legal/` folder is complete:

```powershell
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta `
  -ValidateLegalOnly
```

---

## Expected package staging files

A runnable Windows package staging folder should include:

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

## Expected validation result

For a complete package staging folder:

```text
Result: PASS
```

Conditional results should be reviewed manually before packaging.

Failure results should block ZIP or installer creation.

---

## Release type examples

Use:

```text
PublicBeta
TesterDemo
Supporter
Pro
Internal
```

Supporter and Pro package usage should wait until the relevant commercial/legal terms are finalized.

---

## Not covered by these helpers

These helpers do not:

```text
build Voila
create ZIP files
create installers
generate SHA256
publish GitHub releases
sign packages
implement payment
implement license activation
```
