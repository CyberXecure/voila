# Voila Windows ZIP Candidate First Real ZIP Build Checklist

Milestone:

```text
v0.3.35-voila-windows-zip-candidate-first-real-zip-plan
```

## Before build

```text
[ ] protected main synced
[ ] working tree clean
[ ] build branch created
[ ] real runtime source selected
[ ] real runtime source path documented
[ ] real runtime source DryRun result reviewed
[ ] output root selected
[ ] ZIP name confirmed
[ ] release type confirmed
```

## Build command

```text
[ ] build-windows-zip-candidate.ps1 run without -DryRun
[ ] -RuntimeSource points to approved source
[ ] -OutputRoot points to release cache folder
[ ] -Version set correctly
[ ] -ReleaseType set correctly
[ ] -Force used only for safe output root
```

## Build output

```text
[ ] staging/voila created
[ ] legal files copied
[ ] package staging validation -Strict PASS
[ ] ZIP created
[ ] SHA256 created
[ ] BUILD-SUMMARY.txt created
[ ] ZIP extracted for validation
[ ] extracted required files present
```

## Post-build checks

```text
[ ] ZIP size recorded
[ ] SHA256 hash recorded
[ ] no EXE created
[ ] no MSI created
[ ] no GitHub release created
[ ] no release assets uploaded
```

## Follow-up smoke milestone

```text
[ ] START-VOILA smoke test planned
[ ] STOP-VOILA smoke test planned
[ ] local URL/health check planned
[ ] process/port cleanup check planned
```
