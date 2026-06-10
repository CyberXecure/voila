# Voila Windows ZIP Candidate Real Launchers Build Inputs

Milestone:

```text
v0.3.43-voila-windows-zip-candidate-real-launchers-build-plan
```

## Required repository state

```text
protected main synced
working tree clean
source commit recorded
build branch created
```

## Required helper scripts

```text
scripts/release/create-windows-package-launchers.ps1
scripts/release/build-windows-zip-candidate.ps1
scripts/release/copy-package-legal-files.ps1
scripts/release/validate-package-staging.ps1
```

## Required runtime source

The runtime source must include enough files to pass package validation and ZIP build.

Required:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
application/runtime marker or files
```

Before build, generated launcher files must exist in runtime source:

```text
START-VOILA.bat
STOP-VOILA.bat
scripts/start-voila.ps1
scripts/stop-voila.ps1
scripts/check-voila-health.ps1
runtime/state/
runtime/logs/
```

## Required legal output after helper run

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

## Required output artifacts

```text
ZIP candidate
SHA256 file
BUILD-SUMMARY.txt
extract validation folder
```

## Missing input policy

If any required input is missing:

```text
do not create ZIP
document blocker
fix input
rerun staging DryRun if needed
```
