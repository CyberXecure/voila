# Voila Windows Package Staging Dry-Run README Integration

Milestone:

```text
v0.3.24-voila-windows-package-staging-dry-run-readme-integration
```

## Purpose

Document in README and release workflow docs that the Voila Windows package staging dry-run has been validated.

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
No final legal guarantee.
```

---

## Validated dry-run

The dry-run was completed in:

```text
v0.3.23-voila-windows-package-staging-dry-run
```

Result:

```text
copy legal files: PASS
validate package staging: PASS
validate package staging with -Strict: PASS
validate legal-only mode: PASS
required staging files present: PASS
no ZIP/EXE/MSI created: PASS
```

---

## README integration goal

README should clearly communicate that Voila has a validated staging process for future controlled Windows packages.

The README should not imply that a final package, ZIP, installer, paid product, or release was created.

---

## Validated staging files

The dry-run validated the presence of:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

---

## Validated helper sequence

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta

.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta `
  -Strict
```

---

## Important limitations

The README wording must remain clear that the dry-run:

```text
does not create a ZIP
does not create an installer
does not create a GitHub release
does not upload assets
does not generate official SHA256
does not make legal terms final
does not enable Supporter / Pro commercial distribution
```

---

## Recommended next milestone

After README integration, the next logical milestone can be:

```text
v0.3.25-voila-windows-package-zip-candidate-plan
```

That milestone should remain planning-only unless explicitly moving to package creation.
