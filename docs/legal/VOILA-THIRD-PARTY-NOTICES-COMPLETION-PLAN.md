# Voila Third-Party Notices Completion Plan

## Purpose

Plan how to turn the current third-party notices placeholder into a useful package-ready notice file.

This does not complete the audit. It defines the work needed.

---

## Current status

Voila already has a third-party notices placeholder:

```text
docs/legal/THIRD-PARTY-NOTICES.md
```

That file makes the license/commercial-readiness gap visible, but it is not yet a completed audit.

---

## Required improvements

Before broader distribution, update third-party notices with:

```text
component names
component versions
license names
copyright notices
license text or license links
redistribution notes
commercial-use notes
required attributions
package inclusion notes
```

---

## Recommended structure

Use sections:

```text
1. Runtime components
2. Backend dependencies
3. Frontend dependencies
4. OCR components
5. Language resources
6. Java/JRE components
7. PDF/image processing components
8. Fonts/icons/assets
9. Build and packaging tools
10. Unknown / pending review
```

---

## Per-component entry format

```text
## Component name

Category:
Version:
License:
Copyright:
Source:
Bundled:
Required notice:
Redistribution notes:
Commercial review status:
```

---

## Review statuses

Use:

```text
Approved
Approved with notice
Pending review
Needs replacement
Do not bundle
Development-only
Unknown
```

---

## Package inclusion recommendation

For Windows packages, include a copy of notices at:

```text
legal/THIRD-PARTY-NOTICES.md
```

Release notes should reference:

```text
See legal/THIRD-PARTY-NOTICES.md for third-party component notices.
```

---

## Completion criteria

Third-party notices are package-ready when:

```text
[ ] bundled components are listed
[ ] versions are listed
[ ] licenses are listed
[ ] required notices are included
[ ] redistribution status is reviewed
[ ] unresolved items are marked clearly
[ ] release/package docs reference the notices file
```
