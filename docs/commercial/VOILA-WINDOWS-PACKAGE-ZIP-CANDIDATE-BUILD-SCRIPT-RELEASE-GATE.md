# Voila Windows Package ZIP Candidate Build Script Release Gate

## Purpose

Define the release gate for introducing a future ZIP candidate build script.

This is commercial/release planning only.

---

## Gate before implementing the script

Before implementation:

```text
[ ] build script plan complete
[ ] build script specification complete
[ ] build script test plan complete
[ ] runtime source decision clarified
[ ] no package publication implied
```

---

## Gate before using script for a real ZIP

Required:

```text
[ ] script implementation reviewed
[ ] DryRun smoke passes
[ ] full candidate build smoke passes
[ ] package validation passes
[ ] post-extract validation passes
[ ] no forbidden files included
[ ] SHA256 generated
```

---

## Gate before sharing ZIP

Required:

```text
[ ] ZIP smoke test PASS
[ ] release notes include SHA256
[ ] candidate status is clear
[ ] legal folder is included
[ ] beta terms are included
[ ] support/feedback path is included
```

---

## Gate before Supporter / Pro

A ZIP candidate build script is not enough for paid distribution.

Before paid packaging:

```text
[ ] paid terms are ready
[ ] third-party audit is sufficient
[ ] payment/refund wording reviewed
[ ] license/activation plan decided
[ ] final legal review obtained if needed
```

---

## Status values

Use:

```text
Pass
Conditional
Fail
Not reviewed
```
