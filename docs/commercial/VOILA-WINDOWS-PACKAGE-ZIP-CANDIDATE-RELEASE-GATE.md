# Voila Windows Package ZIP Candidate Release Gate

## Purpose

Define the release gate for a future Voila Windows ZIP candidate.

This is commercial/release guidance only.

---

## Gate before ZIP creation

Required:

```text
[ ] package staging folder prepared
[ ] legal files copied
[ ] package staging validation passes
[ ] Strict validation passes
[ ] README-WINDOWS.txt present
[ ] RELEASE-NOTES.txt present
[ ] START-VOILA.bat present
[ ] STOP-VOILA.bat present
[ ] no forbidden files detected
[ ] package candidate name selected
```

---

## Gate after ZIP creation

Required before sharing:

```text
[ ] ZIP exists
[ ] ZIP extracts cleanly
[ ] expected root folder exists
[ ] required package files exist after extraction
[ ] legal folder exists after extraction
[ ] START-VOILA.bat smoke-tested
[ ] STOP-VOILA.bat smoke-tested
[ ] SHA256 generated
[ ] release notes updated with SHA256
```

---

## Gate before GitHub release

Required before attaching to GitHub Releases:

```text
[ ] package smoke test PASS
[ ] release notes finalized
[ ] SHA256 asset ready
[ ] public download wording reviewed
[ ] beta terms reviewed
[ ] third-party notices reviewed enough for beta distribution
[ ] no private files included
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
All candidate gates pass.

Conditional:
Warnings exist, but manual approval is documented.

Fail:
Candidate must not be shared or published.

Not reviewed:
Candidate must not be shared or published.
```

---

## Commercial readiness note

A ZIP candidate is not the same as a commercial release.

Before Supporter or Pro distribution:

```text
Supporter/Pro terms must be ready
payment/refund wording must be reviewed
license/activation decision must be made
third-party audit must be sufficient for distribution
```
