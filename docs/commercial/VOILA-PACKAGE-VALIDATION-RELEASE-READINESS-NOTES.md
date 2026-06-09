# Voila Package Validation Release Readiness Notes

## Purpose

Connect package staging validation usage to release readiness for future public beta, tester, Supporter, or Pro packages.

This document is planning/guidance only.

---

## Release readiness principle

A future package should not be zipped, installed, uploaded, or publicly shared until package staging validation passes or receives documented manual approval.

---

## Public beta readiness

Before publishing a public beta runtime package:

```text
[ ] legal files copied
[ ] package staging validation passes
[ ] README exists
[ ] release notes exist
[ ] START/STOP launchers exist
[ ] package type is clear
[ ] SHA256 is generated after final packaging
[ ] smoke test is completed
```

---

## Tester demo readiness

Before sharing a tester demo package:

```text
[ ] package staging validation passes
[ ] tester README exists
[ ] feedback instructions are present
[ ] page-count limits are clear
[ ] no redistribution wording is clear
[ ] no private files are included
```

---

## Supporter readiness

Before first Supporter package:

```text
[ ] package staging validation passes
[ ] Supporter terms exist or are referenced
[ ] EULA reviewed for paid/supporter use
[ ] third-party notices reviewed enough for distribution
[ ] payment/refund wording is not misleading
```

---

## Pro readiness

Before first Pro package:

```text
[ ] package staging validation passes
[ ] Pro terms or addendum exists
[ ] commercial/internal use rights are clear
[ ] third-party license audit is complete
[ ] official download/support path is defined
```

---

## Gate status

Use:

```text
Pass
Conditional
Fail
Not reviewed
```

Definitions:

```text
Pass:
Validation passes and required release docs are present.

Conditional:
Warnings exist but manual approval is documented.

Fail:
Validation fails; do not package.

Not reviewed:
Validation was not run; do not package.
```
