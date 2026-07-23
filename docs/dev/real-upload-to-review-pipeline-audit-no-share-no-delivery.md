# v0.8.64 Real upload-to-review pipeline audit — no share/no delivery

## Verdict

`V0.8.64_AUDIT_VERDICT=BLOCKED_FOR_TESTER_SHARE`

The current package must not be staged for testers yet.

## Product decision

The user-facing visual/OCR Math flow must be:

`PDF page image -> bbox -> crop -> OCR Math on crop -> manual validation -> clean Study`

## Deprecated for user-facing flow

Global OCR Math before bbox/crop is deprecated for the user-facing flow.

Old shrink/preview/hybrid figure/crop UI must be removed from user-facing navigation or clearly deprecated.

## Current findings

The current `/generate` sequence runs the global OCR Math report hook after page extraction and before bbox/crop-based review.

LanguageTool exists in the project, but the audit did not prove that LanguageTool artifacts are automatically produced by the main `/generate` pipeline.

Existing visual tooling includes bbox/crop candidates and also older hybrid/shrink crop flows.

## Required next milestone

`v0.8.65-owner-local-bbox-crop-ocrmath-pipeline-plan-no-share-no-delivery`

The next milestone should define the canonical bbox/crop pipeline and remove/deprecate old user-facing shrink/hybrid routes before any tester share.

## Policy

No build.

No ZIP.

No OneDrive staging.

No share link.

No tester delivery.

No distribution.

No public release.

This milestone is audit documentation and validation only.
