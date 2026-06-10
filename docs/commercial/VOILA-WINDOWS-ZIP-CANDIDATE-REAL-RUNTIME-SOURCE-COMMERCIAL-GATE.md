# Voila Windows ZIP Candidate Real Runtime Source Commercial Gate

## Purpose

Define commercial/release gate for moving from a planned runtime source to a real runtime source.

This is guidance only.

---

## Gate before real runtime source DryRun

Required:

```text
[ ] real runtime source path selected
[ ] runtime source generated from protected main or documented package baseline
[ ] required launchers exist
[ ] README/release notes exist
[ ] source is not repository root
[ ] no private files are knowingly included
```

---

## Gate before ZIP candidate build

Required:

```text
[ ] real runtime source validation plan completed
[ ] build helper DryRun passes
[ ] package staging validation -Strict passes
[ ] BUILD-SUMMARY.txt reviewed
[ ] no ZIP was created during DryRun
[ ] no forbidden files included
```

---

## Gate before sharing a ZIP candidate

Required later:

```text
[ ] ZIP created from approved real runtime source
[ ] extracted ZIP smoke passes
[ ] SHA256 generated
[ ] release notes updated with SHA256
[ ] legal folder included
[ ] candidate status clear
```

---

## Commercial boundary

A real runtime source is not a paid product release.

Before Supporter/Pro distribution:

```text
[ ] Supporter/Pro terms ready
[ ] EULA reviewed for paid use
[ ] third-party notices complete enough for distribution
[ ] payment/refund wording reviewed
[ ] support/download path defined
```

---

## Current recommendation

Proceed next with a DryRun using the real runtime source before creating any ZIP.
