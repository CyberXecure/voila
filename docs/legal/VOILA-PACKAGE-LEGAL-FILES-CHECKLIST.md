# Voila Package Legal Files Checklist

## Purpose

Define the legal and terms-related files that should be included in future Voila Windows packages.

This checklist helps keep packages consistent before broader public distribution or paid Supporter/Pro builds.

## Minimum package legal files

Recommended minimum:

```text
LICENSE.txt
BETA-TERMS.md or EULA.txt
THIRD-PARTY-NOTICES.md
README-WINDOWS.txt or README-TESTERS.txt
RELEASE-NOTES.txt
```

## Suggested package structure

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
  legal/
    EULA.txt
    BETA-TERMS.md
    THIRD-PARTY-NOTICES.md
```

## Required legal statements per package

Each package should clearly state:

```text
package name
version
release type
publisher/project owner
license/beta terms
whether commercial use is allowed
whether redistribution is allowed
whether page-count limits apply
whether generated content must be reviewed
third-party notices location
```

## Release type checklist

### Public Beta Runtime Package

```text
[ ] EULA or beta terms included
[ ] public beta status clear
[ ] non-commercial/evaluation wording clear if applicable
[ ] runtime package status clear
[ ] known limitations included
[ ] SHA256 generated
```

### Tester Demo Build

```text
[ ] tester-only wording clear
[ ] page-count limit documented
[ ] no-redistribution wording clear
[ ] feedback instructions included
[ ] known limitations included
```

### Supporter Build

```text
[ ] Supporter rights defined
[ ] page limit / feature differences defined
[ ] personal/internal use wording clear
[ ] no-redistribution wording clear
[ ] payment/license reference included
```

### Pro Build

```text
[ ] commercial/internal use rights defined
[ ] Pro limits/features defined
[ ] support expectations defined
[ ] redistribution restrictions clear
[ ] license activation/payment terms referenced if applicable
```

## Third-party notice readiness

Before a broader paid release:

```text
[ ] list all bundled third-party components
[ ] list versions
[ ] list licenses
[ ] include required notices
[ ] include license texts or links where required
[ ] verify redistribution rights
[ ] verify Java/JRE redistribution requirements
[ ] verify Tesseract/OCR data requirements
[ ] verify LanguageTool requirements
[ ] verify Python/package requirements
[ ] verify frontend dependency requirements
```

## README / release note references

Package README should point to:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

Release notes should include:

```text
release type
intended audience
download guidance
known limits
legal/terms reference
SHA256
```

## What not to include

Avoid including:

```text
private project notes
commercial roadmap docs
internal QA notes
pricing assumptions
license key implementation plans
secrets
API keys
private PDFs
customer documents
machine-specific local paths
```
