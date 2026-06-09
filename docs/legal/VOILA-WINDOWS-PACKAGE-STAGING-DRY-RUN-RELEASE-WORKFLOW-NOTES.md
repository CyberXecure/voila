# Voila Windows Package Staging Dry-Run Release Workflow Notes

## Purpose

Connect the validated Windows package staging dry-run to the future Voila release workflow.

This document is guidance only and does not create a package.

---

## Current validated flow

The validated staging flow is:

```text
create staging folder
create README-WINDOWS.txt
create RELEASE-NOTES.txt
create START-VOILA.bat
create STOP-VOILA.bat
copy legal files
validate package staging
validate package staging with -Strict
validate legal-only mode
confirm no ZIP/EXE/MSI created
clean staging folder
```

---

## Helper scripts

The dry-run used:

```text
scripts/release/copy-package-legal-files.ps1
scripts/release/validate-package-staging.ps1
```

---

## Required staging files

A future controlled Windows package candidate should include:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

---

## Future release workflow

Recommended future flow:

```text
1. sync protected main
2. create release/package branch
3. create package staging folder
4. copy runtime files
5. copy README and release notes
6. copy start/stop launchers
7. run copy-package-legal-files.ps1
8. run validate-package-staging.ps1
9. run validate-package-staging.ps1 -Strict
10. create ZIP or installer candidate
11. generate SHA256
12. smoke test candidate
13. publish controlled release only if ready
```

---

## Important release boundary

The validated dry-run is not a release package.

It is a readiness signal that the staging process can be executed cleanly before a future package candidate is built.

---

## Recommended gate

Before creating any ZIP or installer candidate:

```text
[ ] dry-run documentation reviewed
[ ] staging folder created
[ ] legal files copied
[ ] package validation passes
[ ] Strict validation passes
[ ] release notes prepared
[ ] SHA256 plan prepared
[ ] no internal/private files included
```
