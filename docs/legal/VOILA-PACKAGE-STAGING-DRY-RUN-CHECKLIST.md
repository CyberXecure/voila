# Voila Package Staging Dry-Run Checklist

Milestone:

```text
v0.3.22-voila-windows-package-staging-dry-run-plan
```

## Dry-run preparation

```text
[ ] sync main
[ ] verify working tree clean
[ ] create dry-run branch
[ ] choose temporary staging folder
[ ] create README-WINDOWS.txt
[ ] create RELEASE-NOTES.txt
[ ] create START-VOILA.bat
[ ] create STOP-VOILA.bat
```

## Legal copy

```text
[ ] run copy-package-legal-files.ps1
[ ] legal/EULA.txt created
[ ] legal/LICENSE.txt created
[ ] legal/BETA-TERMS.md created
[ ] legal/THIRD-PARTY-NOTICES.md created
```

## Validation

```text
[ ] run validate-package-staging.ps1
[ ] result is PASS
[ ] run validate-package-staging.ps1 -Strict
[ ] result is PASS
[ ] optional ValidateLegalOnly passes
```

## Inspection

```text
[ ] list dry-run staging folder
[ ] verify no forbidden files
[ ] verify no private docs
[ ] verify no docs/commercial
[ ] verify no ZIP was created
[ ] verify no installer was created
```

## Cleanup

```text
[ ] dry-run staging folder removed
[ ] no release package created
[ ] no GitHub release created
[ ] no official SHA256 generated
```

## Documentation result

```text
[ ] dry-run result documented
[ ] failures documented if any
[ ] next action identified
```
