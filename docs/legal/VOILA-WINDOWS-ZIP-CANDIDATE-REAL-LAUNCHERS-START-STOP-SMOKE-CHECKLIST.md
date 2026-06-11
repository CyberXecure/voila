# Voila Windows ZIP Candidate Real Launchers START/STOP Smoke Checklist

Milestone:

```text
v0.3.45-voila-windows-zip-candidate-real-launchers-start-stop-smoke-plan
```

## Before START

```text
[ ] ZIP candidate exists
[ ] SHA256 verified
[ ] ZIP extracted to clean folder
[ ] README-WINDOWS.txt present
[ ] RELEASE-NOTES.txt present
[ ] START-VOILA.bat present
[ ] STOP-VOILA.bat present
[ ] scripts/start-voila.ps1 present
[ ] scripts/stop-voila.ps1 present
[ ] scripts/check-voila-health.ps1 present
[ ] runtime/state present
[ ] runtime/logs present
[ ] legal folder present
[ ] ports 8787 and 8081 checked
```

## START checks

```text
[ ] run START-VOILA.bat
[ ] exit code recorded
[ ] start log checked
[ ] Voila service responds
[ ] health URL checked
[ ] LanguageTool checked if expected
[ ] runtime/state PID files checked
[ ] process snapshot recorded
```

## STOP checks

```text
[ ] run STOP-VOILA.bat
[ ] exit code recorded
[ ] stop log checked
[ ] package-owned processes stopped
[ ] ports released
[ ] stale PID behavior checked
[ ] unrelated user processes not killed
```

## Result

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
[ ] local service result recorded
[ ] STOP result recorded
[ ] cleanup result recorded
[ ] warnings recorded
[ ] next action recorded
```
