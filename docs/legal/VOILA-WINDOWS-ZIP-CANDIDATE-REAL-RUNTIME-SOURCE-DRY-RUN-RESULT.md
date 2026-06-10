# Voila Windows ZIP Candidate Real Runtime Source DryRun Result

Milestone:

`	ext
v0.3.34-voila-windows-zip-candidate-real-runtime-source-dry-run
`

## Purpose

Validate the real runtime source staging approach for the first controlled Voila Windows ZIP candidate by running:

`	ext
scripts/release/build-windows-zip-candidate.ps1 -DryRun
`

## Scope

`	ext
Release/package real runtime-source DryRun validation only.
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
`

## Real runtime source approach

Selected runtime source approach:

`	ext
fresh runtime staging generated from protected main
`

Generated from:

`	ext
Branch: test/v0.3.34-voila-windows-zip-candidate-real-runtime-source-dry-run
Commit: bf03e0b
`

## DryRun setup

The DryRun used a temporary real runtime source staging folder outside the repository.

The runtime source included:

`	ext
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
app/REAL-RUNTIME-SOURCE-DRYRUN.txt
runtime/REAL-RUNTIME-MARKER.txt
service/SERVICE-MARKER.txt
`

The build helper copied legal files into staging:

`	ext
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
`

## Command validated

`powershell
.\scripts\release\build-windows-zip-candidate.ps1
  -RuntimeSource <real-runtime-source>
  -OutputRoot <dry-run-output-root>
  -Version "v0.3.34"
  -ReleaseType PublicBeta
  -DryRun
`

## Result

`	ext
real runtime source safety check: PASS
required runtime source files: PASS
build script DryRun: PASS
runtime source copied to staging: PASS
package legal files copied: PASS
package staging validation with -Strict: PASS
BUILD-SUMMARY.txt created: PASS
no ZIP created: PASS
no SHA256 created: PASS
no EXE/MSI created: PASS
`

## Notes

This milestone validates the real runtime source DryRun path only.

It does not create a real ZIP candidate.

Temporary runtime and output folders are deleted after validation.
