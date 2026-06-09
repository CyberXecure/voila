# Voila Legal Copy Script Commercial Gate

## Purpose

Define when the future legal copy script becomes required for Voila commercial or controlled package distribution.

This document is planning-only.

---

## Gate rule

Any future public beta, tester, Supporter, or Pro package should pass legal file copy validation before packaging is finalized.

---

## Public beta gate

Required before public beta package publishing:

```text
[ ] legal copy script or equivalent manual process used
[ ] legal/EULA.txt present
[ ] legal/LICENSE.txt present
[ ] legal/BETA-TERMS.md present
[ ] legal/THIRD-PARTY-NOTICES.md present
[ ] README references legal folder
[ ] release notes reference legal folder
```

---

## Tester demo gate

Required:

```text
[ ] legal folder included
[ ] tester-only terms clear
[ ] page-count limit clear
[ ] no redistribution clear
[ ] legal copy validation passed
```

---

## Supporter gate

Required before first paid Supporter package:

```text
[ ] legal copy validation passed
[ ] Supporter terms included or referenced
[ ] EULA reviewed for paid beta/supporter use
[ ] third-party notices reviewed enough for distribution
[ ] payment/refund wording not misleading
```

---

## Pro gate

Required before Pro package:

```text
[ ] legal copy validation passed
[ ] Pro license addendum included or referenced
[ ] third-party license audit completed
[ ] commercial/internal use rights clear
[ ] official download/support path defined
```

---

## Gate result values

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
Legal files are copied and validation passed.

Conditional:
Legal files copied, but one or more content reviews remain pending.

Fail:
Required legal files are missing or invalid.

Not reviewed:
No package should be published.
```

---

## Recommendation

The future copy script should become a required packaging gate before any Supporter or Pro package is built.
