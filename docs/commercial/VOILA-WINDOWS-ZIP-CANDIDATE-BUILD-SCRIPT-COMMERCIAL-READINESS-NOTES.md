# Voila Windows ZIP Candidate Build Script Commercial Readiness Notes

## Purpose

Document what the implemented and DryRun-validated Windows ZIP candidate build helper means for commercial readiness.

This is guidance only.

---

## What is now ready

Voila now has:

```text
package legal file copy helper
package staging validation helper
Windows ZIP candidate build helper
validated build helper DryRun smoke
README/release workflow documentation
```

---

## What is not yet ready

The project still does not yet have:

```text
confirmed final runtime source for candidate ZIP
real ZIP candidate created from production-intended runtime
full extracted ZIP smoke test
official SHA256 for a ZIP candidate
GitHub release publication
installer
code signing
Supporter/Pro paid terms
license activation
payment/refund wording
final legal approval
```

---

## Commercial implication

The project is closer to controlled package candidate readiness, but this is not yet a commercial release.

Before any paid Supporter/Pro package:

```text
[ ] final or reviewed EULA ready
[ ] third-party notices complete enough for distribution
[ ] Supporter/Pro terms drafted
[ ] payment/refund wording reviewed
[ ] activation/licensing decision made
[ ] official support/download path defined
```

---

## Recommended next gate

Before creating a real ZIP candidate, define:

```text
exact runtime source
candidate version
candidate ZIP name
candidate output folder
smoke test procedure
release notes SHA256 handling
```

Recommended next milestone:

```text
v0.3.31-voila-windows-zip-candidate-runtime-source-plan
```
