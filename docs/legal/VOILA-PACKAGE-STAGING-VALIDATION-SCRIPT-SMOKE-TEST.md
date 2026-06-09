# Voila Package Staging Validation Script Smoke Test

Milestone:

```text
v0.3.20-voila-package-staging-validation-script-smoke
```

## Purpose

Smoke test the Voila package staging validation helper script:

```text
scripts/release/validate-package-staging.ps1
```

## Scope

```text
Release/package validation helper smoke test only.
No runtime changes.
No backend changes.
No frontend behavior changes.
No dependency changes.
No package rebuild.
No GitHub visibility change.
No payment/licensing implementation.
No final legal guarantee.
```

## Smoke test setup

The smoke test creates a temporary package staging folder outside the repository.

The temporary package includes:

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

The legal files are copied by:

```text
scripts/release/copy-package-legal-files.ps1
```

The package staging folder is validated by:

```text
scripts/release/validate-package-staging.ps1
```

## Test result

```text
copy legal files: PASS
validate package staging: PASS
validate package staging with -Strict: PASS
validate legal-only mode: PASS
```

## Fix included

The smoke test identified and fixed a strict-mode Count handling issue in:

```text
scripts/release/validate-package-staging.ps1
```

The script now counts filtered validation results using array wrapping so zero or single matches work correctly under strict mode.

## Notes

This smoke test does not create a ZIP package, installer, GitHub release, SHA256 file, or runtime build.

The temporary staging folder is deleted after the smoke test.
