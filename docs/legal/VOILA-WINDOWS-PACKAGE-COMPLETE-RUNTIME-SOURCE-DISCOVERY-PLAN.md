# Voila Windows Package Complete Runtime Source Discovery Plan

Milestone:

```text
v0.3.47-voila-windows-package-complete-runtime-source-plan
```

## Purpose

Define a safe discovery step before implementing a complete runtime source.

This is planning-only.

---

## Discovery questions

Answer before implementation:

```text
[ ] Where is the real FastAPI entrypoint?
[ ] What command starts Voila locally today?
[ ] Which Python executable/environment is currently used?
[ ] Which dependencies are needed at runtime?
[ ] Is frontend served by backend or separate?
[ ] Are frontend assets already built?
[ ] Is LanguageTool required in the next package?
[ ] Is Java bundled or external?
[ ] Is Tesseract required in the next package?
[ ] Which files are safe to copy into runtime source?
[ ] Which files must be excluded?
```

---

## Suggested discovery commands

```powershell
Get-ChildItem -Recurse -File -Include main.py,app.py | Select-Object FullName
Get-ChildItem -Recurse -File -Include requirements.txt,pyproject.toml,package.json | Select-Object FullName
Get-ChildItem -Recurse -Directory -Include api,backend,service,frontend,dist,static | Select-Object FullName
Select-String -Path .\scripts\**\*.ps1 -Pattern "uvicorn|fastapi|8787|8081|tesseract|LanguageTool" -ErrorAction SilentlyContinue
```

---

## Discovery output

The discovery milestone should produce:

```text
actual API entrypoint
actual start command
runtime source copy map
dependency strategy
frontend strategy
LanguageTool strategy
Tesseract strategy
exclusion list
next build plan
```

---

## Safety boundary

Discovery must not:

```text
modify runtime behavior
install dependencies
run START/STOP smoke
create ZIP
publish release assets
```
