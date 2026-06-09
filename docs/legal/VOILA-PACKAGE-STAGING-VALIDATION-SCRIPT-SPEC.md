# Voila Package Staging Validation Script Specification

## Purpose

Specify detailed behavior for the future Voila package staging validation script.

This file is not the implementation.

---

## Proposed script

```text
scripts/release/validate-package-staging.ps1
```

---

## Responsibilities

The script should:

```text
validate package root
validate legal files
validate README or tester instructions
validate release notes
validate launchers
validate exclusions
return clear pass/fail status
```

The script should not:

```text
copy files
modify files
build ZIP
create installer
publish release
```

---

## Validation groups

### 1. Package root

Required checks:

```text
PackageRoot parameter present
PackageRoot exists
PackageRoot is directory
PackageRoot is not repository root
PackageRoot is not docs/
PackageRoot is not scripts/
```

### 2. Legal files

Required:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

Each required file must:

```text
exist
be a file
have length greater than zero
```

### 3. README

Accepted filenames:

```text
README-WINDOWS.txt
README-TESTERS.txt
README.md
```

Required content indicators:

```text
Voila
legal/
EULA
BETA-TERMS
THIRD-PARTY-NOTICES
START
STOP
```

### 4. Release notes

Recommended filename:

```text
RELEASE-NOTES.txt
```

Required content indicators:

```text
Release type
Version
Legal
Limitations
SHA256
```

### 5. Launchers

Required for runnable packages:

```text
START-VOILA.bat
STOP-VOILA.bat
```

This can be advisory for Internal or documentation-only staging.

### 6. Exclusions

Fail if any matching files/folders are present:

```text
.env
*.pem
*.key
*.pfx
secrets
private
docs/commercial
```

Warn if any internal planning docs are present:

```text
*PLAN.md
*CHECKLIST.md
*OUTLINE.md
```

---

## Result model

Use these result values:

```text
PASS
WARN
FAIL
```

Overall result:

```text
PASS:
No failures and no warnings.

CONDITIONAL:
No failures, but warnings exist.

FAIL:
One or more required checks failed.
```

---

## Release type rules

### PublicBeta

Required:

```text
legal files
README
release notes
launchers
public beta wording
known limitations
```

### TesterDemo

Required:

```text
legal files
tester README
release notes
launchers
tester-only wording
page-limit wording
no-redistribution wording
```

### Supporter

Required later:

```text
legal files
README
release notes
launchers
Supporter terms or reference
package limits
```

### Pro

Required later:

```text
legal files
README
release notes
launchers
Pro terms or reference
commercial/internal use wording
```

---

## Implementation notes

The future script should be simple and deterministic.

Recommended functions:

```text
Resolve-RequiredDirectory
Assert-SafePackageRoot
Test-RequiredFile
Test-FileContainsAny
Test-ForbiddenPatterns
Write-CheckResult
Complete-Validation
```

---

## Manual validation equivalent

Until the script exists, reviewers can manually check:

```powershell
Get-ChildItem <package-root>\legal
Test-Path <package-root>\README-WINDOWS.txt
Test-Path <package-root>\RELEASE-NOTES.txt
Test-Path <package-root>\START-VOILA.bat
Test-Path <package-root>\STOP-VOILA.bat
```
