# Voila Windows Package Complete Runtime Source Validation Checklist

Milestone:

`	ext
v0.3.48-voila-windows-package-complete-runtime-source-discovery
`

## Required before next ZIP rebuild

`	ext
[ ] actual API entrypoint selected
[ ] launcher helper supports selected entrypoint path
[ ] Python runtime strategy selected
[ ] dependencies available package-locally
[ ] frontend/static strategy selected
[ ] LanguageTool/Java decision selected
[ ] Tesseract/OCR decision selected
[ ] runtime source copy map approved
[ ] exclusion list applied
[ ] real launchers generated
[ ] package staging validates with -Strict
`

## Blocker to resolve

`	ext
v0.3.46 failed full service start because Voila API entrypoint was not found.
The next implementation must ensure the selected entrypoint exists inside the package runtime source.
`
