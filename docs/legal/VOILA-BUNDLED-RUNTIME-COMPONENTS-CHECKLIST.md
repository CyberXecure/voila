# Voila Bundled Runtime Components Checklist

## Purpose

Identify bundled runtime components that may create redistribution obligations in Voila Windows packages.

This is a checklist, not a completed audit.

---

## Runtime areas to review

### Python runtime

Check:

```text
[ ] Is Python bundled in the package?
[ ] Which Python version?
[ ] Is the Python license included?
[ ] Are Python DLLs included?
[ ] Are embedded runtime files redistributed?
[ ] Is the package using a virtual environment?
[ ] Are all Python package licenses inventoried?
```

### Python packages

Check:

```text
[ ] package list exists
[ ] exact versions captured
[ ] licenses identified
[ ] transitive dependencies reviewed
[ ] build-only packages separated from runtime packages
[ ] notices included if required
```

### Java / JRE runtime

Check:

```text
[ ] Is a JRE bundled?
[ ] Which distribution?
[ ] Which version?
[ ] Is redistribution allowed?
[ ] Are license notices included?
[ ] Are required files preserved?
[ ] Is JRE needed for LanguageTool only?
```

### LanguageTool

Check:

```text
[ ] LanguageTool version identified
[ ] license identified
[ ] redistribution requirements reviewed
[ ] bundled language resources reviewed
[ ] server/runtime files inventoried
[ ] required notices included
```

### Tesseract / OCR

Check:

```text
[ ] Tesseract binary/version identified
[ ] OCR language data files identified
[ ] language data licenses reviewed
[ ] required notices included
[ ] redistribution requirements reviewed
```

### PDF/OCR/extraction libraries

Check:

```text
[ ] PDF libraries identified
[ ] OCR helper libraries identified
[ ] image processing libraries identified
[ ] licenses identified
[ ] commercial redistribution reviewed
```

### Frontend runtime/assets

Check:

```text
[ ] frontend dependencies inventoried
[ ] licenses identified
[ ] bundled build output reviewed
[ ] fonts reviewed
[ ] icons reviewed
[ ] image/media assets reviewed
```

### Windows package scripts

Check:

```text
[ ] scripts included in package are intentional
[ ] internal-only scripts excluded
[ ] local machine paths removed
[ ] no secrets or tokens included
[ ] license files included
```

---

## Package-level checklist

Before publishing any broader Windows package:

```text
[ ] package content inventory complete
[ ] legal folder included
[ ] EULA included or referenced
[ ] beta terms included or referenced
[ ] third-party notices included
[ ] release notes include package type
[ ] SHA256 published
[ ] runtime smoke test completed
[ ] stop script verified
[ ] no private documents included
```

---

## Commercial readiness gate

A package should not be labeled Supporter or Pro until:

```text
[ ] third-party notices are complete enough for distribution
[ ] EULA is ready
[ ] redistribution obligations are reviewed
[ ] release type is clearly labeled
[ ] package legal files are included
```
