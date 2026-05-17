# Voila! Language Pack RC Manual Test Final Checklist

Milestone: v0.2.42-public-beta-language-pack-rc-manual-test-dry-run  
Status: PASS with notes

## Manual validation

- [x] RC ZIP SHA256 matched
- [x] ZIP extracted successfully
- [x] required runtime files present
- [x] required language-pack files present
- [x] Voila started from Run-Voila.ps1
- [x] /health returned ok on port 8765
- [x] LanguageTool responded on port 8081
- [x] Tesseract listed eng, osd, ron, rus
- [x] browser/app opened
- [x] PDF/OCR review flow marked PASS
- [x] Stop-Voila.ps1 stopped services

## Notes

- [x] wrong-port issue documented: 8780 was incorrect for standalone manual test
- [x] final TCP FinWait2/TimeWait note documented
- [x] mixed English/Romanian UI documented as follow-up

## Safety

- [x] no GitHub release upload
- [x] no Git tag
- [x] no public ZIP publish
- [x] v0.2.0-public-beta assets unchanged
- [x] no runtime behavior change
- [x] no UI behavior change
- [x] no LICENSE change

## Decision

- [x] PASS with notes
- [x] create follow-up milestone for UI language consistency
