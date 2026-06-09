# Voila Package Staging Validation Script Test Plan

## Purpose

Plan how the future package staging validation script should be tested.

This is documentation-only.

---

## Future script under test

```text
scripts/release/validate-package-staging.ps1
```

---

## Test scenarios

### 1. Valid public beta package staging

Setup:

```text
package root exists
legal files exist
README exists
RELEASE-NOTES exists
START-VOILA.bat exists
STOP-VOILA.bat exists
no forbidden files
```

Expected:

```text
PASS
exit code 0
```

### 2. Missing legal folder

Setup:

```text
legal/ missing
```

Expected:

```text
FAIL
missing legal folder reported
```

### 3. Missing EULA

Setup:

```text
legal/EULA.txt missing
```

Expected:

```text
FAIL
missing EULA reported
```

### 4. Missing README

Setup:

```text
no README-WINDOWS.txt
no README-TESTERS.txt
no README.md
```

Expected:

```text
FAIL or WARN depending release type
```

### 5. Missing release notes

Setup:

```text
RELEASE-NOTES.txt missing
```

Expected:

```text
WARN or FAIL depending release type and Strict mode
```

### 6. Missing launchers

Setup:

```text
START-VOILA.bat missing
STOP-VOILA.bat missing
```

Expected:

```text
FAIL for PublicBeta / TesterDemo runnable package
WARN for Internal if launcher check skipped
```

### 7. Forbidden secret file

Setup:

```text
.env exists
```

Expected:

```text
FAIL
forbidden file reported
```

### 8. Internal commercial docs included

Setup:

```text
docs/commercial/ exists in package
```

Expected:

```text
FAIL
internal commercial docs reported
```

### 9. Strict mode warnings

Setup:

```text
advisory warning exists
-Strict provided
```

Expected:

```text
FAIL or exit code 2
```

---

## Temporary staging test approach

A future smoke test can:

```text
create temp folder
create minimal legal files
create minimal README
create minimal RELEASE-NOTES
create dummy START/STOP launchers
run validation script
delete temp folder
```

---

## Completion criteria for implementation

The future implementation is complete when:

```text
valid package staging passes
missing legal files fail
forbidden files fail
README/release notes checks work
launcher checks work
Strict mode works
documentation is updated
```
