# Voila Windows ZIP Candidate First Real ZIP Build Result

Milestone:

`	ext
v0.3.36-voila-windows-zip-candidate-first-real-zip-build
`

## Purpose

Create the first local Voila Windows ZIP candidate using:

`	ext
scripts/release/build-windows-zip-candidate.ps1
`

This milestone creates a local ZIP candidate, SHA256 file, build summary, and extract validation output.

It does not publish a GitHub release.

## Scope

`	ext
Local release/package ZIP candidate build only.
No runtime source changes.
No backend changes.
No frontend behavior changes.
No dependency changes.
No installer creation.
No GitHub visibility change.
No payment/licensing implementation.
No GitHub release publication.
No final legal guarantee.
`

## Runtime source

The build used a temporary runtime source staging folder outside the repository.

Generated from:

`	ext
Branch: build/v0.3.36-voila-windows-zip-candidate-first-real-zip-build
Commit: e4254db
`

The runtime source included:

`	ext
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
app/FIRST-REAL-ZIP-RUNTIME.txt
runtime/FIRST-REAL-ZIP-RUNTIME-MARKER.txt
service/SERVICE-MARKER.txt
`

## Build command

`powershell
.\scripts\release\build-windows-zip-candidate.ps1
  -RuntimeSource <runtime-source>
  -OutputRoot <output-root>
  -Version "v0.3.36"
  -ReleaseType PublicBeta
  -Force
`

## Result

`	ext
runtime source safety check: PASS
required runtime source files: PASS
package legal files copied: PASS
package staging validation with -Strict: PASS
ZIP created: PASS
SHA256 file created: PASS
SHA256 verified against ZIP: PASS
extract validation: PASS
BUILD-SUMMARY.txt created: PASS
no EXE/MSI installer created: PASS
no GitHub release created: PASS
`

## ZIP candidate

`	ext
voila-v0.3.36-public-beta-windows-package-candidate.zip
`

## SHA256

`	ext
40D9AED111900C1CC47AAF24F45DE406E74480E3F480F448FA521C5F6BD3B22A
`

## Notes

This is a local ZIP candidate build result.

The ZIP candidate is not automatically approved for public sharing.

A separate smoke milestone should run START/STOP validation before any publication.
