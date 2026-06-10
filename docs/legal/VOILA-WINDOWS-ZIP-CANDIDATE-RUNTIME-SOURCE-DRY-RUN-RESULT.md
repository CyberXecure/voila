# Voila Windows ZIP Candidate Runtime Source DryRun Result

Milestone:

```text
v0.3.32-voila-windows-zip-candidate-runtime-source-dry-run
```

## Purpose

Validate the selected runtime source approach for the first controlled Voila Windows ZIP candidate by running:

```text
scripts/release/build-windows-zip-candidate.ps1 -DryRun
```

## Scope

```text
Release/package runtime-source DryRun validation only.
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

## Runtime source decision

Selected runtime source approach:

```text
fresh runtime staging generated from repository
```

Reason:

```text
cleanest future-proof path
lowest risk of stale package files
best basis for repeatable package pipeline
```

## DryRun setup

The DryRun used a temporary runtime source outside the repository.

The runtime source included:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
app/RUNTIME-SOURCE-DRYRUN.txt
runtime/RUNTIME-MARKER.txt
```

The build helper copied legal files into staging:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

## Command validated

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <selected-runtime-source> `
  -OutputRoot <dry-run-output-root> `
  -Version "v0.3.32" `
  -ReleaseType PublicBeta `
  -DryRun
```

## Result

```text
runtime source safety check: PASS
build script DryRun: PASS
runtime source copied to staging: PASS
package legal files copied: PASS
package staging validation with -Strict: PASS
BUILD-SUMMARY.txt created: PASS
no ZIP created: PASS
no SHA256 created: PASS
no EXE/MSI created: PASS
```

## Notes

This milestone validates the runtime source approach and DryRun path only.

It does not create a real ZIP candidate.

Temporary runtime and output folders are deleted after validation.
