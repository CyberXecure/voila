# Voila Windows ZIP Candidate Real Launchers Build Plan

Milestone:

```text
v0.3.43-voila-windows-zip-candidate-real-launchers-build-plan
```

## Purpose

Plan the rebuild of a Windows ZIP candidate with real package launchers integrated into staging.

This milestone is documentation/release build planning only.

It does not:

```text
rebuild the package
create a ZIP
generate SHA256
run START-VOILA.bat
run STOP-VOILA.bat
create an installer
publish a GitHub release
upload release assets
change runtime behavior
change backend behavior
change frontend behavior
change dependencies
change GitHub visibility
add payment or activation
provide final legal approval
```

---

## Background

Completed chain:

```text
v0.3.40 real launchers helper added
v0.3.41 real launchers helper smoke PASS
v0.3.42 real launchers staging DryRun PASS
```

The next package step is to rebuild the ZIP candidate so the extracted package contains generated real launchers instead of placeholder launchers.

---

## Goal

Create a new local Windows ZIP candidate that includes:

```text
START-VOILA.bat
STOP-VOILA.bat
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
runtime/state/
runtime/logs/
legal/
README-WINDOWS.txt
RELEASE-NOTES.txt
application/runtime files
```

The ZIP build should still be local only and should not publish a GitHub release.

---

## Proposed version

Recommended:

```text
v0.3.44
```

Reason:

```text
v0.3.43 remains docs-only planning.
v0.3.44 can perform the local ZIP rebuild.
```

---

## Required preconditions

Do not rebuild ZIP unless:

```text
[ ] protected main synced
[ ] working tree clean
[ ] create-windows-package-launchers.ps1 exists
[ ] real launchers helper smoke passed
[ ] real launchers staging DryRun passed
[ ] legal copy helper exists
[ ] package staging validation helper exists
[ ] build-windows-zip-candidate.ps1 exists
[ ] output root selected
[ ] runtime source selected
```

---

## Proposed output root

Recommended:

```text
.release-cache/voila-v0.3.44-real-launchers-zip-candidate/
```

Expected output:

```text
staging/voila/
out/
extract-smoke/voila/
```

---

## Required build flow

The build flow should:

```text
1. create or select runtime source
2. copy runtime source to package staging
3. generate real launchers in staging
4. copy legal files
5. validate package staging with -Strict
6. create ZIP candidate
7. generate SHA256
8. extract ZIP for validation
9. verify real launchers are present in extracted package
10. verify no EXE/MSI installer was created
11. document result
```

---

## Required command approach

Current `build-windows-zip-candidate.ps1` creates required top-level launchers, but it does not yet explicitly call `create-windows-package-launchers.ps1`.

Therefore, the rebuild milestone must choose one of these approaches:

```text
Option A:
Update build-windows-zip-candidate.ps1 to call create-windows-package-launchers.ps1 during staging.

Option B:
Prepare RuntimeSource that already contains generated real launchers, then run build-windows-zip-candidate.ps1.
```

Recommended for next implementation:

```text
Option B first
```

Reason:

```text
lower risk
no build helper behavior change yet
validates generated real launchers inside the ZIP candidate
keeps build helper modification optional for later
```

---

## Proposed Option B flow

```powershell
# 1. create real runtime source staging
# 2. generate real launchers into that runtime source
.\scripts\release\create-windows-package-launchers.ps1 `
  -PackageRoot <runtime-source> `
  -Force

# 3. build ZIP candidate from that runtime source
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <runtime-source> `
  -OutputRoot <output-root> `
  -Version "v0.3.44" `
  -ReleaseType PublicBeta `
  -Force
```

Expected:

```text
Result: PASS
ZIP created: PASS
SHA256 created: PASS
extract validation: PASS
real launchers present in extracted ZIP: PASS
```

---

## Required post-build validation

After build, verify extracted ZIP contains:

```text
START-VOILA.bat
STOP-VOILA.bat
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
runtime/state/
runtime/logs/
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

Also verify:

```text
[ ] START-VOILA.bat calls scripts/start-voila.ps1
[ ] STOP-VOILA.bat calls scripts/stop-voila.ps1
[ ] start-voila.ps1 references runtime/state/logs
[ ] stop-voila.ps1 references package PID files
[ ] no ZIP publish occurred
[ ] no EXE/MSI installer exists
```

---

## Smoke boundary

The rebuild milestone should not necessarily run START/STOP smoke.

Recommended split:

```text
v0.3.44 rebuild ZIP with real launchers
v0.3.45 run START/STOP smoke on rebuilt ZIP
```

This keeps build validation separate from runtime execution.

---

## Publication boundary

The rebuilt ZIP candidate must not automatically:

```text
publish GitHub release
upload assets
claim final release
enable paid distribution
create installer
sign binaries
```

Publishing remains a separate milestone after smoke validation.

---

## Recommended next milestone

```text
v0.3.44-voila-windows-zip-candidate-real-launchers-build
```

That milestone should create the local ZIP candidate with real launchers, generate SHA256, perform extract validation, and document the result.
