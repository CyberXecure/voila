# Voila Legal File Copy Script Implementation Notes

Milestone:

```text
v0.3.14-voila-package-legal-files-copy-script
```

## Purpose

Document the implemented packaging helper script:

```text
scripts/release/copy-package-legal-files.ps1
```

The script copies required legal files into a package staging folder.

---

## Scope

This milestone adds a release/package helper script only.

It does not:

```text
change runtime behavior
change backend behavior
change frontend behavior
change dependencies
rebuild a package
create a release
upload assets
change GitHub visibility
add payment/licensing implementation
provide final legal approval
```

---

## Script command

Example:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot .\.release-cache\voila-package `
  -ReleaseType PublicBeta
```

Dry run:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot .\.release-cache\voila-package `
  -ReleaseType PublicBeta `
  -WhatIf
```

Validation-only mode:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot .\.release-cache\voila-package `
  -ReleaseType PublicBeta `
  -ValidateOnly
```

---

## Required package output

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

---

## Default source mapping

```text
docs/legal/VOILA-BETA-EULA-DRAFT.md -> legal/EULA.txt
LICENSE.txt -> legal/LICENSE.txt
BETA-TERMS.md -> legal/BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md -> legal/THIRD-PARTY-NOTICES.md
```

---

## Safety behavior

The script:

```text
requires PackageRoot
requires ReleaseType
rejects repository root as PackageRoot
validates required source files
creates legal/ in the package staging folder
copies required legal files
validates required output files
supports -WhatIf
supports -ValidateOnly
```

---

## Release integration point

Recommended order in a future packaging flow:

```text
1. create package staging folder
2. copy runtime files
3. copy README / release notes
4. run scripts/release/copy-package-legal-files.ps1
5. run package validation
6. create ZIP / installer
7. generate SHA256
8. run smoke test
```

---

## Notes

The script is not automatically wired into any package build yet.

A later milestone can integrate it into the Windows package build pipeline.
