# Voila Package Staging Validation Script Commercial Gate

## Purpose

Define when the future package staging validation script becomes a required release gate.

This document is planning-only.

---

## Gate rule

The future validation script should become mandatory before any controlled public release, tester demo, Supporter build, or Pro build.

---

## Public beta gate

Before publishing a public beta runtime package:

```text
[ ] copy-package-legal-files.ps1 completed
[ ] validate-package-staging.ps1 passes
[ ] legal files present
[ ] README present
[ ] release notes present
[ ] launchers present
[ ] no forbidden files
[ ] SHA256 generated after package creation
```

---

## Tester demo gate

Before publishing a tester demo:

```text
[ ] validate-package-staging.ps1 passes
[ ] tester README present
[ ] page-count limits clear
[ ] no redistribution wording clear
[ ] feedback instructions present
[ ] no secrets/private docs included
```

---

## Supporter gate

Before paid Supporter package:

```text
[ ] package validation passes
[ ] Supporter terms included or referenced
[ ] EULA reviewed for paid/supporter use
[ ] third-party notices reviewed enough for distribution
[ ] payment/refund wording checked
[ ] package limits clear
```

---

## Pro gate

Before Pro package:

```text
[ ] package validation passes
[ ] Pro terms or addendum included or referenced
[ ] third-party audit completed
[ ] commercial/internal use rights clear
[ ] support/contact path defined
[ ] official download channel selected
```

---

## Gate status values

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
Validation script passes.

Conditional:
Validation script has warnings only and manual approval is documented.

Fail:
Validation script fails.

Not reviewed:
Validation script was not run; do not publish.
```

---

## Recommendation

Do not package or publish Supporter/Pro builds until this validation script exists and is part of the release workflow.
