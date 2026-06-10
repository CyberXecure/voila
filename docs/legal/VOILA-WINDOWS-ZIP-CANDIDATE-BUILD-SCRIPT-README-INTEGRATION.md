# Voila Windows ZIP Candidate Build Script README Integration

Milestone:

```text
v0.3.30-voila-windows-package-zip-candidate-build-script-readme-integration
```

## Purpose

Document in README and release workflow docs that Voila now has a Windows ZIP candidate build helper script with a validated `-DryRun` mode.

Implemented helper:

```text
scripts/release/build-windows-zip-candidate.ps1
```

This milestone is documentation/release workflow guidance only.

---

## Scope

```text
No runtime changes.
No backend changes.
No frontend behavior changes.
No dependency changes.
No package rebuild.
No ZIP creation.
No installer creation.
No GitHub visibility change.
No payment/licensing implementation.
No GitHub release publication.
No final legal guarantee.
```

---

## Background

The build helper was implemented in:

```text
v0.3.28-voila-windows-package-zip-candidate-build-script
```

The build helper DryRun smoke test passed in:

```text
v0.3.29-voila-windows-package-zip-candidate-build-script-dry-run-smoke
```

DryRun smoke result:

```text
build script DryRun: PASS
runtime source copied to staging: PASS
package legal files copied: PASS
package staging validation with -Strict: PASS
BUILD-SUMMARY.txt created: PASS
no ZIP created: PASS
no SHA256 created: PASS
no EXE/MSI created: PASS
```

---

## README integration goal

README should clearly document:

```text
the build helper script path
the safe DryRun command
the validated DryRun result
the full local candidate build command for later use
the fact that GitHub release publishing is not performed by this helper
```

---

## Recommended DryRun command

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <runtime-source-folder> `
  -OutputRoot .\.release-cache\voila-windows-package-candidate `
  -Version "v0.3.x" `
  -ReleaseType PublicBeta `
  -DryRun
```

---

## Recommended full local candidate command

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <runtime-source-folder> `
  -OutputRoot .\.release-cache\voila-windows-package-candidate `
  -Version "v0.3.x" `
  -ReleaseType PublicBeta `
  -Force
```

---

## Important limitations

The README must not imply that the helper:

```text
publishes a GitHub release
uploads assets
creates an installer
signs binaries
implements payment
implements license activation
makes legal terms final
makes third-party notices complete
```

---

## Recommended next milestone

After README integration, the next logical milestone is:

```text
v0.3.31-voila-windows-zip-candidate-runtime-source-plan
```

That milestone should define the exact runtime source to use before any real ZIP candidate is created.
