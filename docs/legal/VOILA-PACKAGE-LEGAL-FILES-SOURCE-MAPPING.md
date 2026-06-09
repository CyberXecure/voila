# Voila Package Legal Files Source Mapping

## Purpose

Map repository legal files to their intended locations in future Windows packages.

This mapping avoids confusion between:

```text
source repository docs
legal drafts
package-ready legal files
internal planning docs
```

---

## Mapping table

```text
Repository source file                                  Package path
--------------------------------------------------------------------------------
docs/legal/VOILA-BETA-EULA-DRAFT.md                     legal/EULA.txt
LICENSE.txt                                             legal/LICENSE.txt
BETA-TERMS.md                                           legal/BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md                       legal/THIRD-PARTY-NOTICES.md
```

---

## Draft vs package-ready status

### Draft files

These are draft/planning files and should not be shipped directly unless reviewed:

```text
docs/legal/VOILA-BETA-EULA-DRAFT.md
docs/legal/VOILA-EULA-DRAFT-OUTLINE.md
docs/legal/VOILA-WINDOWS-PACKAGE-EULA-PLAN.md
docs/legal/VOILA-THIRD-PARTY-LICENSE-AUDIT-PLAN.md
docs/commercial/*.md
```

### Package-ready files

These are intended package filenames:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

---

## Conversion notes

Before packaging:

```text
review beta EULA draft
copy reviewed content to legal/EULA.txt
copy LICENSE.txt to legal/LICENSE.txt
copy BETA-TERMS.md to legal/BETA-TERMS.md
copy updated THIRD-PARTY-NOTICES.md to legal/THIRD-PARTY-NOTICES.md
```

---

## Release type differences

### Public Beta Runtime Package

```text
use beta EULA
use beta terms
state public beta purpose
state non-commercial/evaluation limits if applicable
```

### Tester Demo Build

```text
use beta EULA
use beta terms
state tester-only intent
state page-count limit
state no redistribution
```

### Supporter Build

```text
use reviewed EULA
add Supporter terms later
state personal/internal use rights
state package limits
```

### Pro Build

```text
use reviewed EULA or Pro addendum
state commercial/internal use rights
state Pro-specific limits/features
```

---

## Safety rule

Do not include commercial strategy files in public packages.

Examples to exclude:

```text
docs/commercial/VOILA-SUPPORTER-PRO-LICENSING-PLAN.md
docs/commercial/VOILA-PROPRIETARY-PRODUCT-STRATEGY.md
docs/commercial/VOILA-PRIVATE-REPO-AND-CONTROLLED-RELEASE-PLAN.md
docs/commercial/VOILA-BETA-EULA-COMMERCIAL-READINESS-NOTES.md
```
