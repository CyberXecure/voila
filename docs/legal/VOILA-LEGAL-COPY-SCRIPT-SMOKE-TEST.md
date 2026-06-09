# Voila Legal Copy Script Smoke Test

Milestone:

```text
v0.3.15-voila-package-legal-files-copy-script-smoke
```

## Purpose

Smoke test the Voila legal file copy helper script:

```text
scripts/release/copy-package-legal-files.ps1
```

## Scope

```text
Release/package helper smoke test only.
No runtime changes.
No backend changes.
No frontend behavior changes.
No dependency changes.
No package rebuild.
No GitHub visibility change.
No payment/licensing implementation.
No final legal guarantee.
```

## Smoke test actions

The smoke test verifies that the script can copy required legal files into a temporary package staging folder.

Expected output:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

## Test result

```text
copy mode: PASS
required output files: PASS
ValidateOnly after copy: PASS
```

## Notes

This smoke test uses a temporary folder outside the repository.

It does not create a ZIP package, installer, GitHub release, or runtime build.
