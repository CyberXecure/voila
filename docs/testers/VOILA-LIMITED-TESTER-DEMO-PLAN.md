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

Maximum 12 pages per PDF.

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

VOILA_TESTER_DEMO_MAX_PAGES = 12

Recommended behavior:

- when a PDF has more than 12 pages, process only the first 12 pages or block with a clear message
- prefer blocking with a clear message for the first limited demo
- tell the tester to use a smaller sample PDF
- show the limit clearly in README-TESTERS.txt and UI text
- avoid silent truncation unless clearly documented

Recommended message:

This tester demo is limited to 12 pages per PDF. Please use a small non-confidential sample document.

## Recommended UI / user-facing text

Add a visible tester demo notice:

Voila! Limited Tester Demo

This version is limited to 12 pages per PDF and is intended only for private feedback.

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

## PDF variety testing update

The limited tester demo should not be tested with only one ideal PDF.

For better product feedback, selected testers should be encouraged to test several small, non-confidential PDF samples.

Technical limit:

- maximum 12 pages per PDF

Recommended tester limit:

- 3 to 5 PDFs per tester
- approximately 15 to 25 pages total per tester

This PDF-count limit is a communication guideline, not a technical enforcement requirement for the first demo.

## Recommended PDF sample types

Ask testers to use varied PDF types when possible:

1. Clean text PDF

Examples:

- short course material
- simple guide
- article
- structured document with headings

Goal:

- test basic extraction and course/quiz generation

2. PDF with images or diagrams

Examples:

- technical manual
- instructions with screenshots
- diagrams
- illustrated process guide

Goal:

- check whether Voila remains useful when visual material is present
- check whether surrounding text is extracted well
- identify where diagram handling is weak

3. Scanned or OCR-heavy PDF

Examples:

- scanned document
- photographed page converted to PDF
- low-volume OCR sample

Goal:

- test OCR review behavior
- identify OCR correction needs

4. PDF with tables, lists or procedures

Examples:

- SOP
- checklist
- internal procedure
- operating instructions
- structured training material

Goal:

- test procedural learning/training value
- check whether quiz/flashcards remain useful

5. Mixed-layout PDF

Examples:

- text + images + tables
- headings + screenshots
- multi-section documentation

Goal:

- identify realistic weaknesses before public distribution

## What not to promise

Do not promise perfect handling of:

- complex diagrams
- technical drawings
- dense tables
- forms
- signatures
- complex multi-column layouts
- image-only documents
- safety-critical interpretation

The demo should be positioned honestly:

The goal is not perfect conversion. The goal is to understand where Voila is useful, where it fails, and which outputs are worth improving.

## Recommended tester instruction

For this limited demo, please test up to 3-5 small PDFs, each with a maximum of 12 pages.

Useful samples:

- one clean text PDF
- one PDF with images or diagrams
- one scanned/OCR PDF
- optionally, one manual, procedure, onboarding or training document
- optionally, one mixed-layout document

Please do not use confidential, personal, legal, medical, financial, safety-critical or sensitive documents.

## Additional feedback questions

Ask testers:

1. What type of PDF did you test?
   - clean text
   - scanned/OCR
   - images/diagrams
   - tables/lists
   - manual/procedure
   - training/onboarding
   - mixed layout

2. Which PDF type worked best?

3. Which PDF type failed or was confusing?

4. Did Voila handle images/diagrams acceptably?

5. Did the generated content remain useful even when images/diagrams were not fully understood?

6. Did tables, lists or procedures produce useful learning/training output?

7. Would this help with real manuals, procedures or onboarding documents if improved?

## Implementation impact

The future implementation milestone should still enforce only one simple technical limit first:

- maximum 12 pages per PDF

Do not add account-based limits, total-document counters or usage tracking yet.

The recommended 3-5 PDF limit should remain a tester instruction for now.
