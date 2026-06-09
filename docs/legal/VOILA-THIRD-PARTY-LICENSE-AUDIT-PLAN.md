# Voila Third-Party License Audit Plan

Milestone:

```text
v0.3.9-voila-third-party-license-audit-plan
```

## Purpose

Plan the third-party license audit needed before broader Voila distribution, Supporter builds, Pro builds, or commercial packaging.

This milestone is documentation-only.

It does not change:

```text
runtime behavior
backend behavior
frontend behavior
dependencies
package contents
GitHub visibility
release assets
```

It also does not claim that the third-party license audit is complete.

---

## Why this audit is needed

Voila Windows packages may include or depend on third-party components such as:

```text
Python runtime
Python packages
FastAPI/backend dependencies
frontend dependencies
OCR tooling
Tesseract-related files
LanguageTool
Java/JRE runtime
PDF processing libraries
fonts
icons
browser/runtime tools
packaging tools
```

Before commercial distribution, every bundled or required third-party component should be identified and reviewed for:

```text
license name
version
copyright notice
redistribution permission
notice requirements
license text requirements
source-code-offer obligations, if any
commercial-use compatibility
package inclusion requirements
```

---

## Audit goals

The audit should answer:

```text
What third-party components are included?
What versions are included?
What license applies to each component?
What notices must be included?
Can each component be redistributed inside a Windows package?
Are there any copyleft/source-code obligations?
Are there any commercial-use restrictions?
Are license texts included where required?
Are bundled runtimes handled correctly?
```

---

## Audit scope

### Runtime components

Review:

```text
Python runtime
Java/JRE runtime
Tesseract/OCR binaries or data
LanguageTool server/files
PDF processing tools
any bundled CLI tools
```

### Backend dependencies

Review:

```text
Python packages
FastAPI-related packages
PDF/OCR/extraction libraries
language processing libraries
testing/build packages if bundled
```

### Frontend dependencies

Review:

```text
package.json
lock files
UI framework dependencies
build tooling
icons and UI assets
fonts
```

### Packaging

Review:

```text
Windows ZIP package contents
installer contents if introduced later
embedded runtimes
scripts included in package
legal folder
README / release notes references
```

---

## Audit method

Recommended approach:

```text
1. inventory all package contents
2. inventory backend dependencies
3. inventory frontend dependencies
4. inventory bundled runtime components
5. record exact versions
6. identify license for each item
7. record notice requirements
8. record redistribution requirements
9. update THIRD-PARTY-NOTICES.md
10. review before public commercial distribution
```

---

## Required output

The audit should produce:

```text
third-party component inventory
license matrix
notice requirements
package legal file requirements
commercial readiness decision
list of unresolved license questions
```

---

## Before commercial distribution

Do not publish a Supporter or Pro package until:

```text
third-party inventory is complete
required notices are included
license texts or links are included where needed
redistribution rights are reviewed
EULA references third-party notices
package contains legal files
release notes identify package type
```

---

## Boundaries

This plan is not legal advice.

Before paid distribution, consult legal counsel if needed, especially if:

```text
bundling a JRE
bundling OCR data
bundling copyleft components
shipping modified third-party code
selling commercial packages
distributing outside the initial test market
```
