# Voila Windows ZIP Candidate Build Script DryRun Smoke Test

Milestone:

```text
v0.3.29-voila-windows-package-zip-candidate-build-script-dry-run-smoke
```

## Purpose

Smoke test the Voila Windows ZIP candidate build helper script in `-DryRun` mode:

```text
scripts/release/build-windows-zip-candidate.ps1
```

## Scope

```text
Release/package helper dry-run smoke test only.
No runtime changes.
No backend changes.
No frontend behavior changes.
No dependency changes.
No ZIP creation.
No installer creation.
No GitHub visibility change.
No payment/licensing implementation.
No GitHub release publication.
No final legal guarantee.
```

## Smoke setup

The smoke test creates a temporary minimal runtime source outside the repository.

The runtime source includes:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
app/SMOKE-RUNTIME.txt
```

The build script then prepares a dry-run staging folder and copies legal files into:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

## Command tested

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <temp-runtime-source> `
  -OutputRoot <temp-output-root> `
  -Version "v0.3.29" `
  -ReleaseType PublicBeta `
  -DryRun
```

## Result

```text
build script DryRun: PASS
runtime source copied to staging: PASS
package legal files copied: PASS
package staging validation -Strict: PASS
BUILD-SUMMARY.txt created: PASS
no ZIP created: PASS
no SHA256 created: PASS
no EXE/MSI created: PASS
```

## Notes

This smoke test intentionally does not create a ZIP candidate.

It validates safe staging and package validation behavior only.

Temporary runtime and output folders are deleted after the smoke test.
