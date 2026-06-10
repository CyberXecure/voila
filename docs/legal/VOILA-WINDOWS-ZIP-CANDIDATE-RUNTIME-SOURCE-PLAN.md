# Voila Windows ZIP Candidate Runtime Source Plan

Milestone:

```text
v0.3.31-voila-windows-zip-candidate-runtime-source-plan
```

## Purpose

Define how the real runtime source should be selected before creating the first controlled Voila Windows ZIP package candidate.

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

## Why this milestone is needed

The build helper exists:

```text
scripts/release/build-windows-zip-candidate.ps1
```

Its DryRun flow has been validated.

Before creating a real ZIP candidate, the runtime source must be selected explicitly to avoid:

```text
mixing old and new runtime files
copying dev-only files
copying private/test documents
copying incomplete staging output
using an unverified package folder
creating a ZIP from repository root by mistake
```

---

## Runtime source definition

A runtime source is the folder that contains the runnable Voila Windows package content before package legal files and ZIP candidate wrapping are applied.

It should already contain:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
runtime/application files
```

The build helper will then copy legal files and validate staging.

---

## Candidate runtime source options

### Option A: latest validated Windows tester package source

Use a previously validated tester package folder or extracted package as the runtime source.

Pros:

```text
already close to user package shape
launchers likely present
known tester packaging assumptions
```

Risks:

```text
may include old README wording
may include tester/demo-specific constraints
may include stale runtime files
may not reflect latest repo docs/scripts
```

### Option B: fresh runtime staging generated from repository

Generate a clean package runtime staging folder from the current repository state.

Pros:

```text
most controlled
repeatable
can use latest README/release docs
can avoid stale artifacts
```

Risks:

```text
requires clearly defined build/staging steps
may uncover missing runtime-copy automation
may require another dry-run milestone
```

### Option C: previous public beta runtime package

Use the previous public beta package as the runtime source.

Pros:

```text
known public beta baseline
likely already runnable
```

Risks:

```text
may be outdated
may not include current legal/package docs
may not reflect current helper scripts
```

### Option D: internal manual staging folder

Create a manual runtime source folder for the candidate.

Pros:

```text
fast
flexible
useful for one-off candidate
```

Risks:

```text
less repeatable
higher chance of omissions
harder to audit later
```

---

## Recommended choice

Recommended for first controlled ZIP candidate:

```text
Option B: fresh runtime staging generated from repository
```

Reason:

```text
cleanest future-proof path
lowest risk of stale files
best basis for repeatable packaging
best match for current release helper scripts
```

However, if a fully validated standalone runtime package already exists and is clearly identified, Option A can be used as an interim source.

---

## Required runtime source contents

The selected runtime source must contain:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
```

It should also contain all runtime files required for Voila to start locally on Windows.

The selected runtime source should not contain `legal/` as a blocker; legal files can be overwritten/copied by the build helper.

---

## Required exclusions

The selected runtime source must not contain:

```text
.git/
.github/
docs/commercial/
private documents
customer PDFs
.env
*.pem
*.key
*.pfx
local helper scripts copied to repo root
development-only caches
personal machine paths
```

---

## Runtime source validation before ZIP

Before using the runtime source for a ZIP candidate:

```text
[ ] runtime source path is documented
[ ] runtime source is not repository root
[ ] runtime source is not docs/
[ ] runtime source is not scripts/
[ ] README-WINDOWS.txt exists
[ ] RELEASE-NOTES.txt exists
[ ] START-VOILA.bat exists
[ ] STOP-VOILA.bat exists
[ ] no forbidden files are present
[ ] source version/candidate label is clear
```

---

## Build helper command once source is selected

DryRun first:

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <selected-runtime-source> `
  -OutputRoot .\.release-cache\voila-v0.3.31-windows-package-candidate `
  -Version "v0.3.31" `
  -ReleaseType PublicBeta `
  -DryRun
```

Only after DryRun passes:

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <selected-runtime-source> `
  -OutputRoot .\.release-cache\voila-v0.3.31-windows-package-candidate `
  -Version "v0.3.31" `
  -ReleaseType PublicBeta `
  -Force
```

---

## Decision record template

When the runtime source is selected, record:

```text
Selected runtime source:
Source type:
Source path:
Created from:
Version/commit:
Validation result:
Known limitations:
Approved for ZIP candidate: Yes/No
```

---

## Out of scope

This milestone does not:

```text
create runtime source
build runtime
create ZIP
generate SHA256
smoke test ZIP
publish release
make GitHub repo private
add licensing/payment
```

---

## Recommended next milestone

If this plan is accepted:

```text
v0.3.32-voila-windows-zip-candidate-runtime-source-dry-run
```

That milestone can create or identify the selected runtime source and run the build helper in `-DryRun` mode against it.
