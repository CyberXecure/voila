# Voila Windows ZIP Candidate Rebuild After START Return-Control Fix Result

Milestone:

```text
v0.3.61-voila-windows-zip-candidate-complete-runtime-source-rebuild-after-start-return-control-fix
```

## Purpose

Rebuild a Windows ZIP candidate after the START launcher return-control fix from v0.3.59 and helper smoke PASS from v0.3.60.

## Scope

```text
Release/package ZIP candidate rebuild only.
No backend behavior changes.
No frontend behavior changes.
No dependency changes.
No installer creation.
No START/STOP execution.
No GitHub visibility change.
No payment/licensing implementation.
No GitHub release publication.
No final legal guarantee.
```

## Source

```text
Branch: build/v0.3.61-voila-windows-zip-candidate-rebuild-after-start-return-control-fix
Commit: 6b2b6d2
```

## Build inputs

```text
Version: v0.3.61
ReleaseType: PublicBeta
RuntimeSourceRoot: C:\Users\liian\AppData\Local\Temp\voila-v0.3.61-complete-runtime-source
RuntimeSource: C:\Users\liian\AppData\Local\Temp\voila-v0.3.61-complete-runtime-source\voila
OutputRoot: C:\Users\liian\AppData\Local\Temp\voila-v0.3.61-complete-runtime-source-zip-candidate-output
```

## Result

```text
complete runtime source helper execution: PASS
runtime source validation: PASS
START launcher content validation: PASS
build script execution: PASS
package staging validation -Strict: PASS
ZIP created: PASS
SHA256 created: PASS
SHA256 verified: PASS
extract validation: PASS
fixed START launcher present in extracted ZIP: PASS
no EXE/MSI installer created in output root: PASS
no START/STOP execution: PASS
```

## ZIP candidate

```text
ZIP: C:\Users\liian\AppData\Local\Temp\voila-v0.3.61-complete-runtime-source-zip-candidate-output\out\voila-v0.3.61-public-beta-windows-package-candidate.zip
SHA256 file: C:\Users\liian\AppData\Local\Temp\voila-v0.3.61-complete-runtime-source-zip-candidate-output\out\voila-v0.3.61-public-beta-windows-package-candidate.zip.sha256
SHA256: 121F3747203BB539033FDE073BC51BD1B0C707C1C562E25A10CE9A77EA24941A
```

## Fixed START launcher evidence

```text
Start-Process -FilePath $PythonExe: present
AddSeconds(15): present
runtime/state/voila-api.pid behavior: present
web_app:app command alignment: present
--app-dir .\services\api command alignment: present
Python -B: present
```

## Boundary

This build result does not claim local service startup from the rebuilt ZIP.

START/STOP smoke on the rebuilt ZIP remains a later milestone.
