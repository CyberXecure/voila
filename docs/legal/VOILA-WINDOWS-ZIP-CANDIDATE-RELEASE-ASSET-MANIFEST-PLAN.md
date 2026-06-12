# Voila Windows ZIP Candidate Release Asset Manifest Plan

Milestone:

```text
v0.3.64-voila-windows-zip-candidate-release-asset-staging-plan
```

## Planned manifest

The future staging milestone should generate an asset manifest similar to:

```text
Voila Windows ZIP Candidate Release/Test Asset Manifest

Candidate:
voila-v0.3.61-public-beta-windows-package-candidate.zip

SHA256:
121F3747203BB539033FDE073BC51BD1B0C707C1C562E25A10CE9A77EA24941A

Assets:
- voila-v0.3.61-public-beta-windows-package-candidate.zip
- voila-v0.3.61-public-beta-windows-package-candidate.zip.sha256
- RELEASE-NOTES-TESTERS.txt
- README-TESTERS-SHORT.txt
- KNOWN-LIMITATIONS-TESTERS.txt
- FEEDBACK-TEMPLATE.txt
- ASSET-MANIFEST.txt
```

## Required notes in manifest

The manifest must state:

```text
limited manual tester sharing only
not a public GitHub release approval
not paid distribution approval
not an installer
not signed software
no final legal guarantee
```

## Hash validation

The manifest should include:

```text
expected SHA256
actual SHA256
validation result
validation timestamp
```

## Exclusions

Do not stage:

```text
repository source
.git folder
developer helper scripts
temporary runtime folders
local runtime logs
private PDFs
screenshots containing private data
docs/commercial unless intentionally shared
```
