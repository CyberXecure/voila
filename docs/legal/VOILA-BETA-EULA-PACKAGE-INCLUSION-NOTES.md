# Voila Beta EULA Package Inclusion Notes

## Purpose

Define how the Voila beta EULA draft could be included in future Windows ZIP or installer packages.

This document is planning-only and does not rebuild packages.

---

## Recommended package layout

For a ZIP-style beta package:

```text
Voila/
  START-VOILA.bat
  STOP-VOILA.bat
  README-WINDOWS.txt
  RELEASE-NOTES.txt
  legal/
    EULA.txt
    LICENSE.txt
    BETA-TERMS.md
    THIRD-PARTY-NOTICES.md
```

For tester demo builds:

```text
Voila/
  README-TESTERS.txt
  RELEASE-NOTES.txt
  legal/
    EULA.txt
    BETA-TERMS.md
    THIRD-PARTY-NOTICES.md
```

---

## Recommended EULA filename

Use:

```text
legal/EULA.txt
```

The source draft can remain:

```text
docs/legal/VOILA-BETA-EULA-DRAFT.md
```

During package preparation, convert or copy the reviewed draft into:

```text
legal/EULA.txt
```

---

## README reference wording

Recommended package README wording:

```text
By using this Voila beta package, you agree to the beta terms and EULA included in the legal/ folder. Voila is proprietary beta software. Do not redistribute, repackage, sell, or use commercially unless the applicable release notes or a written agreement allow it.
```

---

## Release notes reference wording

Recommended release notes wording:

```text
This package includes legal terms in the legal/ folder. Review EULA.txt, BETA-TERMS.md, and THIRD-PARTY-NOTICES.md before using the package.
```

---

## Current beta package approach

For current ZIP-style packages:

```text
include EULA as a file
reference EULA in README
reference EULA in release notes
state package type clearly
state page-count limits clearly, if any
```

---

## Future installer approach

For a future installer:

```text
show EULA during installation
require acceptance before installation
install legal files locally
provide Terms / License link in About screen later
```

---

## Do not include in public package

Avoid including:

```text
internal legal drafts
commercial roadmap docs
pricing assumptions
private repo transition docs
license key implementation notes
internal QA notes
unreviewed third-party inventory files
```

---

## Package inclusion checklist

```text
[ ] EULA draft reviewed
[ ] EULA copied to legal/EULA.txt
[ ] BETA-TERMS.md included
[ ] LICENSE.txt included
[ ] THIRD-PARTY-NOTICES.md included
[ ] README references legal folder
[ ] release notes reference legal folder
[ ] package type is clear
[ ] page-count limits are clear
[ ] no private/internal docs included
```
