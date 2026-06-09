# Voila Beta EULA Review Checklist

## Purpose

Checklist for reviewing the Voila beta EULA draft before including it in a Windows package.

This checklist does not make the EULA legally final.

---

## Draft completeness

```text
[ ] introduction included
[ ] definitions included
[ ] license grant included
[ ] restrictions included
[ ] beta status included
[ ] release type / limits included
[ ] user document responsibility included
[ ] generated content disclaimer included
[ ] third-party component section included
[ ] ownership section included
[ ] feedback section included
[ ] no warranty section included
[ ] limitation of liability section included
[ ] termination section included
[ ] updates to terms included
[ ] commercial use section included
[ ] contact section included
```

---

## Consistency check

Compare against:

```text
LICENSE.txt
BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md
docs/legal/VOILA-WINDOWS-PACKAGE-EULA-PLAN.md
docs/legal/VOILA-EULA-DRAFT-OUTLINE.md
docs/commercial/VOILA-CONTROLLED-PUBLIC-RELEASE-POLICY.md
```

Check:

```text
[ ] no conflict with LICENSE.txt
[ ] no conflict with BETA-TERMS.md
[ ] no conflict with public download wording
[ ] no conflict with controlled release policy
[ ] release type labels are consistent
[ ] Supporter / Pro wording is not overpromised
```

---

## Risk check

Review:

```text
[ ] generated content disclaimer is clear
[ ] OCR/PDF extraction limitations are clear
[ ] user document responsibility is clear
[ ] confidential document warning is clear
[ ] commercial use restriction is clear
[ ] no-redistribution restriction is clear
[ ] third-party component limitation is clear
[ ] no warranty wording is clear
[ ] liability limitation wording is clear
```

---

## Package readiness check

Before package inclusion:

```text
[ ] EULA reviewed
[ ] EULA exported/copied to legal/EULA.txt
[ ] README references EULA
[ ] release notes reference EULA
[ ] package includes BETA-TERMS.md
[ ] package includes LICENSE.txt
[ ] package includes THIRD-PARTY-NOTICES.md
[ ] package type and limits are clear
```

---

## Legal review check

Before commercial use:

```text
[ ] legal counsel review considered
[ ] consumer law review considered
[ ] privacy/data handling review considered
[ ] third-party license audit considered
[ ] paid Supporter / Pro terms reviewed separately
[ ] refund/payment terms reviewed separately
```

---

## Decision

Use one:

```text
Draft only
Approved for internal review
Approved for public beta package
Approved for tester demo package
Requires legal review
Requires revision
Do not use yet
```
