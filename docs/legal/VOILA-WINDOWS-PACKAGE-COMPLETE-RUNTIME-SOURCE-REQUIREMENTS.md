# Voila Windows Package Complete Runtime Source Requirements

Milestone:

```text
v0.3.47-voila-windows-package-complete-runtime-source-plan
```

## Required categories

A complete runtime source must cover:

```text
API/backend entrypoint
Python runtime
Python dependencies
frontend/static UI
LanguageTool and Java decision
Tesseract/OCR decision
launcher files
runtime logs/state folders
package docs
legal files during build
```

---

## API/backend requirement

Required:

```text
[ ] actual API entrypoint path identified
[ ] launcher can start the entrypoint
[ ] backend host is 127.0.0.1
[ ] backend port is documented
[ ] health URL is documented
```

Current launcher expected paths:

```text
app/api/main.py
api/main.py
backend/main.py
service/main.py
main.py
```

If the actual path differs, either:

```text
[ ] adjust runtime source layout
```

or:

```text
[ ] update launcher helper path detection
```

---

## Python requirement

Choose one:

```text
[ ] embedded Python under runtime/python/
[ ] package-local .venv/
[ ] documented global Python dependency
```

For tester packages, prefer:

```text
embedded Python or package-local .venv
```

---

## Dependency requirement

Required:

```text
[ ] uvicorn available
[ ] FastAPI app import works
[ ] required OCR/PDF dependencies available
[ ] package does not need pip install during tester use
```

---

## Frontend/static requirement

Choose one:

```text
[ ] backend serves static frontend
[ ] package includes prebuilt frontend assets
[ ] package opens API-only local service
[ ] frontend intentionally deferred
```

Document chosen strategy before rebuild.

---

## LanguageTool requirement

Choose one:

```text
[ ] bundled LanguageTool + Java
[ ] external LanguageTool not included
[ ] LanguageTool deferred
```

If bundled:

```text
[ ] Java executable path exists
[ ] LanguageTool server JAR/files exist
[ ] port 8081 documented
[ ] stop behavior documented
```

---

## Tesseract/OCR requirement

Choose one:

```text
[ ] bundled Tesseract + traineddata
[ ] external Tesseract documented
[ ] OCR deferred
```

If bundled:

```text
[ ] executable path exists
[ ] traineddata path exists
[ ] environment variables documented
```

---

## Security/exclusion requirement

Complete runtime source must exclude:

```text
.git/
.github/
.env
secrets
private data
developer caches
node_modules unless intentionally packaged
test-only artifacts
local output folders
```

---

## Documentation requirement

Package must include:

```text
README-WINDOWS.txt
RELEASE-NOTES.txt
legal/EULA.txt
legal/LICENSE.txt
legal/BETA-TERMS.md
legal/THIRD-PARTY-NOTICES.md
```
