# Voila! Windows Tester Package Plan

## Milestone

v0.3.1-public-beta-windows-tester-package-plan

## Purpose

Prepare a tester-friendly Windows package for non-technical users.

The goal is to make Voila! easier to test externally without requiring Git, GitHub CLI, PowerShell knowledge, Python setup, manual dependency installation, or technical release verification.

Target tester experience:

1. Download ZIP.
2. Extract ZIP.
3. Double-click START-VOILA.bat.
4. Browser opens automatically.
5. Tester uploads a small PDF.
6. Tester reviews generated outputs.
7. Tester submits feedback.

## Why this is needed

The existing v0.3.0 Public Beta Language Pack RC1 is intentionally technical.

It validates:

- language-pack schema
- English and Romanian core packs
- sample packs
- runtime helper
- validator
- release-readiness documentation
- release-candidate documentation
- ZIP asset
- SHA256 checksum
- release notes
- final checklist
- test log

That is useful for technical release validation, but it is not friendly enough for non-technical early users.

For real product feedback, testers need a simple Windows package.

## Recommended package type

Recommended now:

- portable Windows ZIP

Not recommended yet:

- full installer
- payment flow
- cloud account system
- enterprise deployment
- auto-update system

## Proposed future asset name

voila-v0.3.1-public-beta-windows-tester-package.zip

Optional supporting assets:

- voila-v0.3.1-public-beta-windows-tester-package.zip.sha256
- voila-v0.3.1-public-beta-windows-tester-package-release-notes.md
- voila-v0.3.1-public-beta-windows-tester-package-final-checklist.md
- voila-v0.3.1-public-beta-windows-tester-package-test-log.md

## Intended package contents

Recommended contents:

- START-VOILA.bat
- STOP-VOILA.bat
- README-TESTERS.txt
- TESTING-GUIDE.md
- FEEDBACK-QUESTIONS.md
- LIMITATIONS.md
- TROUBLESHOOTING.md
- language-packs/
- app/runtime files needed by the existing Voila public beta
- optional small sample PDFs if safe and redistributable

## Tester positioning

The tester package should be described as:

Download, extract, double-click, test with a PDF.

No install.
No terminal.
No setup.

## What testers should test

Testers should check whether Voila! can help transform dense PDF documents into useful learning or training materials.

Target use cases:

- course PDFs
- study materials
- internal manuals
- company procedures
- onboarding documents
- technical documentation
- training content
- OCR review before content generation

Target outputs:

- course outline
- normalized outline
- cleaned course content
- glossary
- quiz
- flashcards
- OCR review artifacts

## Recommended test PDFs

Start with:

- small course PDF, 5-20 pages
- clean text PDF
- simple manual or procedure, 5-30 pages
- small scanned PDF, 2-5 pages, for OCR review testing
- non-confidential training document

Avoid for first tests:

- confidential documents
- personal data
- legal/medical/financial records
- huge scanned books
- very large PDFs
- image-heavy files
- complex tables/forms/signatures
- multi-column layouts

## Current limitations to communicate

Voila! is still in public beta.

Known limitations:

- The package is for testing, not production use.
- Output quality depends on PDF quality and structure.
- Scanned PDFs may require OCR review and correction.
- Very large PDFs may be slower or unreliable.
- Complex tables, forms, images and multi-column layouts may not convert perfectly.
- Generated content must be reviewed by a human.
- Do not use generated content as the only source of truth for legal, medical, financial, safety or compliance-critical decisions.
- English and Romanian are included in the current language-pack RC path.
- German, Spanish, Italian and Portuguese remain planned future expansion candidates.
- No cloud collaboration, accounts, payments or enterprise workflow exists yet.
- No LICENSE file has been added yet because the licensing/commercial model is still under evaluation.

## Scope of this milestone

This milestone is documentation-only.

Included:

- Windows tester package plan
- tester quickstart
- feedback questions
- limitations document
- package checklist

Excluded:

- no ZIP build
- no installer
- no runtime changes
- no UI changes
- no language-pack JSON changes
- no GitHub release upload
- no Git tag
- no LICENSE file
- no payment flow
- no forced de/es/it/pt language packs

## Next milestone

After this plan is reviewed and merged, the next milestone can be:

v0.3.1-public-beta-windows-tester-package

That future milestone may build the actual portable Windows ZIP for non-technical testers.
