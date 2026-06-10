# Voila Windows Package ZIP Candidate Build Checklist

Milestone:

```text
v0.3.26-voila-windows-package-zip-candidate-build-plan
```

## Before build

```text
[ ] protected main synced
[ ] working tree clean
[ ] candidate branch created
[ ] runtime source selected
[ ] staging folder selected
[ ] output folder selected
[ ] ZIP name selected
[ ] SHA256 filename selected
```

## Staging

```text
[ ] runtime files copied to staging
[ ] README-WINDOWS.txt copied/created
[ ] RELEASE-NOTES.txt copied/created
[ ] START-VOILA.bat copied
[ ] STOP-VOILA.bat copied
[ ] legal files copied with copy-package-legal-files.ps1
```

## Pre-ZIP validation

```text
[ ] validate-package-staging.ps1 PASS
[ ] validate-package-staging.ps1 -Strict PASS
[ ] no forbidden files found
[ ] no docs/commercial included
[ ] no secrets included
[ ] no local helper root scripts included
```

## ZIP creation

```text
[ ] ZIP created
[ ] ZIP filename matches plan
[ ] ZIP contains single root folder
[ ] ZIP size recorded
[ ] SHA256 generated
[ ] SHA256 file created
```

## Post-ZIP validation

```text
[ ] ZIP extracted to clean folder
[ ] README-WINDOWS.txt present
[ ] RELEASE-NOTES.txt present
[ ] START-VOILA.bat present
[ ] STOP-VOILA.bat present
[ ] legal/EULA.txt present
[ ] legal/LICENSE.txt present
[ ] legal/BETA-TERMS.md present
[ ] legal/THIRD-PARTY-NOTICES.md present
```

## Smoke

```text
[ ] START-VOILA.bat runs
[ ] app opens locally
[ ] expected local health/app check passes
[ ] STOP-VOILA.bat runs
[ ] processes/ports cleaned
```

## Release readiness

```text
[ ] release notes updated with SHA256
[ ] public download wording reviewed
[ ] beta terms reviewed
[ ] third-party notices reviewed enough for candidate distribution
[ ] candidate marked not final
```
