# Voila! Limited Tester Demo Checklist

## Milestone

v0.3.2-public-beta-limited-tester-demo-plan

## Scope

Documentation-only checklist for planning a limited tester demo.

## Planning files

- [ ] docs/testers/VOILA-LIMITED-TESTER-DEMO-PLAN.md
- [ ] docs/testers/VOILA-LIMITED-TESTER-DEMO-CHECKLIST.md

## Recommended demo identity

- [ ] Name: Voila! Limited Tester Demo
- [ ] Positioning: PDF-to-learning / PDF-to-training demo
- [ ] Audience: selected external testers
- [ ] Distribution: private only
- [ ] Test duration: 10-15 minutes
- [ ] Documents: small, non-confidential PDFs only

## Recommended page limit

- [ ] Maximum 5 pages per PDF
- [ ] Limit should be easy to explain
- [ ] Limit should apply to the tester demo
- [ ] Limit should prevent large manual/procedure processing
- [ ] Limit should be documented clearly
- [ ] Limit should be visible before processing

## Future implementation requirements

Future implementation milestone should verify:

- [ ] page count is detected before heavy processing
- [ ] PDFs over 5 pages are blocked or clearly rejected
- [ ] tester receives a clear message
- [ ] OCR-heavy documents remain limited
- [ ] UI or route output explains the demo limit
- [ ] README-TESTERS.txt explains the demo limit
- [ ] generated output includes human-review warning where appropriate
- [ ] tests/smoke checks cover the limit

## Recommended message for blocked PDFs

This tester demo is limited to 5 pages per PDF. Please use a small non-confidential sample document.

## Future package requirements

Future limited demo package should include:

- [ ] START-VOILA.bat
- [ ] STOP-VOILA.bat
- [ ] START-VOILA-DEBUG.bat
- [ ] STOP-VOILA-DEBUG.bat
- [ ] README-TESTERS.txt
- [ ] tester docs
- [ ] clean data folder
- [ ] .venv runtime if needed
- [ ] no old PDFs
- [ ] no .release-cache
- [ ] no LICENSE
- [ ] no payment logic
- [ ] no new language packs

## LinkedIn tester strategy

- [ ] Post publicly without ZIP link
- [ ] Ask for 3-5 interested testers
- [ ] Target people who work with PDFs/manuals/procedures/training/onboarding
- [ ] Qualify testers in private message
- [ ] Send link only to selected testers
- [ ] Ask testers not to use sensitive documents
- [ ] Ask testers not to share the ZIP/link
- [ ] Collect feedback in tracker

## Risk controls

- [ ] private ZIP link only
- [ ] no public download link
- [ ] no broad Reddit/Discord ZIP sharing
- [ ] no enterprise/company-wide distribution
- [ ] private testing notice included
- [ ] no confidential documents
- [ ] no commercial promise
- [ ] no license promise
- [ ] no unlimited usage promise

## Explicit exclusions

This milestone must not add:

- [ ] runtime code changes
- [ ] page-limit implementation
- [ ] release ZIP
- [ ] GitHub release upload
- [ ] Git tag
- [ ] LICENSE file
- [ ] payment flow
- [ ] installer
- [ ] cloud accounts
- [ ] new language packs
- [ ] public download link

## Final verification

Before merge:

- [ ] only docs/testers files changed
- [ ] no LICENSE file exists
- [ ] no v0.3.2 tag exists
- [ ] no release asset changed
- [ ] no runtime code changed
- [ ] working tree clean after commit
