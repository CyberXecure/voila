# Voila Package Legal Files Integration Plan

Milestone:

```text
v0.3.11-voila-package-legal-files-integration-plan
```

## Purpose

Plan how Voila legal files should be included in future Windows ZIP or installer packages.

This milestone is documentation-only.

It does not:

```text
change runtime behavior
change backend behavior
change frontend behavior
change dependencies
rebuild any package
change GitHub visibility
add payment or activation
provide final legal approval
```

---

## Background

Voila is moving toward:

```text
proprietary product
private development
controlled public releases
clear beta terms
future Supporter / Pro licensing
```

Recent legal/commercial milestones prepared:

```text
LICENSE.txt
BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md
docs/legal/VOILA-BETA-EULA-DRAFT.md
docs/legal/VOILA-PACKAGE-LEGAL-FILES-CHECKLIST.md
docs/commercial/VOILA-CONTROLLED-PUBLIC-RELEASE-POLICY.md
```

The next step is to define how these files should be mapped into future Windows packages.

---

## Recommended package legal folder

Future Windows packages should include:

```text
legal/
  EULA.txt
  LICENSE.txt
  BETA-TERMS.md
  THIRD-PARTY-NOTICES.md
```

Optional later files:

```text
legal/
  PRIVACY-NOTICE.md
  SUPPORTER-TERMS.md
  PRO-LICENSE-ADDENDUM.md
  COMMERCIAL-USE-NOTICE.md
```

---

## Package root files

Recommended root files:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
legal/
```

For selected tester builds:

```text
README-TESTERS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
legal/
```

---

## Integration principles

Legal files should be:

```text
included in every public/tester package
easy to find
referenced from README
referenced from release notes
consistent with release type
not mixed with internal commercial planning docs
not replaced by GitHub-only links
```

Package users should be able to read the terms even if they are offline.

---

## Source-to-package mapping

Recommended mapping:

```text
docs/legal/VOILA-BETA-EULA-DRAFT.md -> legal/EULA.txt after review
LICENSE.txt -> legal/LICENSE.txt
BETA-TERMS.md -> legal/BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md -> legal/THIRD-PARTY-NOTICES.md
```

Do not include draft/planning docs in public packages unless intentionally intended.

---

## README wording

Package README should include:

```text
Before using Voila, review the files in the legal/ folder.

This package includes:
- legal/EULA.txt
- legal/LICENSE.txt
- legal/BETA-TERMS.md
- legal/THIRD-PARTY-NOTICES.md

Voila is proprietary beta software. Do not redistribute, repackage, sell, or use commercially unless the applicable release notes or a written agreement allow it.
```

---

## Release notes wording

Release notes should include:

```text
Release type:
Package version:
Intended audience:
Runtime package: Yes / No
Page-count limits:
Commercial use:
Redistribution:
Legal files:
Checksum:
```

Recommended legal wording:

```text
This package includes legal terms in the legal/ folder. Review EULA.txt, LICENSE.txt, BETA-TERMS.md, and THIRD-PARTY-NOTICES.md before use.
```

---

## Before package rebuild

Before rebuilding a future package:

```text
[ ] EULA draft reviewed for intended release type
[ ] LICENSE.txt checked
[ ] BETA-TERMS.md checked
[ ] THIRD-PARTY-NOTICES.md updated enough for package type
[ ] release notes include package type
[ ] README references legal folder
[ ] legal folder copied into package
[ ] no internal commercial docs copied into package
[ ] package smoke tested
[ ] SHA256 generated
```

---

## Completion criteria

This milestone is complete when the package legal integration approach is documented and ready to be used by a later packaging milestone.

This milestone should not rebuild a package.
