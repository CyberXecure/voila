# Voila Windows ZIP Candidate Runtime Source Commercial Gate

## Purpose

Define the commercial/release gate for selecting a runtime source before creating a Voila Windows ZIP candidate.

This is guidance only.

---

## Gate rule

Do not create a real ZIP candidate until the runtime source is selected, documented, and validated.

---

## Minimum gate before DryRun

Required:

```text
[ ] source path selected
[ ] source type selected
[ ] source is not repository root
[ ] required launchers exist
[ ] README/release notes exist
[ ] no obvious private/secrets files
```

---

## Minimum gate before ZIP creation

Required:

```text
[ ] runtime source validation checklist complete
[ ] DryRun passes
[ ] package legal files copy correctly
[ ] package staging validation -Strict passes
[ ] BUILD-SUMMARY.txt reviewed
[ ] no forbidden files included
```

---

## Minimum gate before sharing ZIP

Required:

```text
[ ] ZIP created from approved runtime source
[ ] ZIP extraction smoke passes
[ ] SHA256 generated
[ ] release notes include SHA256
[ ] candidate status is clear
[ ] legal files are included
```

---

## Commercial boundary

A runtime source selection does not mean the product is ready for paid distribution.

Before Supporter/Pro package:

```text
[ ] Supporter/Pro terms ready
[ ] EULA reviewed for paid use
[ ] third-party notices complete enough for distribution
[ ] payment/refund wording reviewed
[ ] support/download path defined
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
