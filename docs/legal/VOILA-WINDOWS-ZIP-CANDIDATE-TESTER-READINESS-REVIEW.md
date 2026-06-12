# Voila Windows ZIP Candidate Tester Readiness Review

Milestone:

```text
v0.3.63-voila-windows-zip-candidate-tester-readiness-review
```

## Purpose

Review whether the rebuilt Windows ZIP candidate is ready for limited manual tester distribution after the START/STOP smoke PASS.

## Candidate

```text
ZIP: voila-v0.3.61-public-beta-windows-package-candidate.zip
SHA256: 121F3747203BB539033FDE073BC51BD1B0C707C1C562E25A10CE9A77EA24941A
```

## Evidence carried forward

```text
#175 START return-control fix implemented
#176 helper smoke PASS
#177 rebuilt ZIP candidate PASS
#178 rebuilt ZIP START/STOP smoke PASS
```

## Readiness result

```text
Tester readiness status: READY FOR LIMITED MANUAL TESTER SHARING
```

## What is ready

```text
complete runtime ZIP candidate exists
SHA256 exists and was verified
ZIP extract validation passed
START launcher returns control
API responds locally on 127.0.0.1:8787
STOP launcher returns control
port 8787 is free after STOP
no installer is required
no installer was created
```

## What to send to testers

Send:

```text
voila-v0.3.61-public-beta-windows-package-candidate.zip
voila-v0.3.61-public-beta-windows-package-candidate.zip.sha256
README-WINDOWS.txt inside package
short tester instructions
feedback template
known limitations note
```

Do not send:

```text
repository source
temporary build folders
helper smoke scripts
local logs
private PDFs
developer-only planning docs unless intentionally shared
```

## Minimum tester instructions

```text
1. Download ZIP.
2. Extract ZIP to a normal folder, for example Downloads or Desktop.
3. Open the extracted voila folder.
4. Run START-VOILA.bat.
5. Open http://127.0.0.1:8787 in the browser.
6. Test with a small non-private PDF.
7. Run STOP-VOILA.bat when finished.
8. Send feedback with screenshots/logs if something fails.
```

## Expected tester behavior

```text
START should return control.
Local web app should open manually at http://127.0.0.1:8787.
STOP should stop the local API.
```

## Boundary

This readiness review does not create a GitHub release, upload release assets, change repository visibility, create an installer, implement payment/licensing, or provide final legal approval.
