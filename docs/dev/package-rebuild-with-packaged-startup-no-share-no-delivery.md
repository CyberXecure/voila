# v0.8.38 Package rebuild with packaged startup — no share/no delivery

## Purpose

This milestone rebuilds the local tester ZIP candidate with the packaged startup bootstrap added in v0.8.37.

It follows:

- v0.8.35 extracted-package browser validation blocker
- v0.8.36 runtime strategy preflight
- v0.8.37 packaged startup bootstrap

## Package change

The new local package candidate must include:

`scripts/dev/start-voila-packaged.ps1`

The package must still exclude `.venv`.

The package must remain owner-local until extracted-package browser validation passes and a separate final no-delivery review is completed.

## Boundary

This milestone creates a local ZIP candidate only under `D:\dev\release-assets`.

This milestone does not copy to OneDrive.

This milestone does not create a share.

This milestone does not deliver anything.

This milestone does not distribute anything.

This milestone does not create a public release.

This milestone does not modify `services/api/web_app.py`.

This milestone does not add a route.

This milestone does not add a POST endpoint.

This milestone does not change Study behavior.

This milestone does not write Progress.

This milestone does not mark answers.

This milestone does not perform OCR rewrite.

This milestone does not perform Formula OCR.

This milestone does not write crop files.

This milestone does not perform extracted-package browser validation.

## Required next step

v0.8.39 must retry extracted-package browser validation using this rebuilt package.

## Policy

Package readiness remains blocked until extracted-package validation passes.

Sharing remains blocked.

Delivery remains blocked.

Distribution remains blocked.

Public release remains blocked.
