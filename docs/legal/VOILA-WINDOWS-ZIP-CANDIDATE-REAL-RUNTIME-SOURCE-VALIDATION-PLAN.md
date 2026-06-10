# Voila Windows ZIP Candidate Real Runtime Source Validation Plan

## Purpose

Define validation steps before a real runtime source can be used to create a ZIP candidate.

This is planning-only.

---

## Step 1: identity

```text
[ ] source path recorded
[ ] branch recorded
[ ] commit recorded
[ ] generation method recorded
[ ] reviewer recorded
```

---

## Step 2: required file check

```text
[ ] README-WINDOWS.txt present
[ ] RELEASE-NOTES.txt present
[ ] START-VOILA.bat present
[ ] STOP-VOILA.bat present
[ ] runtime/application files present
```

---

## Step 3: safety scan

```text
[ ] no .git/
[ ] no .github/
[ ] no docs/commercial/
[ ] no .env
[ ] no *.pem
[ ] no *.key
[ ] no *.pfx
[ ] no private PDFs
[ ] no customer documents
[ ] no local helper scripts at package root unless intentional
```

---

## Step 4: helper DryRun

Command:

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <real-runtime-source> `
  -OutputRoot <dry-run-output-root> `
  -Version "v0.3.34" `
  -ReleaseType PublicBeta `
  -DryRun
```

Expected:

```text
Result: DRY-RUN PASS
```

---

## Step 5: review output

```text
[ ] staging/voila exists
[ ] legal files copied
[ ] BUILD-SUMMARY.txt exists
[ ] no ZIP created
[ ] no SHA256 created
[ ] no EXE/MSI created
```

---

## Step 6: decision

Use status:

```text
Approved for ZIP candidate build
Needs fixes
Rejected
```

A real ZIP candidate should not be created unless status is:

```text
Approved for ZIP candidate build
```
