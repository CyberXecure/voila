# Voila Windows Package ZIP Candidate Build Release Gate

## Purpose

Define the release gate for the future ZIP candidate build.

This is commercial/release planning only.

---

## Build gate

Do not build the ZIP candidate unless:

```text
[ ] runtime source is selected
[ ] staging folder is prepared
[ ] required docs are ready
[ ] launchers are real package launchers
[ ] legal files copy successfully
[ ] package staging validation passes
[ ] Strict validation passes
```

---

## Share gate

Do not share the ZIP candidate unless:

```text
[ ] ZIP extracts cleanly
[ ] SHA256 is generated
[ ] smoke test passes
[ ] release notes include SHA256
[ ] candidate status is clear
[ ] no private files included
[ ] legal files are included
```

---

## GitHub release gate

Do not attach to GitHub Releases unless:

```text
[ ] release notes are ready
[ ] public download wording is reviewed
[ ] README points users to the correct release
[ ] ZIP and SHA256 assets are both available
[ ] known limitations are clear
[ ] support/feedback path is defined
```

---

## Commercial boundary

A ZIP candidate is not yet a paid Supporter or Pro release.

Before Supporter/Pro:

```text
[ ] paid terms are ready
[ ] refund/payment wording is reviewed
[ ] activation/licensing decision is made
[ ] third-party audit is sufficient
[ ] final legal review is obtained if needed
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
