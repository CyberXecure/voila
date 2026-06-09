# Voila Commercial Readiness Third-Party Gate

## Purpose

Define a commercial-readiness gate for third-party licensing before Voila Supporter or Pro packages.

This document is planning-only.

---

## Gate rule

Do not publish a paid Supporter or Pro package until third-party licensing is reviewed enough to support commercial distribution.

---

## Required before Supporter package

```text
[ ] third-party inventory started
[ ] bundled runtime components identified
[ ] obvious license blockers identified
[ ] beta/supporter EULA drafted
[ ] package legal files included
[ ] release type clearly labeled
[ ] no redistribution rights promised beyond terms
```

---

## Required before Pro package

```text
[ ] third-party inventory complete
[ ] license matrix complete
[ ] third-party notices updated
[ ] EULA reviewed
[ ] commercial use rights defined
[ ] redistribution obligations reviewed
[ ] Supporter vs Pro differences documented
[ ] official download channel chosen
[ ] package smoke test documented
```

---

## High-risk components

Review carefully:

```text
bundled Java/JRE
LanguageTool
Tesseract binaries
OCR language data
PDF processing libraries
frontend assets/fonts/icons
any copyleft dependency
any modified third-party code
```

---

## Decision outcomes

After review, each component should be classified as:

```text
OK for beta
OK for Supporter
OK for Pro
OK with notice
Needs replacement
Needs legal review
Do not bundle
Development-only
Unknown
```

---

## Commercial readiness decision

A future release checklist should include:

```text
Third-party commercial gate: Pass / Conditional / Fail
```

Definitions:

```text
Pass:
All bundled components reviewed and notices included.

Conditional:
No obvious blocker, but some notices or exact versions still need completion before broader distribution.

Fail:
A component has unresolved redistribution, commercial-use, or notice issues.
```

---

## Recommended next actions

```text
generate backend dependency inventory
generate frontend dependency inventory
inspect Windows package contents
identify bundled runtime versions
complete third-party notices file
create license matrix
review EULA against third-party notices
```
