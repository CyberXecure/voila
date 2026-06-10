# Voila Windows ZIP Candidate START/STOP Smoke Checklist

Milestone:

```text
v0.3.37-voila-windows-zip-candidate-start-stop-smoke-plan
```

## Before smoke

```text
[ ] ZIP candidate exists
[ ] SHA256 verified
[ ] ZIP extracted to clean folder
[ ] README-WINDOWS.txt present
[ ] RELEASE-NOTES.txt present
[ ] START-VOILA.bat present
[ ] STOP-VOILA.bat present
[ ] legal folder present
[ ] previous Voila/LanguageTool processes stopped
[ ] expected ports free or documented
```

## START checks

```text
[ ] run START-VOILA.bat
[ ] no immediate launcher failure
[ ] expected process starts
[ ] local service responds
[ ] UI or health check responds
[ ] logs reviewed for blocking errors
```

## STOP checks

```text
[ ] run STOP-VOILA.bat
[ ] expected processes stop
[ ] expected ports are released
[ ] no orphaned windows/processes remain
[ ] no manual cleanup needed
```

## Result classification

```text
[ ] PASS
[ ] CONDITIONAL
[ ] FAIL
[ ] NOT RUN
```

## Required notes

```text
[ ] ZIP path recorded
[ ] SHA256 recorded
[ ] extracted folder recorded
[ ] START result recorded
[ ] local check result recorded
[ ] STOP result recorded
[ ] cleanup result recorded
[ ] warnings recorded
```
