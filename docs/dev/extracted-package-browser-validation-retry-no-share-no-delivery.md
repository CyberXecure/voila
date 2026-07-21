# v0.8.39 Extracted package browser validation retry — no share/no delivery

## Purpose

This milestone retries extracted-package browser validation using the v0.8.38 local ZIP candidate.

It follows:

- v0.8.35 extracted-package browser validation blocker
- v0.8.36 runtime strategy preflight
- v0.8.37 packaged startup bootstrap
- v0.8.38 package rebuild with packaged startup

## Validated package

`D:\dev\release-assets\voila\v0.8.38-package-rebuild-with-packaged-startup-no-share-no-delivery\voila-v0.8.38-controlled-tester-windows-package-candidate.zip`

## Validation flow

The validation must confirm:

1. package ZIP exists
2. package SHA256 matches its `.sha256` file
3. package contains `scripts/dev/start-voila-packaged.ps1`
4. package still excludes `.venv`
5. package is extracted only under `D:\dev\tester-runs`
6. extracted package is not inside the repo
7. extracted package is not inside OneDrive
8. packaged startup can run from extracted package root
9. extracted app reaches `/health`
10. extracted Home page loads
11. Home exposes Course Tools link for the validation course
12. Course Tools page loads from Home link
13. normal Study link opens `/study?pdf=...`
14. normal Study renders Manual Study default
15. Manual Study cards are visible
16. answer content remains read-only inside details
17. source metadata is visible
18. shadow Study link remains separate
19. dry-run link remains separate
20. normal Study falls back to legacy Study when `manual_study_items.preview.json` is temporarily unavailable
21. no Progress write is introduced
22. no answer marking is introduced
23. no Study POST endpoint is introduced
24. no OCR rewrite happens
25. no Formula OCR happens
26. no crop file write happens
27. no rebuild happens
28. no new ZIP is created
29. no OneDrive copy is created
30. no share is created
31. no delivery is performed
32. no distribution is performed
33. no public release is created

## Boundary

This milestone validates a previously rebuilt local ZIP candidate.

It does not rebuild the package.

It does not create a new ZIP.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

It does not change Study behavior.

It does not write Progress.

It does not mark answers.

It does not perform OCR rewrite.

It does not perform Formula OCR.

It does not write crop files.

It does not copy to OneDrive.

It does not create a share.

It does not deliver anything.

It does not distribute anything.

It does not create a public release.

## Policy

Package readiness remains blocked until this validation passes and a separate final no-delivery review is completed.

Sharing remains blocked.

Delivery remains blocked.

Distribution remains blocked.

Public release remains blocked.
