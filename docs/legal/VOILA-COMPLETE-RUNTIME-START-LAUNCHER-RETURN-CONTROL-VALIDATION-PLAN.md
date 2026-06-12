# Voila Complete Runtime START Launcher Return-Control Validation Plan

Milestone:

```text
v0.3.58-voila-complete-runtime-start-launcher-return-control-fix-plan
```

## Purpose

Define validation for the future launcher return-control fix.

## Validation stages

```text
1. helper generation validation
2. launcher content validation
3. START return-control smoke
4. health check smoke
5. STOP cleanup smoke
6. post-stop safety checks
```

## Helper generation validation

Generate runtime source:

```powershell
.\scripts\release\create-complete-windows-runtime-source.ps1 `
  -RuntimeSourceRoot <runtime-source-root> `
  -PythonStrategy PackageVenv `
  -IncludeCropEditor `
  -LanguageToolStrategy Deferred `
  -OcrStrategy Deferred `
  -Force
```

Expected:

```text
runtime source created
START/STOP launchers generated
start-voila.ps1 contains non-blocking launch strategy
```

## START return-control validation

Run:

```powershell
$proc = Start-Process -FilePath .\START-VOILA.bat -WorkingDirectory <package-root> -Wait -PassThru
$proc.ExitCode
```

Expected:

```text
START exits within timeout
exit code 0
port 8787 listening
voila-api.pid exists
```

## Health validation

Check:

```text
http://127.0.0.1:8787/health
http://127.0.0.1:8787
```

Expected:

```text
at least one endpoint responds successfully
```

## STOP validation

Run:

```powershell
.\STOP-VOILA.bat
```

Expected:

```text
exit code 0
port 8787 free after STOP
no matching package-owned process remains
```

## Safety validation

Confirm:

```text
no unrelated Python/Java processes killed
no installer created
no ZIP created unless separate build milestone requires it
no GitHub release created
```

## PASS criteria

```text
START returns control
service responds
STOP returns control
port 8787 is free after STOP
logs/state are present
no unsafe process behavior
```
