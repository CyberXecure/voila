# Voila! Limited Tester Demo Plan

## Milestone

v0.3.2-public-beta-limited-tester-demo-plan

## Purpose

Plan a safer limited tester demo before sending Voila! to external testers through LinkedIn or other public channels.

The current v0.3.1 Windows tester package proved that a tester-friendly ZIP can work locally, but it still behaves like a broad portable application.

For external testers, especially people who are not personally known, the preferred next step is a limited demo build.

## Product positioning

Name:

Voila! Limited Tester Demo

Short positioning:

Turn small PDF samples into learning and training materials.

Target experience:

Download.
Extract.
Double-click.
Test with a small non-confidential PDF.
Send feedback.

## Recommended demo limit

Recommended limit:

Maximum 5 pages per PDF.

This should apply to the tester demo regardless of PDF type.

Reasons:

- simple to explain
- enough for product feedback
- prevents broad real-world usage during private testing
- reduces processing time
- reduces accidental large-document testing
- makes the demo feel clearly limited
- avoids sending a full unlimited tool to strangers

## Alternative limits considered

### OCR-only limit

Limit only scanned/OCR pages.

Rejected for first demo because it is harder to explain to non-technical testers.

### Text-PDF unlimited, OCR limited

Rejected for first demo because it can still allow full manual/procedure processing.

### Time-limited demo

Rejected for now because it requires date logic, clock handling, expiration behavior and more support complexity.

### Account-based demo

Rejected for now because it requires cloud, accounts, auth and payment-like infrastructure.

## Recommended implementation approach

The future implementation milestone should add a single central page limit that is enforced before heavy processing starts.

Recommended constant:

VOILA_TESTER_DEMO_MAX_PAGES = 5

Recommended behavior:

- when a PDF has more than 5 pages, process only the first 5 pages or block with a clear message
- prefer blocking with a clear message for the first limited demo
- tell the tester to use a smaller sample PDF
- show the limit clearly in README-TESTERS.txt and UI text
- avoid silent truncation unless clearly documented

Recommended message:

This tester demo is limited to 5 pages per PDF. Please use a small non-confidential sample document.

## Recommended UI / user-facing text

Add a visible tester demo notice:

Voila! Limited Tester Demo

This version is limited to 5 pages per PDF and is intended only for private feedback.

Do not use confidential, personal, legal, medical, financial, safety-critical or compliance-critical documents.

Generated content must be reviewed by a human.

## Recommended package naming

Future local ZIP candidate:

voila-v0.3.2-public-beta-limited-tester-demo.zip

Supporting files:

- voila-v0.3.2-public-beta-limited-tester-demo.zip.sha256
- voila-v0.3.2-public-beta-limited-tester-demo-release-notes.md
- voila-v0.3.2-public-beta-limited-tester-demo-final-checklist.md
- voila-v0.3.2-public-beta-limited-tester-demo-test-log.md

## Tester audience

Recommended first outreach:

LinkedIn contacts who work with:

- PDFs
- manuals
- procedures
- onboarding
- training
- technical documentation
- course materials
- learning and development
- HR
- operations
- technical writing

Do not send the ZIP publicly.

Use LinkedIn only to identify interested testers.

Send the private ZIP link only after a short qualification message.

## Private tester qualification question

Before sending the demo link, ask:

Do you usually work with PDFs such as training materials, manuals, procedures, onboarding docs, course content or technical documentation?

Send the link only if the person has a relevant use case.

## Private testing notice

Recommended notice to include in README-TESTERS.txt and tester message:

This package is provided only for private testing and feedback.

It is not licensed for redistribution, modification, resale, republication, commercial use or use as the basis for a competing product.

Do not share this package or download link with others without explicit permission.

No LICENSE file is included because the licensing and commercial model are still under evaluation.

## What this plan does not solve

This demo limit is not a full security or licensing solution.

It reduces risk and clarifies intent, but it does not prevent all copying, reverse engineering or misuse.

For broader public distribution, future steps may still require:

- explicit license decision
- source-available or proprietary terms
- tester agreement
- commercial terms
- installer or signed binary
- stronger packaging model

## Scope of this milestone

This milestone is documentation-only.

Included:

- limited tester demo plan
- implementation checklist
- tester positioning
- recommended page limit
- recommended package naming
- recommended LinkedIn testing strategy
- risk notes

Excluded:

- no runtime code changes
- no page-limit implementation yet
- no ZIP rebuild
- no GitHub release upload
- no Git tag
- no LICENSE
- no payment flow
- no installer
- no cloud/accounts
- no new language packs
- no public tester ZIP

## Recommended next milestone

v0.3.2-public-beta-limited-tester-demo

That future milestone should implement the 5-page limit, rebuild the tester ZIP, validate local start/stop behavior and only then prepare a very small private LinkedIn tester round.
