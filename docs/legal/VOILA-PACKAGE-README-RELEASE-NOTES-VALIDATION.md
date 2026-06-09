# Voila Package README and Release Notes Validation

## Purpose

Define package README and release notes checks for future Voila Windows packages.

This is documentation-only.

---

## README purpose

The package README should help a non-technical user understand:

```text
what Voila is
what package type they downloaded
how to start Voila
how to stop Voila
where legal terms are located
what limitations apply
how to provide feedback
```

---

## README required topics

Check that README includes:

```text
[ ] product name
[ ] package type
[ ] version or release label
[ ] start instructions
[ ] stop instructions
[ ] legal folder reference
[ ] EULA reference
[ ] beta terms reference
[ ] third-party notices reference
[ ] known limitations
[ ] feedback/contact path
```

---

## Suggested README legal wording

```text
Before using this Voila package, review the legal/ folder.

This package includes:
- legal/EULA.txt
- legal/LICENSE.txt
- legal/BETA-TERMS.md
- legal/THIRD-PARTY-NOTICES.md
```

---

## Release notes purpose

Release notes should make clear:

```text
what changed
who the package is for
whether it is a runtime package
whether page limits apply
whether it is public beta, tester demo, or another release type
where legal terms are located
where checksum information is published
```

---

## Release notes required fields

Recommended fields:

```text
Release type:
Version:
Date:
Intended audience:
Runtime package: Yes / No
Page-count limits:
Commercial use:
Redistribution:
Legal files:
Known limitations:
SHA256:
Feedback/contact:
```

---

## Public download wording

Avoid:

```text
Download the latest release.
```

Use:

```text
Download the public beta runtime package identified in the release notes.
```

---

## Validation result

Use:

```text
Pass
Conditional
Fail
```

Definitions:

```text
Pass:
README and release notes include all required package information.

Conditional:
README or release notes are usable, but one or more advisory fields are missing.

Fail:
Package type, legal terms, start/stop instructions, or runtime status are unclear.
```
