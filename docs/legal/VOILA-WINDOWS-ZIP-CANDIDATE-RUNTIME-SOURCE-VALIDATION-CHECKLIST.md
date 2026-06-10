# Voila Windows ZIP Candidate Runtime Source Validation Checklist

Milestone:

```text
v0.3.31-voila-windows-zip-candidate-runtime-source-plan
```

## Source identity

```text
[ ] runtime source path documented
[ ] source type documented
[ ] source version/commit documented
[ ] source creation method documented
[ ] source owner/reviewer documented
```

## Required files

```text
[ ] README-WINDOWS.txt present
[ ] RELEASE-NOTES.txt present
[ ] START-VOILA.bat present
[ ] STOP-VOILA.bat present
[ ] runtime/application files present
```

## Safety checks

```text
[ ] source is not repository root
[ ] source is not docs/
[ ] source is not scripts/
[ ] source does not include .git/
[ ] source does not include docs/commercial/
[ ] source does not include .env
[ ] source does not include *.pem
[ ] source does not include *.key
[ ] source does not include *.pfx
[ ] source does not include private PDFs
[ ] source does not include customer documents
```

## Package readiness

```text
[ ] README wording suitable for candidate
[ ] release notes wording suitable for candidate
[ ] candidate status clear
[ ] limitations clear
[ ] commercial use wording clear
[ ] redistribution wording clear
```

## DryRun readiness

```text
[ ] build-windows-zip-candidate.ps1 can use source
[ ] DryRun output root selected
[ ] DryRun command prepared
[ ] expected result is DRY-RUN PASS
```

## Decision

```text
[ ] Approved for DryRun
[ ] Approved for ZIP candidate build
[ ] Blocked
```
