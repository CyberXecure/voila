# Voila Package Staging Validation Specification

## Purpose

Specify the expected behavior of a future package staging validation helper.

This is not an implementation document.

---

## Proposed script path

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

---

## Proposed parameters

### PackageRoot

Required.

Purpose:

```text
path to package staging folder
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
fail on warnings that would otherwise be advisory
```

### ValidateLegalOnly

Optional.

Purpose:

```text
validate only legal/ files and legal references
```

---

## Required checks

### Package root

```text
[ ] exists
[ ] directory
[ ] safe path
```

### Legal files

```text
[ ] legal/EULA.txt exists
[ ] legal/LICENSE.txt exists
[ ] legal/BETA-TERMS.md exists
[ ] legal/THIRD-PARTY-NOTICES.md exists
```

### Documentation files

At least one README:

```text
README-WINDOWS.txt
README-TESTERS.txt
README.md
```

Recommended release notes:

```text
RELEASE-NOTES.txt
```

### Launchers

Expected for runnable Windows package:

```text
START-VOILA.bat
STOP-VOILA.bat
```

For documentation-only packages, launcher check may be advisory.

---

## Content checks

Recommended content checks:

```text
EULA.txt contains "Voila"
LICENSE.txt contains "All rights reserved" or "proprietary"
BETA-TERMS.md contains "beta"
THIRD-PARTY-NOTICES.md contains "third-party"
README references legal/
README references start and stop instructions
RELEASE-NOTES references release type
```

---

## Exclusion checks

Fail if package contains:

```text
.env
*.pem
*.key
*.pfx
docs/commercial/
private/
secrets/
*.sqlite with private data
test private PDFs
```

Advisory warning if package contains:

```text
docs/legal/*PLAN.md
docs/legal/*CHECKLIST.md
docs/legal/*OUTLINE.md
```

---

## Output format

Recommended output:

```text
=== VOILA PACKAGE STAGING VALIDATION ===
Package root:
Release type:
Checks:
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
0 = Pass
1 = Fail
2 = Conditional / warnings in strict mode
```

---

## Release type differences

### PublicBeta

Required:

```text
legal files
README
release notes
start/stop launchers
public beta wording
known limitations
```

### TesterDemo

Required:

```text
legal files
tester README
release notes
tester-only wording
page-count limit wording
no redistribution wording
```

### Supporter

Required later:

```text
legal files
Supporter terms or reference
release notes
payment/license wording
```

### Pro

Required later:

```text
legal files
Pro terms or addendum
commercial use rights
support/contact path
```

---

## Not implemented yet

This document does not add:

```text
validate-package-staging.ps1
release package
installer
GitHub release
SHA256 generator
smoke test automation
```
