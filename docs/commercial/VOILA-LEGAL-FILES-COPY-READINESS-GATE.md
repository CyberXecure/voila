# Voila Legal Files Copy Readiness Gate

## Purpose

Define when it is safe to copy legal files into a Voila Windows package.

This gate is planning-only and does not publish a package.

---

## Gate statuses

Use:

```text
Not ready
Ready for tester package
Ready for public beta package
Ready for Supporter package
Ready for Pro package
Needs legal review
```

---

## Ready for tester package

Minimum:

```text
[ ] beta EULA draft reviewed enough for tester use
[ ] BETA-TERMS.md present
[ ] LICENSE.txt present
[ ] THIRD-PARTY-NOTICES.md present
[ ] tester README references legal folder
[ ] release notes state tester/demo limits
[ ] no redistribution wording clear
```

---

## Ready for public beta package

Minimum:

```text
[ ] EULA reviewed enough for public beta use
[ ] BETA-TERMS.md present
[ ] LICENSE.txt present
[ ] THIRD-PARTY-NOTICES.md present
[ ] public README references legal folder
[ ] release notes state package type
[ ] public download wording is clear
[ ] generated content disclaimer is clear
```

---

## Ready for Supporter package

Minimum:

```text
[ ] Supporter terms drafted or referenced
[ ] EULA reviewed for paid beta/supporter use
[ ] third-party notices reviewed enough for distribution
[ ] payment/refund wording reviewed
[ ] personal/internal use rights clear
[ ] page-count / feature limits clear
```

---

## Ready for Pro package

Minimum:

```text
[ ] Pro terms drafted
[ ] commercial/internal use rights clear
[ ] EULA reviewed for commercial use
[ ] third-party license audit completed
[ ] package legal folder complete
[ ] official download/support path defined
```

---

## Not ready conditions

Do not package if:

```text
EULA is missing
BETA-TERMS.md is missing
LICENSE.txt is missing
THIRD-PARTY-NOTICES.md is missing
package type is unclear
commercial use status is unclear
redistribution wording is unclear
internal commercial docs are included by mistake
```

---

## Recommendation

For the next actual package milestone, treat legal file inclusion as a required packaging gate, not an optional documentation step.
