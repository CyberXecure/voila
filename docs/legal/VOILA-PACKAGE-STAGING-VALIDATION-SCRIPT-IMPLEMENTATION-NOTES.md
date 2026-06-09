# Voila Package Staging Validation Script Implementation Notes

Milestone:

```text
v0.3.19-voila-package-staging-validation-script
```

## Purpose

Document the implemented package staging validation helper script:

```text
scripts/release/validate-package-staging.ps1
```

The script validates a Voila Windows package staging folder before ZIP or installer creation.

---

## Scope

This milestone adds a release/package validation helper script only.

It does not:

```text
change runtime behavior
change backend behavior
change frontend behavior
change dependencies
rebuild a package
create a release
upload release assets
change GitHub visibility
add payment or activation
provide final legal approval
```

---

## Script command

Example:

```powershell
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot .\.release-cache\voila-package `
  -ReleaseType PublicBeta
```

Strict mode:

```powershell
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot .\.release-cache\voila-package `
  -ReleaseType PublicBeta `
  -Strict
```

Legal-only validation:

```powershell
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot .\.release-cache\voila-package `
  -ReleaseType PublicBeta `
  -ValidateLegalOnly
```

---

## Checks implemented

The script checks:

```text
package root exists and is safe
legal/EULA.txt exists and is non-empty
legal/LICENSE.txt exists and is non-empty
legal/BETA-TERMS.md exists and is non-empty
legal/THIRD-PARTY-NOTICES.md exists and is non-empty
legal file content indicators
README presence and legal references
release notes presence and checksum/type references
START-VOILA.bat
STOP-VOILA.bat
forbidden files/folders
planning docs advisory
```

---

## Result behavior

The script produces:

```text
Result: PASS
Result: CONDITIONAL
Result: FAIL
```

Failures throw an error.

Warnings are allowed unless `-Strict` is used.

---

## Relationship to legal copy script

Recommended package flow:

```text
1. create package staging folder
2. copy runtime files and launchers
3. copy README and release notes
4. run scripts/release/copy-package-legal-files.ps1
5. run scripts/release/validate-package-staging.ps1
6. create ZIP or installer
7. generate SHA256
8. run smoke test
```
