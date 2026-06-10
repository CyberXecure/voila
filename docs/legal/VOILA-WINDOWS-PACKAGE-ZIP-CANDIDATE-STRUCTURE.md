# Voila Windows Package ZIP Candidate Structure

## Purpose

Define the expected structure of the future Voila Windows ZIP candidate.

This is planning-only.

---

## ZIP filename

Recommended:

```text
voila-v0.3.25-public-beta-windows-package-candidate.zip
```

Internal-only alternative:

```text
voila-v0.3.25-windows-package-candidate-internal.zip
```

---

## ZIP root folder

Recommended:

```text
voila/
```

Do not place many files directly at ZIP root.

---

## Required top-level files

Inside `voila/`:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
START-VOILA.bat
STOP-VOILA.bat
legal/
```

---

## Required legal folder

```text
legal/
  EULA.txt
  LICENSE.txt
  BETA-TERMS.md
  THIRD-PARTY-NOTICES.md
```

---

## Runtime/package content

The package should include the runtime files needed to start Voila on Windows.

Expected categories:

```text
application files
embedded Python/runtime files if required
Tesseract/runtime files if required
Java/LanguageTool runtime files if required
backend/service files
frontend/static files
launcher scripts
documentation
legal files
```

---

## Files that must not be included

Do not include:

```text
.git/
.github/
node_modules source cache
docs/commercial/
private PDFs
customer documents
.env
*.pem
*.key
*.pfx
local helper scripts copied to repo root
release planning docs unless intentionally included
personal machine paths
```

---

## Candidate label

A candidate ZIP should clearly indicate it is not final until validated:

```text
candidate
public beta candidate
internal candidate
```

Avoid:

```text
final
production
commercial release
Pro
Supporter
```

unless those terms are genuinely ready.

---

## Candidate extraction expectation

A tester should be able to:

```text
extract ZIP
open voila/
read README-WINDOWS.txt
review legal/
run START-VOILA.bat
use Voila locally
run STOP-VOILA.bat
```

---

## Validation before ZIP

Before creating ZIP:

```text
copy-package-legal-files.ps1 PASS
validate-package-staging.ps1 -Strict PASS
```

After creating ZIP:

```text
extract ZIP to clean folder
verify required files
run smoke test
generate/verify SHA256
```
