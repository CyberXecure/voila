# Voila Windows ZIP Candidate Real Runtime Source Plan

Milestone:

```text
v0.3.33-voila-windows-zip-candidate-real-runtime-source-plan
```

## Purpose

Plan how to move from temporary/minimal runtime source DryRun validation to a real runtime source for the first controlled Voila Windows ZIP candidate.

This milestone is documentation-only.

It does not:

```text
create a ZIP
create an installer
rebuild runtime files
publish a GitHub release
upload release assets
change runtime behavior
change backend behavior
change frontend behavior
change dependencies
change GitHub visibility
add payment or activation
provide final legal approval
```

---

## Background

Completed milestones:

```text
v0.3.28 build-windows-zip-candidate.ps1 implemented
v0.3.29 build script DryRun smoke passed
v0.3.31 runtime source selection planned
v0.3.32 selected runtime source approach DryRun passed
```

The next risk is replacing the temporary/minimal DryRun runtime source with a real runtime source that can become the basis for a ZIP candidate.

---

## Real runtime source definition

A real runtime source is a folder containing the actual runnable Voila Windows package content intended for the ZIP candidate.

It must include:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
actual Voila runtime/application files
required OCR/runtime dependencies if bundled
required Java/LanguageTool runtime files if bundled
required backend/frontend/package files
```

The build helper will copy legal files and validate staging.

---

## Preferred real runtime source approach

Preferred:

```text
fresh runtime staging generated from protected main
```

Reason:

```text
best repeatability
lowest stale-file risk
best audit path
best match with current docs and helper scripts
```

Do not use repository root directly as `RuntimeSource`.

---

## Candidate real runtime source path

Recommended local path:

```text
.release-cache/voila-v0.3.33-real-runtime-source/voila/
```

Alternative temporary path:

```text
$env:TEMP/voila-v0.3.33-real-runtime-source/voila/
```

The path should be generated explicitly and should not be committed.

---

## Required real runtime source build inputs

The real runtime source generation should identify:

```text
source commit
source branch
runtime copy command or script
frontend build output, if applicable
backend/service files, if applicable
embedded runtime dependencies, if applicable
launchers
README-WINDOWS.txt
RELEASE-NOTES.txt
```

---

## Required validation before DryRun

Before using the real runtime source with `build-windows-zip-candidate.ps1 -DryRun`:

```text
[ ] source path documented
[ ] source commit documented
[ ] source generation method documented
[ ] README-WINDOWS.txt present
[ ] RELEASE-NOTES.txt present
[ ] START-VOILA.bat present
[ ] STOP-VOILA.bat present
[ ] runtime/application files present
[ ] no repository root used as RuntimeSource
[ ] no docs/commercial included
[ ] no secrets included
[ ] no private documents included
```

---

## Real runtime source safety scan

Required exclusions:

```text
.git/
.github/
.release-cache/
docs/commercial/
private PDFs
customer documents
.env
*.pem
*.key
*.pfx
local helper scripts copied to repo root
temporary build logs unless intentionally included
developer machine paths
```

---

## DryRun command after real runtime source is prepared

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource .\.release-cache\voila-v0.3.33-real-runtime-source\voila `
  -OutputRoot .\.release-cache\voila-v0.3.33-real-runtime-source-dry-run `
  -Version "v0.3.33" `
  -ReleaseType PublicBeta `
  -DryRun
```

Expected:

```text
Result: DRY-RUN PASS
```

---

## Decision record template

```text
Selected real runtime source:
Source path:
Generated from branch:
Generated from commit:
Generation method:
Required files present:
Safety scan result:
DryRun result:
Approved for ZIP candidate build: Yes/No
Known limitations:
```

---

## Out of scope

This milestone does not:

```text
generate the real runtime source
run the real runtime source DryRun
create ZIP
generate SHA256
run extracted ZIP smoke
publish release
```

---

## Recommended next milestone

After this plan:

```text
v0.3.34-voila-windows-zip-candidate-real-runtime-source-dry-run
```

That milestone should generate or identify the real runtime source and run `build-windows-zip-candidate.ps1 -DryRun` against it.
