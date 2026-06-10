# Voila Windows ZIP Candidate First Real ZIP Build Inputs

## Purpose

Define required inputs for the first real Voila Windows ZIP candidate build.

This is planning-only.

---

## Required source state

```text
protected main synced
working tree clean
source commit recorded
build branch created
```

---

## Required runtime source

The runtime source must be selected and documented.

Required:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
runtime/application files
```

The runtime source must not be:

```text
repository root
docs/
scripts/
```

---

## Required helper scripts

```text
scripts/release/build-windows-zip-candidate.ps1
scripts/release/copy-package-legal-files.ps1
scripts/release/validate-package-staging.ps1
```

---

## Required legal source files

The build helper and legal copy helper should produce:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

---

## Required output root

Recommended:

```text
.release-cache/voila-v0.3.35-first-real-zip-candidate/
```

The output root should be local and ignored by Git.

---

## Required version

Recommended:

```text
v0.3.35
```

---

## Required release type

Recommended:

```text
PublicBeta
```

---

## Required checks before build

```text
[ ] real runtime source exists
[ ] build helper exists
[ ] legal copy helper exists
[ ] package validation helper exists
[ ] no forbidden files found
[ ] DryRun result reviewed
```

---

## Missing input policy

If any required input is missing:

```text
do not create ZIP
document blocker
fix input
rerun DryRun if needed
```
