# Voila Package Legal Files Validation Checklist

## Purpose

Define validation checks for a future package staging folder after legal files have been copied.

This checklist is planning-only.

---

## Expected legal folder

```text
legal/
  EULA.txt
  LICENSE.txt
  BETA-TERMS.md
  THIRD-PARTY-NOTICES.md
```

---

## File existence checks

```text
[ ] legal/ exists
[ ] legal/EULA.txt exists
[ ] legal/LICENSE.txt exists
[ ] legal/BETA-TERMS.md exists
[ ] legal/THIRD-PARTY-NOTICES.md exists
```

---

## File content checks

```text
[ ] EULA.txt references Voila
[ ] EULA.txt states beta/proprietary status
[ ] EULA.txt includes generated content disclaimer
[ ] LICENSE.txt states all rights reserved / proprietary notice
[ ] BETA-TERMS.md states beta use boundaries
[ ] THIRD-PARTY-NOTICES.md exists even if still marked in-progress
```

---

## Package README checks

```text
[ ] README-WINDOWS.txt or README-TESTERS.txt references legal/
[ ] README mentions EULA.txt
[ ] README mentions BETA-TERMS.md
[ ] README mentions THIRD-PARTY-NOTICES.md
[ ] README warns against redistribution/repackaging
[ ] README states package type
```

---

## Release notes checks

```text
[ ] RELEASE-NOTES.txt references legal/
[ ] release type is clear
[ ] intended audience is clear
[ ] runtime package status is clear
[ ] page-count limits are clear if applicable
[ ] commercial use status is clear
[ ] redistribution status is clear
```

---

## Exclusion checks

Ensure package does not include:

```text
[ ] docs/commercial strategy files
[ ] repo privacy transition docs
[ ] pricing assumptions
[ ] activation implementation notes
[ ] private QA notes
[ ] local helper scripts not intended for package
[ ] private PDFs or generated private content
```

---

## Suggested future PowerShell validation concept

A later implementation milestone may validate files with checks like:

```powershell
$required = @(
  "legal\EULA.txt",
  "legal\LICENSE.txt",
  "legal\BETA-TERMS.md",
  "legal\THIRD-PARTY-NOTICES.md"
)

foreach ($file in $required) {
  if (-not (Test-Path (Join-Path $packageRoot $file))) {
    throw "Missing required legal file: $file"
  }
}
```

This milestone does not add runtime/package scripts.
