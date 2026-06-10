# Voila Windows Package ZIP Candidate Build Inputs

## Purpose

Define required inputs for the future Voila Windows ZIP candidate build.

This is planning-only.

---

## Required repository inputs

```text
scripts/release/copy-package-legal-files.ps1
scripts/release/validate-package-staging.ps1
docs/legal/VOILA-BETA-EULA-DRAFT.md
LICENSE.txt
BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md
```

---

## Required package documentation inputs

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
```

These may be generated during package staging or copied from controlled release docs.

---

## Required launchers

```text
START-VOILA.bat
STOP-VOILA.bat
```

The candidate build should use real package launchers, not dry-run placeholders.

---

## Required runtime source

One runtime source must be selected and documented.

Allowed source categories:

```text
latest validated Windows tester package source
fresh package staging generated from repository
previous public beta runtime package
internal runtime staging folder
```

The selected source must be:

```text
known
repeatable
validated
not mixed with another runtime source
```

---

## Required legal outputs

The build must include:

```text
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```

These should be produced by the legal copy script.

---

## Required validation outputs

Before ZIP creation:

```text
validate-package-staging.ps1 result: PASS
validate-package-staging.ps1 -Strict result: PASS
```

After ZIP creation:

```text
ZIP extraction check: PASS
candidate smoke test: PASS
SHA256 generated: PASS
```

---

## Missing input policy

If any required input is missing:

```text
do not create ZIP
document blocker
fix input
rerun validation
```

---

## Inputs not allowed

Do not include:

```text
secrets
private PDFs
customer documents
docs/commercial
local root helper scripts
developer machine paths
unreviewed license/payment docs
```
