# Voila Package Legal Files Copy Script Plan

Milestone:

```text
v0.3.13-voila-package-legal-files-copy-script-plan
```

## Purpose

Plan a future package helper script that copies and validates Voila legal files into a Windows package staging folder.

This milestone is documentation-only.

It does not add the script, run the script, rebuild a package, or change runtime behavior.

---

## Background

The previous milestone documented the package legal file copy plan:

```text
docs/legal/VOILA-PACKAGE-LEGAL-FILES-COPY-PLAN.md
docs/legal/VOILA-LEGAL-FILES-COPY-MATRIX.md
docs/legal/VOILA-PACKAGE-LEGAL-FILES-VALIDATION-CHECKLIST.md
```

The future helper script should implement the documented copy flow in a safe packaging-only context.

---

## Future script goal

A future script should:

```text
accept a package staging folder
create legal/ if missing
copy reviewed legal source files into legal/
rename the beta EULA draft to EULA.txt
validate required legal files exist
optionally validate README/release notes references
fail loudly if required files are missing
avoid copying internal commercial planning docs
```

---

## Future script name

Recommended future script path:

```text
scripts/release/copy-package-legal-files.ps1
```

Alternative:

```text
scripts/package/copy-legal-files.ps1
```

---

## Future script inputs

Recommended parameters:

```text
-PackageRoot <path>
-ReleaseType <PublicBeta|TesterDemo|Supporter|Pro>
-Force
-WhatIf
```

Optional later parameters:

```text
-EulaSource <path>
-LicenseSource <path>
-BetaTermsSource <path>
-ThirdPartyNoticesSource <path>
-ValidateOnly
```

---

## Future source mapping

Default source mapping:

```text
docs/legal/VOILA-BETA-EULA-DRAFT.md -> legal/EULA.txt
LICENSE.txt -> legal/LICENSE.txt
BETA-TERMS.md -> legal/BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md -> legal/THIRD-PARTY-NOTICES.md
```

---

## Future validation checks

The script should fail if any required source is missing:

```text
docs/legal/VOILA-BETA-EULA-DRAFT.md
LICENSE.txt
BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md
```

The script should fail if package output is missing:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

---

## What the future script must not do

The script must not:

```text
modify runtime code
modify backend code
modify frontend code
install dependencies
change package version
create a release
upload assets
change GitHub visibility
copy docs/commercial into the package
copy private planning docs into the package
silently ignore missing legal files
```

---

## Safety behavior

Recommended behavior:

```text
print clear source and destination paths
print release type
print required files copied
print validation result
exit non-zero on missing files
support -WhatIf before actual copy
```

---

## Package integration point

The script should run after package staging is created and before package ZIP/installer is finalized.

Recommended packaging order:

```text
1. create package staging folder
2. copy runtime files
3. copy README/release notes
4. run copy-package-legal-files.ps1
5. run package validation
6. create ZIP/installer
7. generate SHA256
8. run smoke test
```

---

## Not included yet

This milestone does not create:

```text
copy-package-legal-files.ps1
package validation script
package rebuild
installer changes
release automation changes
```

---

## Recommended next milestone

```text
v0.3.14-voila-package-legal-files-copy-script
```

or, if more planning is needed:

```text
v0.3.14-voila-package-legal-files-validation-script-plan
```
