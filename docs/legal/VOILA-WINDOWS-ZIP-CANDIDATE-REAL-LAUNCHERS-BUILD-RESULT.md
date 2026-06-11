# Voila Windows ZIP Candidate Real Launchers Build Result

Milestone:

`	ext
v0.3.44-voila-windows-zip-candidate-real-launchers-build
`

## Purpose

Create a local Windows ZIP candidate with generated real launchers integrated into the runtime source before build.

## Scope

`	ext
Local release/package ZIP candidate rebuild only.
No runtime source changes.
No backend changes.
No frontend behavior changes.
No dependency changes.
No installer creation.
No START/STOP execution.
No GitHub visibility change.
No payment/licensing implementation.
No GitHub release publication.
No final legal guarantee.
`

## Runtime source

Generated from:

`	ext
Branch: build/v0.3.44-voila-windows-zip-candidate-real-launchers-build
Commit: 8bb295e
`

The runtime source included generated real launchers:

`	ext
START-VOILA.bat
STOP-VOILA.bat
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
runtime/state/
runtime/logs/
`

## Build command

`powershell
.\scripts\release\build-windows-zip-candidate.ps1
  -RuntimeSource <runtime-source-with-real-launchers>
  -OutputRoot <output-root>
  -Version "v0.3.44"
  -ReleaseType PublicBeta
  -Force
`

## Result

`	ext
runtime source safety check: PASS
real launchers generated in runtime source: PASS
required runtime source files: PASS
package legal files copied: PASS
package staging validation with -Strict: PASS
ZIP created: PASS
SHA256 file created: PASS
SHA256 verified against ZIP: PASS
extract validation: PASS
real launchers present in extracted ZIP: PASS
BUILD-SUMMARY.txt created: PASS
no EXE/MSI installer created: PASS
no START/STOP execution: PASS
no GitHub release created: PASS
`

## ZIP candidate

`	ext
voila-v0.3.44-public-beta-windows-package-candidate.zip
`

## SHA256

`	ext
9516F462B3D12D800DBC37EDBD6F3148C2A85BBC0690E7CB577A65FB1624C2F5
`

## Notes

This milestone validates local ZIP rebuild with real launchers only.

A separate future milestone should run START/STOP smoke on the rebuilt ZIP candidate.
