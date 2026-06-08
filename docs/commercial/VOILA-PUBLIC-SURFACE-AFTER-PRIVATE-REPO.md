# Voila Public Surface After Private Repository

## Purpose

Define what should remain publicly visible after Voila moves toward private development.

The goal is to keep product trust and tester access while protecting source code and commercial strategy.

---

## Recommended public surface

After the development repository becomes private, the public surface should focus on product presentation and controlled distribution.

Recommended public assets:

```text
product landing page
short README / public product description
screenshots
public beta release notes
public beta runtime package or installer
SHA256 checksum
beta terms
license notice
support/contact information
feedback instructions
known limitations
```

---

## What should move private

Recommended private-only material:

```text
source code
backend implementation
frontend implementation
runtime internals
packaging scripts
build scripts
release automation
internal architecture notes
commercial roadmap
future licensing implementation
experimental features
test data that is not meant for public use
```

---

## Public GitHub options

### Option A — Make current repository private

Pros:

```text
fastest path
protects existing source history
keeps issues/PRs/history in one place
simple to understand internally
```

Cons:

```text
public README disappears from repository view
public users may lose easy source/release navigation
release visibility may need verification
external links may need updates
```

### Option B — Keep a separate public showcase repository

Pros:

```text
public product page remains on GitHub
source stays private
public README and screenshots remain easy to access
release links can be curated
```

Cons:

```text
requires maintaining two repositories
requires careful separation
risk of outdated public docs
```

### Option C — Use website as primary public surface

Pros:

```text
best product positioning
no need to expose source repository
better for commercial product
clearer CTA and download flow
```

Cons:

```text
requires website maintenance
GitHub discovery may be reduced
download hosting must be managed carefully
```

---

## Recommended approach

Recommended practical approach:

```text
make development repository private
keep official public releases controlled
use CX Trading / CyberXecure website for product presentation
optionally create a small public showcase repository later
```

---

## Public messaging

Suggested short wording:

```text
Voila is proprietary beta software. Development is private, while official public beta packages and documentation are distributed through controlled release channels.
```

Suggested longer wording:

```text
Voila is moving toward private development as a proprietary product. Public beta packages, release notes, screenshots, beta terms, and feedback instructions remain available through official channels. Source code access is not required to test the public beta package.
```

---

## Public release page expectations

Each public release should include:

```text
version
release type
package file
SHA256 checksum
release notes
known limitations
license / beta terms link
tester instructions
contact / feedback channel
```

---

## Public docs that should remain available

Recommended:

```text
README summary
LANDING-PAGE-CONTENT.md or website equivalent
SCREENSHOT-SHOWCASE-GUIDE.md or public images
FEEDBACK-COLLECTION-PLAN.md or simplified public feedback page
LICENSE.txt
BETA-TERMS.md
public release notes
```

---

## What not to expose publicly

Avoid exposing:

```text
internal pricing assumptions
license key implementation plans
private technical shortcuts
internal QA notes with weaknesses
private release scripts
local machine paths
private sample files
unreleased commercial features
```
