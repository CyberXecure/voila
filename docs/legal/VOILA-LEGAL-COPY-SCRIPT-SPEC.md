# Voila Legal Copy Script Specification

## Purpose

Specify the behavior of a future legal file copy helper script for Voila Windows packages.

This document is not the script implementation.

---

## Proposed script path

```text
scripts/release/copy-package-legal-files.ps1
```

---

## Proposed command

Example:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot .\.release-cache\voila-package `
  -ReleaseType PublicBeta
```

With dry run:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot .\.release-cache\voila-package `
  -ReleaseType PublicBeta `
  -WhatIf
```

---

## Parameters

### PackageRoot

Required.

Purpose:

```text
path to the package staging folder
```

Validation:

```text
must exist
must be a directory
should not be repository root
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

Purpose:

```text
prints release type
enables release-type-specific validation later
```

### Force

Optional.

Purpose:

```text
overwrite existing legal files
```

### WhatIf

Optional.

Purpose:

```text
show planned copy operations without writing files
```

### ValidateOnly

Optional later.

Purpose:

```text
validate legal folder without copying
```

---

## Copy operations

The script should copy:

```text
docs/legal/VOILA-BETA-EULA-DRAFT.md
```

to:

```text
legal/EULA.txt
```

Copy:

```text
LICENSE.txt
```

to:

```text
legal/LICENSE.txt
```

Copy:

```text
BETA-TERMS.md
```

to:

```text
legal/BETA-TERMS.md
```

Copy:

```text
docs/legal/THIRD-PARTY-NOTICES.md
```

to:

```text
legal/THIRD-PARTY-NOTICES.md
```

---

## Required output

After success:

```text
legal/
  EULA.txt
  LICENSE.txt
  BETA-TERMS.md
  THIRD-PARTY-NOTICES.md
```

---

## Error handling

The script should stop with an error when:

```text
PackageRoot does not exist
PackageRoot is not a directory
a required source file is missing
a copy operation fails
a required output file is missing after copy
PackageRoot appears to be the repository root
```

---

## Logging

The script should print:

```text
package root
release type
legal output folder
source files
destination files
copy results
validation results
```

---

## Exit codes

Recommended:

```text
0 = success
1 = validation failure
2 = missing source file
3 = invalid package root
4 = copy failure
```

---

## Files excluded by design

The script should not copy:

```text
docs/commercial/*.md
docs/legal/*PLAN.md
docs/legal/*CHECKLIST.md
docs/legal/*OUTLINE.md
repo privacy docs
supporter/pro planning docs
pricing docs
internal QA docs
```

---

## Future release-type validation

Later validation may check:

```text
PublicBeta requires beta EULA and beta terms
TesterDemo requires tester README references
Supporter requires Supporter terms
Pro requires Pro addendum
```
