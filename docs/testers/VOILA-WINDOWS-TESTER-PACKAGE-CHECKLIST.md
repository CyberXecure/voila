# Voila! Windows Tester Package Checklist

## Milestone

v0.3.1-public-beta-windows-tester-package-plan

## Scope

Documentation-only checklist for preparing a future tester-friendly Windows package.

## Required documents

- [ ] docs/testers/VOILA-WINDOWS-TESTER-PACKAGE-PLAN.md
- [ ] docs/testers/VOILA-WINDOWS-TESTER-PACKAGE-CHECKLIST.md
- [ ] docs/testers/VOILA-TESTER-QUICKSTART.md
- [ ] docs/testers/VOILA-TESTER-FEEDBACK-QUESTIONS.md
- [ ] docs/testers/VOILA-TESTER-LIMITATIONS.md

## Package goal

Future tester package should support:

- [ ] download
- [ ] extract
- [ ] double-click start
- [ ] browser opens locally
- [ ] upload small PDF
- [ ] generate learning/training outputs
- [ ] collect feedback

## Non-technical tester requirements

The future package should avoid requiring:

- [ ] Git
- [ ] GitHub CLI
- [ ] manual Python setup
- [ ] manual Java setup
- [ ] manual Tesseract setup
- [ ] PowerShell commands
- [ ] command-line troubleshooting for the first test

## Future package contents to verify

Recommended:

- [ ] START-VOILA.bat
- [ ] STOP-VOILA.bat
- [ ] README-TESTERS.txt
- [ ] TESTING-GUIDE.md
- [ ] FEEDBACK-QUESTIONS.md
- [ ] LIMITATIONS.md
- [ ] TROUBLESHOOTING.md
- [ ] required runtime files
- [ ] required app files
- [ ] language-packs directory
- [ ] safe sample PDFs, only if redistributable

## Future package behavior

Expected:

- [ ] START-VOILA.bat starts local services
- [ ] browser opens automatically
- [ ] app is reachable locally
- [ ] tester can upload a small PDF
- [ ] tester can generate outputs
- [ ] STOP-VOILA.bat stops local services
- [ ] common errors are explained in troubleshooting docs

## Communication requirements

The public message should clearly say:

- [ ] this is a public beta / tester package
- [ ] this is not a finished commercial product
- [ ] generated content requires human review
- [ ] output quality depends on input PDF quality
- [ ] sensitive documents should not be used for early tests
- [ ] EN/RO are current language-pack focus
- [ ] de/es/it/pt are planned future candidates only
- [ ] no LICENSE has been added yet

## Explicit exclusions

This milestone must not add:

- [ ] LICENSE file
- [ ] installer
- [ ] payment system
- [ ] cloud accounts
- [ ] large new features
- [ ] new language packs
- [ ] runtime changes
- [ ] release tag
- [ ] GitHub release upload
- [ ] rebuilt v0.3.0 RC1 asset

## Final verification

Before merging:

- [ ] git status is clean after commit
- [ ] only docs/testers files were added
- [ ] no release asset was changed
- [ ] no LICENSE file exists
- [ ] no language-pack JSON changed
- [ ] no runtime source changed
- [ ] no Git tag was created
- [ ] existing v0.3.0 RC1 remains unchanged
