# Voila Windows ZIP Candidate Release Asset Staging Plan

Milestone:

```text
v0.3.64-voila-windows-zip-candidate-release-asset-staging-plan
```

## Purpose

Plan the release/tester asset staging package for the Windows ZIP candidate that passed tester readiness review.

This milestone defines what should be prepared for manual tester sharing or a future draft GitHub release.

It does not upload, publish, rebuild, sign, or distribute anything.

## Candidate

```text
ZIP: voila-v0.3.61-public-beta-windows-package-candidate.zip
SHA256: 121F3747203BB539033FDE073BC51BD1B0C707C1C562E25A10CE9A77EA24941A
```

## Evidence carried forward

```text
#177 rebuilt ZIP candidate PASS
#178 rebuilt ZIP START/STOP smoke PASS
#179 tester readiness review READY FOR LIMITED MANUAL TESTER SHARING
```

## Asset staging goal

Prepare a clean set of release/tester assets:

```text
Windows ZIP package
SHA256 checksum file
short release notes
tester instructions
known limitations
feedback template
optional tester handoff message
```

## Asset staging boundary

This milestone does not:

```text
create a new ZIP
modify the v0.3.61 ZIP
create installer
create EXE/MSI
upload GitHub release assets
publish GitHub release
change repository visibility
implement payment/licensing
provide final legal approval
```

## Recommended staging folder

Suggested local staging root:

```text
%TEMP%\voila-v0.3.64-release-asset-staging
```

Suggested contents:

```text
voila-v0.3.61-public-beta-windows-package-candidate.zip
voila-v0.3.61-public-beta-windows-package-candidate.zip.sha256
RELEASE-NOTES-TESTERS.txt
README-TESTERS-SHORT.txt
KNOWN-LIMITATIONS-TESTERS.txt
FEEDBACK-TEMPLATE.txt
ASSET-MANIFEST.txt
```

## Staging validation

Validate:

```text
ZIP exists
SHA256 file exists
SHA256 matches ZIP
asset manifest lists all files
instructions mention START-VOILA.bat
instructions mention STOP-VOILA.bat
instructions mention http://127.0.0.1:8787
known limitations mention beta status and local-only operation
feedback template requests Windows version, START/STOP result, and screenshots/logs
no source code or temporary runtime folders included
no private logs or private PDFs included
```

## Recommended next milestone

```text
v0.3.65-voila-windows-zip-candidate-release-asset-staging
```

That milestone should create the actual local staging folder and validate the staged files without publishing a GitHub release.
