# Voila! Monetization Plan

Status: draft  
Milestone: v0.2.1-public-beta-monetization  
Base release: v0.2.0-public-beta  
License status: under evaluation

Voila! is currently published as a public beta. The project is visible publicly for transparency, testing, feedback, and early community validation.

The final licensing and commercial model are still being evaluated. Until a license is explicitly added to this repository, do not assume that the project is MIT, Apache, GPL, or otherwise open-source licensed.

This document describes the intended monetization direction without changing the current public beta release.

---

## Goals

The monetization model should:

- keep the public beta useful and honest
- allow real users to test Voila! before paying
- preserve the possibility of a commercial version
- avoid locking the project too early into a license model
- keep sensitive business logic and payment infrastructure out of the public repo until ready
- support both individual users and business users

---

## Proposed tiers

### 1. Community

Audience:

- learners
- hobby users
- testers
- early adopters
- people who want to try Voila! locally

Possible positioning:

- public beta access
- local usage
- basic PDF/manual learning workflow
- feedback welcome
- no guaranteed support
- no commercial SLA

What may be public:

- public beta source code
- release ZIP
- checksums
- release notes
- setup instructions
- issue templates
- basic documentation
- roadmap-level discussion

What should not be promised yet:

- long-term free unlimited usage
- commercial usage rights
- redistribution rights
- white-label rights
- guaranteed support
- final open-source license

---

### 2. Supporter

Audience:

- users who like the project
- early supporters
- people who want to help development continue

Possible benefits:

- supporter mention, if requested
- early access notes
- priority feedback review
- vote on roadmap priorities
- supporter-only updates, if a channel is created later

Possible channels:

- GitHub Sponsors
- Buy Me a Coffee
- Ko-fi
- Gumroad support product
- Lemon Squeezy support product

Important:

Supporter payments should be framed as support for development, not as a license purchase, unless a paid license is explicitly created later.

---

### 3. Pro

Audience:

- individual power users
- translators
- trainers
- technical writers
- people who use Voila! regularly

Possible paid features later:

- larger batch processing
- advanced export options
- saved projects
- advanced language packs
- improved OCR workflows
- custom glossary
- translation memory
- offline language tooling bundles
- priority packaging/installer builds
- automatic update channel

Possible distribution:

- paid ZIP / installer
- license key
- Gumroad
- Lemon Squeezy
- direct invoice for Romanian/EU customers

Important:

Do not implement licensing/payment enforcement before the product value is clearer.

---

### 4. Business

Audience:

- companies
- training providers
- technical documentation teams
- service providers
- internal knowledge teams

Possible business offer:

- commercial usage license
- deployment help
- custom language packs
- custom templates
- company glossary
- onboarding session
- priority support
- private builds
- invoice-based payment
- optional maintenance plan

Possible pricing style:

- one-time setup fee
- annual maintenance
- per-seat license
- per-company license
- custom quote

Important:

Business terms should be written separately from the public beta documentation.

---

## What should stay public for now

The public repository may include:

- public beta source code
- release notes
- build/test logs
- setup instructions
- user documentation
- high-level roadmap
- known limitations
- support instructions
- monetization direction
- license status note

Reason:

This keeps the project transparent and testable while avoiding premature licensing commitments.

---

## What should not be public yet

Do not publish yet:

- final paid license text
- private customer terms
- private business proposals
- license key logic
- payment provider secrets
- API keys
- signing keys
- private analytics keys
- production payment webhooks
- customer lists
- paid support commitments
- unreleased commercial-only feature source code, if later separated

---

## README positioning

Recommended README message:

Voila! is currently available as a public beta for evaluation and feedback. The final licensing and commercial model are still under review. Until a license is explicitly published in this repository, please do not assume MIT, Apache, GPL, or another open-source/commercial license.

---

## GitHub Sponsors draft text

Suggested profile/repository text:

Support Voila!

Voila! is a public beta project focused on turning PDFs and technical manuals into practical learning material. Sponsorship helps cover development time, testing, packaging, documentation, and future language/runtime improvements.

Current focus:

- stable Windows packaging
- better PDF/manual workflows
- language pack improvements
- local-first learning tools
- documentation and public beta feedback

Sponsorship does not currently grant a commercial license or guaranteed support unless a specific paid plan is published later.

---

## Paid download draft text

Suggested Gumroad / Lemon Squeezy text:

Voila! Public Beta Supporter Package

Voila! helps transform PDF documents and technical manuals into structured learning material.

This supporter package helps fund continued development, testing, documentation, and packaging.

Included:

- current public beta build
- checksum file
- release notes
- setup instructions
- public beta documentation

Important:

This is an early public beta. The final licensing and commercial model are still under evaluation. Purchasing this package supports development and does not yet grant a separate commercial license unless explicitly stated in a future paid license.

---

## Future decisions

Before adding a LICENSE file, decide:

- fully open-source or source-available
- permissive or copyleft
- dual license or commercial license
- whether public repo remains complete or becomes community edition
- whether Pro/Business features live in the same repo or a private repo
- contribution policy
- contributor license agreement, if needed

---

## Recommended next milestone after this

v0.2.2-public-beta-support-page

Possible scope:

- add support links
- add funding URL, if ready
- create GitHub Sponsors profile text
- prepare paid download page
- decide whether to add .github/FUNDING.yml
- improve README positioning
