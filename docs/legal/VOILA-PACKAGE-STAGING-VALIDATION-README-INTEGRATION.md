# Voila Package Staging Validation README Integration

Milestone:

```text
v0.3.21-voila-package-staging-validation-readme-integration
```

## Purpose

Document how the package staging validation helper should be referenced from README and release workflow docs.

Implemented helper:

```text
scripts/release/validate-package-staging.ps1
```

Related helper:

```text
scripts/release/copy-package-legal-files.ps1
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
No GitHub visibility change.
No payment/licensing implementation.
No final legal guarantee.
```

---

## README integration goal

README should clearly show that a future package staging folder should be validated before ZIP/installer creation.

Recommended command sequence:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta

.\scripts\release\validate-package-staging.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta
```

---

## Validation script purpose

The validation script checks package staging readiness for:

```text
legal files
README / tester instructions
release notes
START/STOP launchers
package type clarity
known limits
forbidden private/secrets files
```

---

## Important limitations

README and docs should not imply that the validation script:

```text
creates a package
creates an installer
publishes a GitHub release
uploads assets
generates SHA256
completes legal review
completes third-party license audit
makes Supporter/Pro terms final
```

---

## Recommended release workflow placement

```text
1. create package staging folder
2. copy runtime files
3. copy README and release notes
4. run copy-package-legal-files.ps1
5. run validate-package-staging.ps1
6. create ZIP or installer
7. generate SHA256
8. run smoke test
9. publish controlled release
```

---

## Current status

The validation script was added in:

```text
v0.3.19-voila-package-staging-validation-script
```

The validation script smoke test passed in:

```text
v0.3.20-voila-package-staging-validation-script-smoke
```
