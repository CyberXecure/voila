# Voila Private Repository Migration Risks

## Purpose

Document risks before changing the Voila repository from public to private development.

This document is a planning aid. It does not change repository visibility.

---

## Main risks

### Broken public links

Risk:

```text
Existing public links to README, files, screenshots, docs, or source paths may stop working or become inaccessible.
```

Mitigation:

```text
identify important links before changing visibility
move public-facing material to website or public showcase repo
keep release notes and download instructions stable
```

---

### Confused beta users

Risk:

```text
Users may think the product was abandoned if the source repository becomes private.
```

Mitigation:

```text
publish a clear public note
keep public beta download channel available
explain that development is private but product is still active
```

---

### Release asset visibility uncertainty

Risk:

```text
GitHub release behavior and asset visibility may change depending on repository visibility and user access.
```

Mitigation:

```text
verify release asset access after visibility change
consider hosting official public downloads on website later
keep SHA256 checksums available
```

---

### Loss of public trust

Risk:

```text
Some users prefer open repositories and may view private development negatively.
```

Mitigation:

```text
be clear that Voila is proprietary beta software
provide screenshots, release notes, checksums, and terms
make tester workflow simple and transparent
```

---

### Accidental exposure before migration

Risk:

```text
Sensitive implementation details, internal strategy, or private files may already be in public history.
```

Mitigation:

```text
audit repository before wider distribution
review docs and packages
avoid adding secrets
do not rely on making repo private as a way to erase already-public history
```

---

### License confusion

Risk:

```text
Users may assume public GitHub access meant open-source rights.
```

Mitigation:

```text
keep LICENSE.txt and BETA-TERMS.md visible
state that public visibility does not mean open-source licensing
avoid using open-source language unless an explicit license is chosen
```

---

### Commercial roadmap exposure

Risk:

```text
Competitors can read monetization and product plans if commercial docs remain public.
```

Mitigation:

```text
move detailed commercial strategy private later
keep public messaging simple
do not expose implementation details for Pro / Supporter features
```

---

### Tester package confusion

Risk:

```text
Public beta runtime packages and tester demo builds may have different limits.
```

Mitigation:

```text
label releases clearly
use release type names consistently
document page limits per package
avoid saying latest release if release types differ
```

---

## High-risk items to review before changing visibility

```text
GitHub Releases
README download instructions
screenshots
docs/public
docs/legal
docs/commercial
release package ZIP contents
sample PDFs
generated course artifacts
local paths in docs
scripts that include machine-specific assumptions
```

---

## Recommended decision gate

Do not change repository visibility until:

```text
public surface plan exists
release visibility plan exists
beta terms are clear
commercial docs are reviewed for what should remain public
important links are identified
website or public showcase path is chosen
```
