# Voila Package Legal Integration Commercial Gate

## Purpose

Define a commercial-readiness gate for including legal files in future Voila packages.

This document is planning-only.

---

## Gate rule

No Supporter or Pro package should be published until legal package inclusion is complete enough for that package type.

---

## Public beta minimum gate

Required:

```text
[ ] legal/EULA.txt included or beta terms clearly included
[ ] legal/LICENSE.txt included
[ ] legal/BETA-TERMS.md included
[ ] legal/THIRD-PARTY-NOTICES.md included
[ ] README references legal folder
[ ] release notes reference legal folder
[ ] package type is clear
[ ] no-redistribution wording clear
[ ] generated content disclaimer clear
```

---

## Tester demo minimum gate

Required:

```text
[ ] tester-only wording clear
[ ] page-count limit clear
[ ] no redistribution clear
[ ] legal folder included
[ ] feedback instructions included
[ ] sensitive document warning included
```

---

## Supporter package gate

Required before first paid Supporter package:

```text
[ ] beta EULA reviewed
[ ] Supporter terms drafted or referenced
[ ] package legal folder included
[ ] third-party notices reviewed enough for distribution
[ ] personal/internal use wording clear
[ ] page limit / feature difference clear
[ ] payment/refund path not misleading
```

---

## Pro package gate

Required before Pro package:

```text
[ ] Pro commercial terms drafted
[ ] commercial/internal use rights clear
[ ] third-party license audit completed
[ ] EULA reviewed
[ ] package legal files included
[ ] official download channel chosen
[ ] support/contact process defined
```

---

## Commercial gate status values

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
Package legal files are complete enough for the release type.

Conditional:
No obvious blocker, but specific file content still needs review.

Fail:
Required legal files or terms are missing.

Not reviewed:
No release should be published yet.
```

---

## Recommended next implementation milestone

Later implementation milestone:

```text
v0.3.12-voila-package-legal-files-copy-plan
```

or:

```text
v0.4.0-voila-private-repo-transition
```
