# Voila Windows Package ZIP Candidate Build Script Implementation Notes

Milestone:

```text
v0.3.28-voila-windows-package-zip-candidate-build-script
```

## Purpose

Document the implemented release helper script:

```text
scripts/release/build-windows-zip-candidate.ps1
```

The script prepares a Windows package staging folder from a selected runtime source and can optionally create a ZIP candidate, SHA256 file, extracted validation folder, and build summary.

---

## Scope

```text
Release/package helper script only.
No runtime changes.
No backend changes.
No frontend behavior changes.
No dependency changes.
No GitHub visibility change.
No payment/licensing implementation.
No final legal guarantee.
```

The script can create a ZIP candidate when not run with `-DryRun`, but this milestone does not publish any release.

---

## Main command

Dry-run:

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <runtime-source-folder> `
  -OutputRoot .\.release-cache\voila-v0.3.28-windows-package-candidate `
  -Version "v0.3.28" `
  -ReleaseType PublicBeta `
  -DryRun
```

Full local candidate build:

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <runtime-source-folder> `
  -OutputRoot .\.release-cache\voila-v0.3.28-windows-package-candidate `
  -Version "v0.3.28" `
  -ReleaseType PublicBeta `
  -Force
```

---

## Script behavior

The script:

```text
validates RuntimeSource
prepares OutputRoot
creates staging/voila
copies runtime source contents
requires README-WINDOWS.txt
requires RELEASE-NOTES.txt
requires START-VOILA.bat
requires STOP-VOILA.bat
runs copy-package-legal-files.ps1
runs validate-package-staging.ps1 -Strict
supports DryRun
creates ZIP when not DryRun
generates SHA256 when not DryRun
extracts ZIP for validation when not DryRun
writes out/BUILD-SUMMARY.txt
```

---

## Important limitations

The script does not:

```text
publish a GitHub release
upload assets
create an installer
sign binaries
change repository visibility
implement payments
implement license activation
provide legal approval
```

---

## Safety note

The script requires an explicit runtime source and output root.

It rejects unsafe roots such as repository root, `docs/`, and `scripts/`.
