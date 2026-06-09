# Voila Legal Copy Script Validation Plan

## Purpose

Plan validation checks for a future legal file copy script.

This document is planning-only and does not add validation code.

---

## Validation phases

The future script should validate in three phases:

```text
pre-copy validation
copy validation
post-copy validation
```

---

## Pre-copy validation

Check:

```text
[ ] PackageRoot parameter is provided
[ ] PackageRoot exists
[ ] PackageRoot is a directory
[ ] PackageRoot is not repository root
[ ] ReleaseType parameter is valid
[ ] required source files exist
```

Required source files:

```text
docs/legal/VOILA-BETA-EULA-DRAFT.md
LICENSE.txt
BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md
```

---

## Copy validation

Check:

```text
[ ] legal/ output folder exists or is created
[ ] EULA source copies to legal/EULA.txt
[ ] LICENSE source copies to legal/LICENSE.txt
[ ] BETA-TERMS source copies to legal/BETA-TERMS.md
[ ] THIRD-PARTY-NOTICES source copies to legal/THIRD-PARTY-NOTICES.md
```

---

## Post-copy validation

Check package output:

```text
[ ] legal/EULA.txt exists
[ ] legal/LICENSE.txt exists
[ ] legal/BETA-TERMS.md exists
[ ] legal/THIRD-PARTY-NOTICES.md exists
```

Optional content checks:

```text
[ ] EULA.txt contains "Voila"
[ ] LICENSE.txt contains "All rights reserved"
[ ] BETA-TERMS.md contains "public beta"
[ ] THIRD-PARTY-NOTICES.md contains "third-party"
```

---

## Package README validation

Optional later:

```text
[ ] README-WINDOWS.txt or README-TESTERS.txt exists
[ ] README references legal/
[ ] README references EULA.txt
[ ] README references BETA-TERMS.md
[ ] README references THIRD-PARTY-NOTICES.md
```

---

## Release notes validation

Optional later:

```text
[ ] RELEASE-NOTES.txt exists
[ ] release type is listed
[ ] legal folder is referenced
[ ] checksum instructions are present
[ ] package limits are clear
```

---

## Failure behavior

Validation should fail loudly when:

```text
required legal file is missing
copy output is incomplete
package root is invalid
internal docs are about to be copied
release type is unknown
```

---

## Future automated test idea

A later implementation milestone can add a dry-run package staging test:

```text
create temporary package folder
run script with -WhatIf
run script without -WhatIf
verify legal files exist
delete temporary package folder
```

---

## Completion criteria for implementation milestone

The future script implementation should be considered complete when:

```text
[ ] script exists
[ ] dry run works
[ ] copy mode works
[ ] missing source failure works
[ ] invalid package root failure works
[ ] required output validation works
[ ] script is documented
```
