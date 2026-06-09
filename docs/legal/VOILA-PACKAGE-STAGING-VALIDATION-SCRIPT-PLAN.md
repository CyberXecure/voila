# Voila Package Staging Validation Script Plan

Milestone:

```text
v0.3.18-voila-package-staging-validation-script-plan
```

## Purpose

Plan a future release helper script that validates a Voila Windows package staging folder before ZIP or installer creation.

This milestone is documentation-only.

It does not add the validation script yet.

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

## Background

Previous milestones added and documented the package legal file copy workflow:

```text
scripts/release/copy-package-legal-files.ps1
docs/legal/VOILA-PACKAGE-STAGING-VALIDATION-PLAN.md
docs/legal/VOILA-PACKAGE-STAGING-VALIDATION-SPEC.md
```

The next implementation step should be a validation helper script, but this milestone only plans that script.

---

## Future script goal

The future validation script should validate a package staging folder for:

```text
legal folder
required legal files
README or tester instructions
release notes
start/stop launchers
release type wording
known limits
exclusion rules
secrets/private files
commercial gate readiness
```

---

## Recommended future script path

```text
scripts/release/validate-package-staging.ps1
```

---

## Proposed command

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

## Proposed parameters

### PackageRoot

Required.

Purpose:

```text
package staging folder to validate
```

Validation:

```text
must exist
must be directory
must not be repository root
must not be docs/
must not be scripts/
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

### Strict

Optional.

Purpose:

```text
treat advisory warnings as failures
```

### ValidateLegalOnly

Optional.

Purpose:

```text
validate legal/ folder and legal references only
```

### SkipLauncherCheck

Optional later.

Purpose:

```text
allow documentation-only or non-runnable package staging validation
```

---

## Required legal checks

Check:

```text
[ ] legal/ exists
[ ] legal/EULA.txt exists
[ ] legal/LICENSE.txt exists
[ ] legal/BETA-TERMS.md exists
[ ] legal/THIRD-PARTY-NOTICES.md exists
[ ] legal files are not empty
```

Optional content checks:

```text
[ ] EULA.txt contains Voila
[ ] LICENSE.txt contains proprietary or all rights reserved wording
[ ] BETA-TERMS.md contains beta wording
[ ] THIRD-PARTY-NOTICES.md contains third-party wording
```

---

## README checks

Accept one of:

```text
README-WINDOWS.txt
README-TESTERS.txt
README.md
```

Check:

```text
[ ] README exists
[ ] README references legal/
[ ] README references EULA.txt
[ ] README references BETA-TERMS.md
[ ] README references THIRD-PARTY-NOTICES.md
[ ] README includes start instructions
[ ] README includes stop instructions
```

For tester builds:

```text
[ ] README contains tester wording
[ ] README contains feedback instructions
[ ] README contains no redistribution wording
```

---

## Release notes checks

Expected:

```text
RELEASE-NOTES.txt
```

Check:

```text
[ ] release notes exist
[ ] release type is clear
[ ] version is clear
[ ] intended audience is clear
[ ] runtime package status is clear
[ ] legal folder is referenced
[ ] known limitations are listed
[ ] SHA256 publication step is expected
```

---

## Launcher checks

Expected for runnable Windows packages:

```text
START-VOILA.bat
STOP-VOILA.bat
```

Check:

```text
[ ] start launcher exists
[ ] stop launcher exists
[ ] README references start launcher
[ ] README references stop launcher
```

For non-runnable documentation-only package staging, launcher checks may be skipped only if explicitly requested.

---

## Exclusion checks

The script should fail if package staging includes:

```text
.env
*.pem
*.key
*.pfx
secrets/
private/
docs/commercial/
repo privacy transition docs
pricing assumptions
activation implementation notes
private QA notes
private PDFs
customer documents
generated private content
```

The script may warn if package staging includes:

```text
docs/legal/*PLAN.md
docs/legal/*CHECKLIST.md
docs/legal/*OUTLINE.md
```

---

## Output format

Recommended console output:

```text
=== VOILA PACKAGE STAGING VALIDATION ===
Package root:
Release type:

Checks:
- Package root: PASS / FAIL
- Legal files: PASS / FAIL
- README: PASS / WARN / FAIL
- Release notes: PASS / WARN / FAIL
- Launchers: PASS / WARN / FAIL
- Exclusions: PASS / FAIL

Result: PASS / CONDITIONAL / FAIL
```

---

## Exit behavior

Recommended:

```text
0 = pass
1 = fail
2 = conditional/warnings in strict mode
```

---

## What the future script must not do

The future script must not:

```text
copy legal files
modify package contents
build package
create ZIP
create installer
generate SHA256
publish release
change runtime code
change dependencies
```

The validation script should validate only.

---

## Recommended next milestone

```text
v0.3.19-voila-package-staging-validation-script
```

This next milestone can implement the actual script.
