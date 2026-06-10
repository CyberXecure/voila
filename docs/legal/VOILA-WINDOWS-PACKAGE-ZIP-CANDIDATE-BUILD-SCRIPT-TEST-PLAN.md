# Voila Windows Package ZIP Candidate Build Script Test Plan

## Purpose

Plan tests for the future ZIP candidate build script.

This is documentation-only.

---

## Future script under test

```text
scripts/release/build-windows-zip-candidate.ps1
```

---

## Test scenario 1: DryRun success

Inputs:

```text
valid RuntimeSource
valid OutputRoot
Version
ReleaseType PublicBeta
DryRun enabled
```

Expected:

```text
staging created
legal files copied
staging validation PASS
no ZIP created
no SHA256 created
summary written
```

---

## Test scenario 2: Full candidate build success

Inputs:

```text
valid RuntimeSource
valid OutputRoot
Version
ReleaseType PublicBeta
DryRun disabled
```

Expected:

```text
staging created
validation PASS
ZIP created
SHA256 created
ZIP extracts cleanly
required files exist after extract
summary written
```

---

## Test scenario 3: Missing runtime source

Expected:

```text
FAIL
no staging produced
no ZIP produced
```

---

## Test scenario 4: Missing legal source

Expected:

```text
legal copy fails
build stops
no ZIP produced
```

---

## Test scenario 5: package validation failure

Setup:

```text
remove README-WINDOWS.txt from staging
```

Expected:

```text
validate-package-staging.ps1 fails
build stops
no ZIP produced
```

---

## Test scenario 6: forbidden file included

Setup:

```text
include .env in RuntimeSource
```

Expected:

```text
validation fails
no ZIP produced
```

---

## Test scenario 7: SHA256 generation

Expected:

```text
ZIP hash generated
SHA256 file created
SHA256 references ZIP filename
```

---

## Test scenario 8: post-extract validation

Expected:

```text
ZIP extracts to clean folder
required files found
legal files found
```

---

## Completion criteria

The implementation should not be considered complete until:

```text
DryRun PASS
full build PASS
missing input failure PASS
forbidden file failure PASS
post-extract validation PASS
no GitHub release is created
```
