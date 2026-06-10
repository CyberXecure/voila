# Voila Windows ZIP Candidate Real Launchers Validation Plan

## Purpose

Define validation steps for real Windows package launchers.

This is planning-only.

---

## Static validation

```text
[ ] START-VOILA.bat exists
[ ] STOP-VOILA.bat exists
[ ] launchers use package-relative paths
[ ] no developer machine paths
[ ] no secrets
[ ] no broad kill commands without package ownership checks
[ ] logs folder behavior documented
[ ] state/PID behavior documented
```

---

## START validation

```text
[ ] run START-VOILA.bat
[ ] exit code is 0
[ ] expected logs created
[ ] expected PID/state files created if used
[ ] Voila service responds
[ ] LanguageTool responds if expected
[ ] no blocking error in logs
```

---

## STOP validation

```text
[ ] run STOP-VOILA.bat
[ ] exit code is 0
[ ] package-owned processes stopped
[ ] ports released
[ ] stale state handled
[ ] no unrelated processes killed
```

---

## Port validation

Expected ports unless changed:

```text
8787
8081
```

Commands:

```powershell
Get-NetTCPConnection -LocalPort 8787 -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalPort 8081 -ErrorAction SilentlyContinue
```

---

## Process validation

Review package-owned process strategy.

Do not classify PASS if STOP only works by killing broad unrelated processes.

---

## Acceptance criteria

Real launchers can be accepted only if:

```text
START smoke: PASS
local service check: PASS
STOP smoke: PASS
cleanup check: PASS
```

A placeholder launcher result must remain:

```text
CONDITIONAL
```
