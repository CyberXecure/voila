# Voila Windows ZIP Candidate Real Runtime Source Requirements

## Purpose

Define the requirements for the real runtime source used by the first controlled Voila Windows ZIP candidate.

This is planning-only.

---

## Required top-level files

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
```

---

## Required runtime categories

The real runtime source should include the actual files required for Voila to run on Windows.

Expected categories:

```text
Voila application/service files
frontend/static assets if applicable
backend/API files if applicable
OCR runtime files if bundled
Tesseract files if bundled
Java runtime files if bundled
LanguageTool files if bundled
local scripts required by START/STOP launchers
configuration defaults safe for distribution
```

---

## Required package wording

`README-WINDOWS.txt` should include:

```text
what Voila is
how to start
how to stop
local URL if applicable
known limitations
legal/ folder reference
support/feedback path
candidate/public beta wording
```

`RELEASE-NOTES.txt` should include:

```text
release type
version
candidate status
runtime source note
known limitations
SHA256 placeholder
smoke status placeholder
commercial use wording
redistribution wording
```

---

## Must not include

```text
source .git metadata
docs/commercial
private/customer documents
developer-only caches
secrets
machine-specific absolute paths
unreviewed paid terms
unreviewed private notes
```

---

## Build helper compatibility

The source must be compatible with:

```text
scripts/release/build-windows-zip-candidate.ps1
```

Meaning it must satisfy:

```text
RuntimeSource is a directory
RuntimeSource is not repository root
RuntimeSource is not docs/
RuntimeSource is not scripts/
required top-level files exist
package staging validation can pass after legal copy
```

---

## Minimum validation result

Before ZIP creation:

```text
build-windows-zip-candidate.ps1 -DryRun: PASS
validate-package-staging.ps1 -Strict: PASS
```
