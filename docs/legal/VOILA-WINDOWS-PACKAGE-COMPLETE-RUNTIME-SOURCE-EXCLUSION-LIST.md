# Voila Windows Package Complete Runtime Source Exclusion List

Milestone:

```text
v0.3.49-voila-windows-package-complete-runtime-source-copy-map-plan
```

## Always exclude

```text
.git/
.github/
.env
*.pem
*.key
*.pfx
secrets/
private/
.release-cache/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.pyc
*.pyo
```

## Usually exclude unless explicitly required

```text
node_modules/
dist/
build/
coverage/
test-output/
tmp/
temp/
logs/
local uploads/
generated OCR outputs containing user data
```

## Review before copying

```text
docs/
scripts/dev/
scripts/release/
tests/
sample data
fixtures
```

## Must not include in public/tester package

```text
private keys
tokens
personal documents
user PDFs
local machine paths in logs
GitHub credentials
payment/licensing secrets
```

## Validation command ideas

```powershell
Get-ChildItem <runtime-source> -Recurse -Force -File |
  Where-Object { $_.Name -eq ".env" -or $_.Extension -in ".pem",".key",".pfx" }

Get-ChildItem <runtime-source> -Recurse -Force -Directory |
  Where-Object { $_.Name -in ".git",".github",".release-cache","__pycache__" }
```
