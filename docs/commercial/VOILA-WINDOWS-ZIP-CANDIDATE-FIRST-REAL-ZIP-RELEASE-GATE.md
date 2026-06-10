# Voila Windows ZIP Candidate First Real ZIP Release Gate

## Purpose

Define the release gate before creating and sharing the first real Voila Windows ZIP candidate.

This is guidance only.

---

## Gate before ZIP creation

Required:

```text
[ ] real runtime source approved
[ ] real runtime source DryRun passed
[ ] no private files detected
[ ] package validation helper ready
[ ] legal copy helper ready
[ ] build helper ready
[ ] output root selected
```

---

## Gate before sharing ZIP

Required after build:

```text
[ ] ZIP created
[ ] SHA256 generated
[ ] extracted ZIP validation passed
[ ] START/STOP smoke passed
[ ] README reviewed
[ ] release notes reviewed
[ ] legal folder verified
[ ] known limitations clear
```

---

## Gate before GitHub release

Required later:

```text
[ ] release notes finalized
[ ] SHA256 asset ready
[ ] public download wording reviewed
[ ] GitHub release draft reviewed
[ ] feedback/support path defined
[ ] no final/legal/commercial claims overstated
```

---

## Commercial boundary

First real ZIP candidate is not automatically a paid or final commercial release.

Before Supporter/Pro distribution:

```text
[ ] paid terms ready
[ ] EULA reviewed for paid use
[ ] third-party notices complete enough for distribution
[ ] payment/refund wording reviewed
[ ] license/activation plan decided
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
