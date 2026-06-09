# Voila Windows Package Legal Folder Specification

## Purpose

Define the expected `legal/` folder for future Voila Windows packages.

This specification is planning-only and does not change any package.

---

## Required folder

Every controlled public package should include:

```text
legal/
```

---

## Required files

Minimum required files:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

---

## File purpose

### legal/EULA.txt

Purpose:

```text
end user license terms for the package
beta restrictions
commercial-use boundary
generated content disclaimer
no warranty / liability limitation
```

Source:

```text
reviewed version of docs/legal/VOILA-BETA-EULA-DRAFT.md
```

### legal/LICENSE.txt

Purpose:

```text
all-rights-reserved/proprietary license notice
copyright notice
redistribution restrictions
```

Source:

```text
LICENSE.txt
```

### legal/BETA-TERMS.md

Purpose:

```text
beta-specific usage rules
tester/demo boundaries
feedback and document-safety notes
```

Source:

```text
BETA-TERMS.md
```

### legal/THIRD-PARTY-NOTICES.md

Purpose:

```text
third-party components
licenses
attributions
redistribution notices
pending review notes
```

Source:

```text
docs/legal/THIRD-PARTY-NOTICES.md
```

---

## Optional future files

```text
legal/PRIVACY-NOTICE.md
legal/SUPPORTER-TERMS.md
legal/PRO-LICENSE-ADDENDUM.md
legal/COMMERCIAL-USE-NOTICE.md
legal/OPEN-SOURCE-NOTICES.md
```

---

## File format

Recommended:

```text
plain text or markdown
UTF-8
readable offline
no external link required for core terms
```

External links may be included, but the package should still contain the core terms.

---

## Excluded files

Do not include:

```text
internal commercial strategy docs
repo privacy transition docs
pricing assumptions
license key implementation notes
private QA notes
private roadmap documents
unreviewed legal drafts unless clearly marked
```

---

## Package validation

Package validation should check:

```text
[ ] legal folder exists
[ ] EULA.txt exists
[ ] LICENSE.txt exists
[ ] BETA-TERMS.md exists
[ ] THIRD-PARTY-NOTICES.md exists
[ ] README references legal folder
[ ] release notes reference legal folder
[ ] no internal docs included
```
