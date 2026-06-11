# Voila Windows ZIP Candidate Complete Runtime Source Build Checklist

Milestone:

```text
v0.3.54-voila-windows-zip-candidate-complete-runtime-source-build-plan
```

## Pre-build checks

```text
[ ] protected main synced
[ ] working tree clean
[ ] create-complete-windows-runtime-source.ps1 exists
[ ] build-windows-zip-candidate.ps1 exists
[ ] copy-package-legal-files.ps1 exists
[ ] validate-package-staging.ps1 exists
[ ] services/api/web_app.py exists
[ ] .venv/Scripts/python.exe exists
```

## Runtime source checks

```text
[ ] complete runtime source generated
[ ] RUNTIME-SOURCE-SUMMARY.txt exists
[ ] services/api/web_app.py copied
[ ] services/api/crop_editor_app.py copied
[ ] package-local .venv copied
[ ] START-VOILA.bat generated
[ ] STOP-VOILA.bat generated
[ ] scripts/start-voila.ps1 generated
[ ] scripts/stop-voila.ps1 generated
[ ] scripts/check-voila-health.ps1 generated
[ ] launcher alignment for web_app:app verified
[ ] forbidden file scan PASS
```

## ZIP build checks

```text
[ ] package legal files copied
[ ] package staging validation -Strict PASS
[ ] ZIP created
[ ] SHA256 file created
[ ] SHA256 verified
[ ] ZIP extracted for validation
[ ] extracted package root found
[ ] complete runtime files present in extracted ZIP
[ ] BUILD-SUMMARY.txt created
```

## Boundary checks

```text
[ ] no EXE installer created
[ ] no MSI installer created
[ ] no START/STOP execution
[ ] no GitHub release created
[ ] no GitHub visibility changed
[ ] no payment/licensing implementation added
[ ] no final legal guarantee claimed
```
