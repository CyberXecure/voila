# v0.8.41 Owner personal Manual Study workflow smoke — no share/no delivery

## Purpose

This milestone records the owner's personal Manual Study workflow smoke test before any tester sharing.

It follows:

- v0.8.38 package rebuild with packaged startup
- v0.8.39 extracted-package browser validation retry PASS
- v0.8.40 final no-delivery review PASS

## What is being tested

The owner personally checks whether the Manual Study workflow is understandable from the extracted package:

Home → Course Tools → Manual Learning Evidence / evidence workflow → export previews → Study normal → Manual Study default

## Important interpretation

This milestone does not require the owner to say the workflow is perfect.

If the technical flow works but the user experience is unclear, the correct result is:

`NEEDS_UX_POLISH`

If a real blocker is found, the correct result is:

`BLOCKED`

If the workflow is understandable and usable, the correct result is:

`PASS_OWNER_PERSONAL_CLEAR`

## Boundary

This milestone records owner personal smoke evidence only.

It does not rebuild the package.

It does not create a new ZIP.

It does not copy to OneDrive.

It does not create a share.

It does not deliver anything.

It does not distribute anything.

It does not create a public release.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

It does not change Study behavior.

It does not write Progress.

It does not mark answers.

It does not perform OCR rewrite.

It does not perform Formula OCR.

It does not write crop files.

## Package under test

`D:\dev\tester-runs\v0839\x\voila-v0.8.38-controlled-tester-windows-package-candidate`

This is the extracted package validated in v0.8.39.

## Policy

No OneDrive copy.

No share.

No delivery.

No distribution.

No public release.

Any future tester delivery requires a separate explicit owner-approved milestone.
