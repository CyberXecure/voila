# Voila Third-Party Inventory Template

## Purpose

Template for recording third-party components used by Voila.

This file is a planning template. It is not yet a completed audit.

---

## Inventory table template

Use this structure during the audit:

```text
Component:
Category:
Version:
Source:
Bundled in package? Yes / No / Unknown
Runtime dependency? Yes / No / Unknown
Development-only? Yes / No / Unknown
License:
Copyright holder:
License URL or file:
Notice required? Yes / No / Unknown
License text required? Yes / No / Unknown
Redistribution allowed? Yes / No / Unknown
Commercial use allowed? Yes / No / Unknown
Source offer required? Yes / No / Unknown
Modification status:
Notes:
Decision:
```

---

## Suggested categories

```text
Python runtime
Python package
Java/JRE runtime
OCR engine
OCR language data
LanguageTool
PDF library
Frontend package
Build tool
Test tool
Packaging tool
Font
Icon
Image/media asset
Documentation asset
Other
```

---

## Component decision values

Use one of:

```text
Approved for beta package
Approved for commercial package
Approved with required notices
Needs replacement
Needs legal review
Development-only, not bundled
Unknown
```

---

## Example entry format

```text
Component: <name>
Category: <category>
Version: <version>
Source: <homepage or package manager>
Bundled in package? Unknown
Runtime dependency? Unknown
Development-only? Unknown
License: Unknown
Copyright holder: Unknown
License URL or file: Unknown
Notice required? Unknown
License text required? Unknown
Redistribution allowed? Unknown
Commercial use allowed? Unknown
Source offer required? Unknown
Modification status: Not reviewed
Notes: To be checked during audit
Decision: Unknown
```

---

## Audit files to inspect

Potential files and folders:

```text
requirements*.txt
pyproject.toml
poetry.lock
package.json
package-lock.json
pnpm-lock.yaml
yarn.lock
scripts/
runtime/
third_party/
vendor/
dist/
release package ZIP contents
docs/legal/THIRD-PARTY-NOTICES.md
```

---

## Output recommendation

After the audit, create or update:

```text
docs/legal/THIRD-PARTY-NOTICES.md
docs/legal/THIRD-PARTY-LICENSE-MATRIX.md
docs/legal/COMMERCIAL-REDISTRIBUTION-REVIEW.md
```
