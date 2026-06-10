# Voila Windows ZIP Candidate Build Script Release Workflow Usage

## Purpose

Define how `build-windows-zip-candidate.ps1` fits into the future Voila release workflow.

This document is guidance only.

---

## Helper script

```text
scripts/release/build-windows-zip-candidate.ps1
```

---

## Safe first usage

Use `-DryRun` first:

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <runtime-source-folder> `
  -OutputRoot .\.release-cache\voila-windows-package-candidate `
  -Version "v0.3.x" `
  -ReleaseType PublicBeta `
  -DryRun
```

Expected DryRun outputs:

```text
staging/voila/
out/BUILD-SUMMARY.txt
```

Expected DryRun non-outputs:

```text
no ZIP
no SHA256
no EXE
no MSI
no GitHub release
```

---

## Full local candidate usage

Only after DryRun passes and runtime source is confirmed:

```powershell
.\scripts\release\build-windows-zip-candidate.ps1 `
  -RuntimeSource <runtime-source-folder> `
  -OutputRoot .\.release-cache\voila-windows-package-candidate `
  -Version "v0.3.x" `
  -ReleaseType PublicBeta `
  -Force
```

Expected outputs:

```text
staging/voila/
out/<zip-name>.zip
out/<zip-name>.zip.sha256
out/BUILD-SUMMARY.txt
extract-smoke/voila/
```

---

## Release workflow placement

Recommended order:

```text
1. choose runtime source
2. run build script with -DryRun
3. review BUILD-SUMMARY.txt
4. run full local candidate build
5. verify ZIP and SHA256
6. smoke test extracted package
7. update release notes with SHA256
8. decide whether to publish controlled release
```

---

## Publishing boundary

The build helper stops before publication.

Publishing requires separate manual or future scripted gates:

```text
GitHub release notes
asset upload
SHA256 upload
public download wording review
final smoke result
legal/commercial review as needed
```

---

## Runtime source caution

The helper requires an explicit `RuntimeSource`.

Do not use repository root as runtime source.

Do not mix runtime sources.

Document the selected runtime source before creating a shareable ZIP candidate.
