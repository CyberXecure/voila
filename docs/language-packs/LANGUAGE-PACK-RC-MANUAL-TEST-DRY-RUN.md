# Voila! Language Pack RC Manual Test Dry Run

Milestone: v0.2.42-public-beta-language-pack-rc-manual-test-dry-run  
Status: completed manual dry run with notes  
Scope: local manual validation only; no GitHub release upload, no Git tag, no public ZIP publish, no runtime/UI behavior change

## RC artifact

``text
ZIP:    D:\dev\releases\voila-v0240-lp-rc1-20260517-0914.zip
SHA256: 33DC31243F45AD499A889A12F4140779499EFCC0C6218C5BB011920CF36679BC
``

## Manual dry-run result

Result: PASS with notes.

The manual dry-run was executed from a clean extraction folder:

``text
D:\dev\manual-tests\voila-v0240-lp-rc1-20260517-0914-manual
``

Manual transcript path:

``text
D:\dev\manual-tests\voila-v0240-lp-rc1-20260517-0914-manual\MANUAL-DRY-RUN-TRANSCRIPT-PORT8765.txt
``

## Validation passed

The following checks passed:

- RC ZIP SHA256 matched expected value
- ZIP extracted successfully
- required runtime files were present
- required language-pack files were present
- Voila started from Run-Voila.ps1
- /health returned {"status":"ok"} on port 8765
- LanguageTool responded on port 8081
- Tesseract listed expected OCR languages: eng, osd, on, us
- browser/app opened
- manual PDF/OCR review flow was marked PASS
- Stop-Voila.ps1 stopped Voila and LanguageTool

## Notes

### Port verification note

The first manual dry-run attempt checked the wrong app port, 8780.

The corrected dry-run used the standalone runtime port, 8765, and /health passed.

At final shutdown, some temporary TCP entries on port 8765 remained briefly in FinWait2 / TimeWait states. These were treated as a verification note, not as a runtime failure, because the manual flow passed and the stop script reported the Voila service stopped.

### UI language consistency note

The UI is currently mixed English/Romanian.

Examples observed:

- English: Upload PDF, Choose File, Upload PDF, Generated, Source Mode, Generate course, Figures, Edit crops, Study, Review weak, Progress, Logs, Delete from library
- Romanian: Deschide cursul

This does not block the language-pack packaging RC validation, but it should be addressed before a polished public release.

Recommended follow-up:

``text
v0.2.43-public-beta-language-pack-ui-language-consistency-plan
``

## Safety

This milestone did not:

- upload assets to GitHub Releases
- create a Git tag
- publish the ZIP
- overwrite v0.2.0-public-beta assets
- change runtime behavior
- change UI behavior
- add or modify LICENSE files

## Decision

v0.2.42 validates that the local RC ZIP can pass manual functional testing.

The UI language consistency issue is documented as a follow-up, not as a blocker for language-pack packaging validation.
