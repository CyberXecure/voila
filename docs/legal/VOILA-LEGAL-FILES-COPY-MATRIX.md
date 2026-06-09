# Voila Legal Files Copy Matrix

## Purpose

Define a clear matrix for copying legal source files into package-ready legal files.

This is planning-only and does not copy package files.

---

## Copy matrix

```text
Repository source                                Package output
--------------------------------------------------------------------------------
docs/legal/VOILA-BETA-EULA-DRAFT.md              legal/EULA.txt
LICENSE.txt                                      legal/LICENSE.txt
BETA-TERMS.md                                    legal/BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md                legal/THIRD-PARTY-NOTICES.md
```

---

## Source file status

### docs/legal/VOILA-BETA-EULA-DRAFT.md

Package output:

```text
legal/EULA.txt
```

Status:

```text
draft for review
not final legal advice
needs review before broader distribution
```

Notes:

```text
copy only after review for the intended release type
rename to EULA.txt in package
```

### LICENSE.txt

Package output:

```text
legal/LICENSE.txt
```

Status:

```text
repository root license notice
all-rights-reserved/proprietary beta notice
```

Notes:

```text
copy as-is unless updated for the release type
```

### BETA-TERMS.md

Package output:

```text
legal/BETA-TERMS.md
```

Status:

```text
beta terms
applies to public beta / tester / demo builds unless changed
```

Notes:

```text
copy as-is unless package-specific beta terms are prepared
```

### docs/legal/THIRD-PARTY-NOTICES.md

Package output:

```text
legal/THIRD-PARTY-NOTICES.md
```

Status:

```text
placeholder / in-progress notices
not a completed audit yet
```

Notes:

```text
must be improved before commercial Supporter / Pro distribution
```

---

## Package output validation

Expected package legal folder:

```text
legal/
  EULA.txt
  LICENSE.txt
  BETA-TERMS.md
  THIRD-PARTY-NOTICES.md
```

Validation:

```text
[ ] all four files exist
[ ] files are readable
[ ] files are UTF-8/plain text or markdown
[ ] release notes reference the legal folder
[ ] README references the legal folder
```

---

## Internal docs exclusion matrix

Do not copy:

```text
docs/legal/VOILA-EULA-DRAFT-OUTLINE.md
docs/legal/VOILA-WINDOWS-PACKAGE-EULA-PLAN.md
docs/legal/VOILA-PACKAGE-LEGAL-FILES-CHECKLIST.md
docs/legal/VOILA-PACKAGE-LEGAL-FILES-INTEGRATION-PLAN.md
docs/legal/VOILA-PACKAGE-LEGAL-FILES-COPY-PLAN.md
docs/commercial/*.md
```

Reason:

```text
these are planning/internal strategy docs, not package terms
```
