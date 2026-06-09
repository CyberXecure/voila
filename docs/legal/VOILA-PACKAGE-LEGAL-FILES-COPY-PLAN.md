# Voila Package Legal Files Copy Plan

Milestone:

```text
v0.3.12-voila-package-legal-files-copy-plan
```

## Purpose

Plan how legal files should be copied or converted from repository sources into a future Voila Windows package legal folder.

This milestone is planning-only.

It does not:

```text
copy files into an actual release package
create a release package
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

The previous package legal integration plan defined the target package folder:

```text
legal/
  EULA.txt
  LICENSE.txt
  BETA-TERMS.md
  THIRD-PARTY-NOTICES.md
```

This copy plan defines the practical source-to-output flow for a future packaging milestone.

---

## Target package legal folder

Future Windows packages should contain:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

Optional future files:

```text
legal/SUPPORTER-TERMS.md
legal/PRO-LICENSE-ADDENDUM.md
legal/PRIVACY-NOTICE.md
```

---

## Source files

Current repository source files:

```text
docs/legal/VOILA-BETA-EULA-DRAFT.md
LICENSE.txt
BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md
```

Planning/reference files that should not be copied into normal public packages:

```text
docs/legal/VOILA-EULA-DRAFT-OUTLINE.md
docs/legal/VOILA-WINDOWS-PACKAGE-EULA-PLAN.md
docs/legal/VOILA-PACKAGE-LEGAL-FILES-CHECKLIST.md
docs/legal/VOILA-PACKAGE-LEGAL-FILES-INTEGRATION-PLAN.md
docs/commercial/*.md
```

---

## Recommended copy flow

### Step 1 — Review source files

Before copying:

```text
[ ] beta EULA draft reviewed
[ ] LICENSE.txt reviewed
[ ] BETA-TERMS.md reviewed
[ ] THIRD-PARTY-NOTICES.md reviewed
[ ] release type confirmed
[ ] package limits confirmed
```

### Step 2 — Prepare package legal folder

Create:

```text
legal/
```

inside the package staging folder.

### Step 3 — Copy package-ready files

Recommended copy mapping:

```text
docs/legal/VOILA-BETA-EULA-DRAFT.md -> legal/EULA.txt
LICENSE.txt -> legal/LICENSE.txt
BETA-TERMS.md -> legal/BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md -> legal/THIRD-PARTY-NOTICES.md
```

### Step 4 — Validate output

Check:

```text
[ ] legal/EULA.txt exists
[ ] legal/LICENSE.txt exists
[ ] legal/BETA-TERMS.md exists
[ ] legal/THIRD-PARTY-NOTICES.md exists
[ ] README references legal folder
[ ] release notes reference legal folder
[ ] no internal planning docs copied
```

---

## Future PowerShell copy concept

A later implementation milestone may use a script concept like:

```powershell
$packageRoot = "path\to\package-staging"
$legalOut = Join-Path $packageRoot "legal"
New-Item -ItemType Directory -Force -Path $legalOut | Out-Null

Copy-Item .\docs\legal\VOILA-BETA-EULA-DRAFT.md (Join-Path $legalOut "EULA.txt") -Force
Copy-Item .\LICENSE.txt (Join-Path $legalOut "LICENSE.txt") -Force
Copy-Item .\BETA-TERMS.md (Join-Path $legalOut "BETA-TERMS.md") -Force
Copy-Item .\docs\legal\THIRD-PARTY-NOTICES.md (Join-Path $legalOut "THIRD-PARTY-NOTICES.md") -Force
```

This milestone does not add that script to runtime or packaging.

---

## Release-type notes

### Public Beta Runtime Package

Use:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

Ensure release notes state:

```text
public beta
runtime package
non-commercial/evaluation status if applicable
page-count limits if applicable
```

### Tester Demo Build

Use same legal folder plus tester-specific README wording.

Ensure release notes state:

```text
tester/demo build
selected tester audience
page-count limit
no redistribution
feedback instructions
```

### Supporter Build

Before use:

```text
Supporter terms must exist or be referenced
third-party notices must be reviewed enough for distribution
payment/refund wording must not be misleading
```

### Pro Build

Before use:

```text
Pro commercial terms must exist
third-party license audit should be complete
commercial/internal use rights must be clear
```

---

## What not to copy

Do not copy these into normal public packages:

```text
docs/commercial/
docs/legal/*PLAN.md
docs/legal/*CHECKLIST.md
docs/legal/*OUTLINE.md
private QA notes
pricing assumptions
license activation design
repo privacy transition docs
internal roadmap docs
```

---

## Completion criteria

This milestone is complete when the copy plan, mapping, validation checklist, and readiness gate are documented.

A later implementation milestone may turn this plan into a package script.
