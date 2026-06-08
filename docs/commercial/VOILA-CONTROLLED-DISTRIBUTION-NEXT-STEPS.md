# Voila Controlled Distribution Next Steps

## Purpose

Define practical next steps for Voila controlled public distribution after deciding on a proprietary/private-repository direction.

This document is planning-only and does not implement distribution changes.

---

## Current direction

Voila should move toward:

```text
private development
controlled public releases
clear beta terms
future Supporter / Pro licensing
official download channels
```

---

## Immediate next steps

### Step 1 — Complete privacy transition checklist

Confirm:

```text
what becomes private
what remains public
which release package is the public beta runtime package
where users should download Voila
where users should send feedback
```

### Step 2 — Clarify public download wording

Avoid:

```text
download the latest release
```

Prefer:

```text
download the public beta runtime package identified in the release notes
```

Reason:

```text
later release candidates or tester demo builds may not be the same as public runtime packages
```

### Step 3 — Prepare website/public landing page

Recommended public page sections:

```text
headline
short value proposition
screenshots
download CTA
beta terms link
known limitations
feedback CTA
contact
```

### Step 4 — Keep official release packages controlled

Each package should include:

```text
version
release type
release notes
SHA256
license/beta terms
known limitations
tester instructions
```

### Step 5 — Decide first monetization experiment

Recommended first monetization experiment:

```text
Supporter package
personal/internal use
higher page limit than demo
early builds
clear no-redistribution terms
```

---

## Suggested release channels

### Public beta

Use for:

```text
public evaluation
low-friction download
feedback collection
non-commercial testing
```

### Private tester

Use for:

```text
selected testers
limited demos
feedback before broader release
```

### Supporter

Use for:

```text
early paid users
higher limits
early-access builds
personal/internal license
```

### Pro

Use for:

```text
commercial/internal professional use
larger limits
advanced features
higher support expectations
```

---

## Recommended distribution checklist

Before any future package:

```text
[ ] package type is clear
[ ] version is clear
[ ] release notes are clear
[ ] beta terms or EULA included
[ ] third-party notices reviewed
[ ] checksum generated
[ ] package starts locally
[ ] package stops cleanly
[ ] no secrets included
[ ] no private docs included
[ ] download channel is official
```

---

## Recommended later milestones

```text
v0.3.7-voila-public-download-wording-polish
v0.3.8-voila-eula-for-windows-package-plan
v0.3.9-voila-third-party-license-audit-plan
v0.4.0-voila-private-repo-transition
v0.4.1-voila-supporter-package-plan
```

---

## Not included yet

This document does not implement:

```text
payment
license keys
activation
website upload
installer
code signing
new runtime package
repository visibility change
```
