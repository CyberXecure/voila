# Voila Private Repository and Controlled Release Plan

Milestone:

```text
v0.3.5-voila-private-repo-and-controlled-release-plan
```

## Strategic direction

Voila is a proprietary product.

The intended product direction is:

```text
private development repository
controlled public releases
clear beta terms
future Supporter / Pro licensing
commercial protection before broader distribution
```

This milestone is documentation-only. It does not change repository visibility, runtime behavior, packaging, dependencies, backend, frontend, or release assets.

---

## Why move toward private development?

Voila contains product-specific work that may become commercially valuable:

- PDF-to-course workflow
- OCR review workflow
- figure extraction workflow
- study mode
- progress dashboard
- local packaging and tester workflow
- language pack strategy
- public beta positioning
- future licensing and monetization plans

Keeping the full repository public makes it easier for others to inspect, copy, repackage, or imitate the product.

A private repository better supports a proprietary/commercial product strategy.

---

## Recommended repository model

### Private repository

Use the private repository for:

```text
source code
runtime implementation
backend/frontend logic
packaging scripts
build scripts
release automation
internal docs
commercial roadmap
licensing implementation
future Pro / Supporter features
```

### Public surface

Keep public only what is needed for product discovery and tester trust:

```text
README / landing page copy
screenshots
release notes
public beta ZIP or installer
SHA256 checksum
tester instructions
beta terms
license notice
support/contact details
issue/feedback channel if desired
```

---

## Controlled public releases

Public releases should be intentional and limited.

Recommended public release rules:

```text
publish only reviewed packages
include version number
include release notes
include SHA256 checksum
include beta terms / EULA
avoid exposing source code
avoid shipping secrets or private configs
avoid shipping internal scripts unless needed
avoid shipping old experimental artifacts
```

---

## Current public beta clarification

The public beta runtime package and later tester/demo builds may differ.

Recommended wording:

```text
The public beta runtime package is intended for evaluation and feedback.
Some later tester/demo builds may include page limits, release-candidate-only changes, or other restrictions.
Use the release notes to identify the correct package for public runtime testing.
```

---

## Migration principles

When moving toward private development:

```text
do not delete history carelessly
do not break current release links
do not remove license/beta terms
do not publish new runtime packages until reviewed
do not confuse public beta users with internal tester builds
keep public communication simple
keep proprietary rights clear
```

---

## Recommended transition steps

### Step 1 — Finish legal/documentation basis

Already started with:

```text
LICENSE.txt
BETA-TERMS.md
docs/legal/THIRD-PARTY-NOTICES.md
README License and beta terms section
```

### Step 2 — Audit public repository contents

Before making decisions, review:

```text
source code visibility
release package links
public docs
screenshots
sample PDFs
test data
third-party bundled components
any private/internal notes
any secrets or credentials
```

### Step 3 — Decide public/private split

Recommended split:

```text
private repo: full development
public release page: packages, docs, screenshots, terms
public website: landing page and CTA
```

### Step 4 — Preserve public beta trust

Keep public users informed:

```text
Voila remains available as public beta package.
Source code visibility may change as the product moves toward proprietary commercial development.
Public releases remain controlled through official channels.
```

### Step 5 — Prepare monetization structure

Future licensing options:

```text
Free beta / tester demo
Supporter package
Pro package
Commercial / Team package later
```

---

## What not to do yet

Do not yet:

```text
switch repository visibility without a public/private plan
publish a new package without checking license terms
claim production readiness
claim full legal/commercial readiness
add payment flow
add license activation runtime
remove public beta assets without replacement
```

---

## Recommended next milestone

```text
v0.3.6-voila-supporter-pro-licensing-plan
```

or:

```text
v0.3.6-voila-repo-privacy-transition-checklist
```
