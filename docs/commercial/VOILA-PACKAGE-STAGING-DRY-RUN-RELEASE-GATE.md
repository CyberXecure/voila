# Voila Package Staging Dry-Run Release Gate

## Purpose

Define how a package staging dry-run affects future release readiness.

This is planning/commercial readiness guidance only.

---

## Gate rule

A controlled public package should not proceed to ZIP or installer creation until package staging dry-run validation passes.

---

## Public beta gate

Before public beta packaging:

```text
[ ] dry-run staging passes validation
[ ] dry-run strict validation passes
[ ] legal files copied correctly
[ ] README/release notes validated
[ ] launchers validated
[ ] no forbidden files detected
```

---

## Tester demo gate

Before tester demo packaging:

```text
[ ] dry-run staging passes validation
[ ] tester README wording is clear
[ ] page-count limit wording is clear
[ ] no redistribution wording is clear
[ ] feedback instructions are included
```

---

## Supporter gate

Before Supporter packaging:

```text
[ ] dry-run staging passes validation
[ ] Supporter terms exist or are referenced
[ ] EULA reviewed for paid/supporter use
[ ] third-party notices reviewed enough for distribution
[ ] payment/refund wording is not misleading
```

---

## Pro gate

Before Pro packaging:

```text
[ ] dry-run staging passes validation
[ ] Pro terms or addendum exists
[ ] commercial/internal use rights are clear
[ ] third-party audit is complete
[ ] official download/support path is defined
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
Dry-run validation passes cleanly.

Conditional:
Warnings exist but manual approval is documented.

Fail:
Dry-run validation fails.

Not reviewed:
Dry-run was not performed; do not package.
```

---

## Recommendation

Make dry-run staging validation mandatory before the next controlled Windows package candidate.
