# Voila Package Staging Validation Plan

Milestone:

```text
v0.3.17-voila-package-legal-files-package-validation-plan
```

## Purpose

Plan a complete validation pass for a future Voila Windows package staging folder before ZIP or installer creation.

This milestone is documentation-only.

It does not:

```text
add a validation script
rebuild a package
create a release
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

Voila now has a release helper script:

```text
scripts/release/copy-package-legal-files.ps1
```

The helper copies legal files into a package staging folder:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

The helper has also been smoke-tested.

The next step is to define what a package-level validation gate should check before a ZIP or installer is created.

---

## Validation goal

A package staging folder should be considered ready only after validating:

```text
legal files
README / tester instructions
release notes
package type labels
known limits
no internal-only docs
no secrets
no private documents
start/stop launchers
SHA256 readiness
smoke test readiness
```

---

## Recommended validation order

```text
1. validate package root
2. validate legal folder
3. validate README / tester instructions
4. validate release notes
5. validate launchers
6. validate package type wording
7. validate exclusion rules
8. validate smoke-test readiness
9. validate checksum readiness
```

---

## Package root validation

Check:

```text
[ ] package staging folder exists
[ ] package staging folder is not the repository root
[ ] package staging folder is not docs/
[ ] package staging folder is not scripts/
[ ] package staging folder is disposable/staging-only
```

---

## Legal folder validation

Required files:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

Check:

```text
[ ] legal/ exists
[ ] EULA.txt exists
[ ] LICENSE.txt exists
[ ] BETA-TERMS.md exists
[ ] THIRD-PARTY-NOTICES.md exists
[ ] files are readable
[ ] files are not empty
[ ] files are package-local, not links only
```

---

## README validation

Expected one of:

```text
README-WINDOWS.txt
README-TESTERS.txt
README.md
```

Check:

```text
[ ] README exists
[ ] README identifies Voila
[ ] README identifies package type
[ ] README references legal/
[ ] README references EULA.txt
[ ] README references BETA-TERMS.md
[ ] README references THIRD-PARTY-NOTICES.md
[ ] README explains how to start Voila
[ ] README explains how to stop Voila
[ ] README includes feedback/contact path if tester/public package
```

---

## Release notes validation

Expected:

```text
RELEASE-NOTES.txt
```

Check:

```text
[ ] release notes exist
[ ] version is clear
[ ] release type is clear
[ ] intended audience is clear
[ ] runtime package status is clear
[ ] page-count limits are clear if applicable
[ ] commercial use status is clear
[ ] redistribution status is clear
[ ] legal folder is referenced
[ ] SHA256 publication step is expected
```

---

## Launcher validation

Expected for Windows package:

```text
START-VOILA.bat
STOP-VOILA.bat
```

or documented equivalents.

Check:

```text
[ ] start launcher exists
[ ] stop launcher exists
[ ] README references start launcher
[ ] README references stop launcher
[ ] launcher names match README
```

---

## Exclusion validation

Ensure package does not include:

```text
docs/commercial/
repo privacy transition docs
pricing assumptions
activation implementation notes
private QA notes
local helper scripts not intended for package
private PDFs
customer documents
generated private content
API keys
tokens
.env files
machine-specific secrets
```

---

## Validation result

A future validation script should produce:

```text
Pass
Conditional
Fail
```

Definitions:

```text
Pass:
All required files and checks pass.

Conditional:
Package can be reviewed manually, but one or more advisory checks are incomplete.

Fail:
Required files, legal files, launchers, or release notes are missing.
```

---

## Recommended future script

A later milestone may implement:

```text
scripts/release/validate-package-staging.ps1
```

Suggested command:

```powershell
.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta
```

---

## Completion criteria

This milestone is complete when package staging validation requirements are documented.

It should not rebuild a package or add the validation script yet.
