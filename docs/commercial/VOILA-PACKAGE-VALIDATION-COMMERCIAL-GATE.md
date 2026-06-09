# Voila Package Validation Commercial Gate

## Purpose

Define the commercial readiness gate for future package staging validation.

This document is planning-only.

---

## Gate rule

No controlled public package, tester demo, Supporter package, or Pro package should be published until package staging validation passes or receives an explicit conditional approval.

---

## Public beta gate

Required:

```text
[ ] legal folder validation passes
[ ] README validation passes
[ ] release notes validation passes
[ ] package type is clear
[ ] runtime package status is clear
[ ] public download wording is clear
[ ] start/stop instructions are clear
[ ] no secrets/private documents are included
```

---

## Tester demo gate

Required:

```text
[ ] legal folder validation passes
[ ] tester README validation passes
[ ] release notes validation passes
[ ] page-count limit is clear
[ ] selected tester audience is clear
[ ] no redistribution wording is clear
[ ] feedback instructions are clear
```

---

## Supporter gate

Required before first paid Supporter package:

```text
[ ] package validation passes
[ ] Supporter terms exist or are referenced
[ ] EULA reviewed for paid/supporter use
[ ] third-party notices reviewed enough for distribution
[ ] payment/refund wording is not misleading
[ ] package limits are clear
```

---

## Pro gate

Required before Pro package:

```text
[ ] package validation passes
[ ] Pro terms or addendum exists
[ ] commercial/internal use rights are clear
[ ] third-party license audit completed
[ ] support/contact path defined
[ ] official download channel selected
```

---

## Gate statuses

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
Package staging validation passes.

Conditional:
Package may proceed only with documented manual approval.

Fail:
Package must not be published.

Not reviewed:
Package must not be published.
```

---

## Recommendation

Package staging validation should become mandatory before any future public package, Supporter package, or Pro package.
