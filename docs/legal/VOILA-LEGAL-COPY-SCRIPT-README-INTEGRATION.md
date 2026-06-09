# Voila Legal Copy Script README Integration

Milestone:

```text
v0.3.16-voila-package-legal-files-copy-script-readme-integration
```

## Purpose

Document how the legal file copy helper script should be referenced from public README and future release workflow documentation.

This milestone is documentation-only.

It does not:

```text
change runtime behavior
change backend behavior
change frontend behavior
change dependencies
rebuild a package
create a release
upload assets
change GitHub visibility
add payment or activation
provide final legal approval
```

---

## Implemented helper script

The helper script is:

```text
scripts/release/copy-package-legal-files.ps1
```

It copies required legal files into a package staging folder:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

---

## README integration goal

README should make clear that future Windows packages need a package-local legal folder and that the helper script can prepare it during package staging.

Recommended README wording:

```text
Voila Windows packages should include an offline legal/ folder containing EULA.txt, LICENSE.txt, BETA-TERMS.md, and THIRD-PARTY-NOTICES.md.
```

Recommended helper command:

```powershell
.\scripts\release\copy-package-legal-files.ps1 `
  -PackageRoot <package-staging-folder> `
  -ReleaseType PublicBeta
```

---

## What README should not imply

README should not imply that:

```text
the helper creates a package
the helper publishes a release
the helper completes legal review
the helper completes third-party license audit
the package is production-ready
Supporter / Pro terms are already final
```

---

## Release workflow placement

The helper should run after package staging is created and before ZIP/installer creation.

Recommended order:

```text
1. create package staging folder
2. copy runtime files
3. copy README and release notes
4. run scripts/release/copy-package-legal-files.ps1
5. run package validation
6. create ZIP or installer
7. generate SHA256
8. run smoke test
9. publish controlled release
```

---

## Current status

The legal copy helper has already been smoke-tested in:

```text
v0.3.15-voila-package-legal-files-copy-script-smoke
```

Smoke result:

```text
copy mode: PASS
required legal output files: PASS
ValidateOnly after copy: PASS
```
