# Voila Windows ZIP Candidate Real Launchers Build Checklist

Milestone:

```text
v0.3.43-voila-windows-zip-candidate-real-launchers-build-plan
```

## Before build

```text
[ ] protected main synced
[ ] working tree clean
[ ] build branch created
[ ] runtime source selected
[ ] output root selected
[ ] launcher helper available
[ ] package validation helper available
[ ] legal copy helper available
[ ] ZIP build helper available
```

## Runtime source preparation

```text
[ ] README-WINDOWS.txt present
[ ] RELEASE-NOTES.txt present
[ ] application/runtime files present
[ ] create-windows-package-launchers.ps1 run
[ ] START-VOILA.bat generated
[ ] STOP-VOILA.bat generated
[ ] scripts/start-voila.ps1 generated
[ ] scripts/stop-voila.ps1 generated
[ ] scripts/check-voila-health.ps1 generated
[ ] runtime/state created
[ ] runtime/logs created
```

## Build

```text
[ ] build-windows-zip-candidate.ps1 run without -DryRun
[ ] package legal files copied
[ ] package staging validation -Strict PASS
[ ] ZIP created
[ ] SHA256 created
[ ] BUILD-SUMMARY.txt created
[ ] extract validation PASS
```

## Extracted ZIP validation

```text
[ ] extracted START-VOILA.bat present
[ ] extracted STOP-VOILA.bat present
[ ] extracted scripts/start-voila.ps1 present
[ ] extracted scripts/stop-voila.ps1 present
[ ] extracted scripts/check-voila-health.ps1 present
[ ] extracted runtime/state present
[ ] extracted runtime/logs present
[ ] extracted legal files present
[ ] no EXE/MSI installer created
[ ] no GitHub release created
```
