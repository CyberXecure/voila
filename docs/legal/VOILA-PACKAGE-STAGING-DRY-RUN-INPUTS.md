# Voila Package Staging Dry-Run Inputs

## Purpose

Define the minimum inputs needed for a Voila Windows package staging dry-run.

This is documentation-only.

---

## Required repository inputs

Required files/scripts:

```text
scripts/release/copy-package-legal-files.ps1
scripts/release/validate-package-staging.ps1
docs/legal/VOILA-BETA-EULA-DRAFT.md
LICENSE.txt
BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md
```

---

## Required staging files

The dry-run staging folder should include:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
```

Then legal files are copied into:

```text
legal/
```

Expected after legal copy:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

---

## README-WINDOWS.txt minimum content

Must include:

```text
Voila
package type
start instructions
stop instructions
legal/ folder reference
EULA reference
BETA-TERMS reference
THIRD-PARTY-NOTICES reference
```

---

## RELEASE-NOTES.txt minimum content

Must include:

```text
Release type
Version or dry-run label
Intended audience
Runtime package status
Legal folder reference
Limitations
SHA256 note
```

For dry-run, SHA256 should be described as a future release step, not generated as official release checksum.

---

## Launcher placeholders

For dry-run only, placeholder launchers are acceptable:

```text
START-VOILA.bat
STOP-VOILA.bat
```

For real package release, launchers must be the real package launchers.

---

## Excluded inputs

Do not include:

```text
private PDFs
customer documents
.env files
API keys
tokens
docs/commercial/
pricing assumptions
private QA notes
repo privacy transition docs
```

---

## Dry-run input validation

Before running validation:

```text
[ ] staging folder exists
[ ] README-WINDOWS.txt exists
[ ] RELEASE-NOTES.txt exists
[ ] START-VOILA.bat exists
[ ] STOP-VOILA.bat exists
[ ] copy-package-legal-files.ps1 has run
[ ] legal/ folder exists
```
