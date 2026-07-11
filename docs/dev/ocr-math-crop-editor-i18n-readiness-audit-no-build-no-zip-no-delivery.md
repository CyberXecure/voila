# v0.7.50 OCR Math Crop Editor i18n readiness audit

Status: COMPLETED / I18N READINESS AUDIT PASS

Marker:
VOILA_V0_7_50_OCR_MATH_CROP_EDITOR_I18N_READINESS_AUDIT_CHECK=PASS

## Scope

This milestone records an owner-local i18n readiness audit for the Crop Editor OCR Math sidecar import UI.

It is documentation/check-only.

No product behavior is changed.

## Finding

Crop Editor is currently a standalone FastAPI app with hard-coded English UI strings.

The main Voila web app already has UI language support through the existing i18n/_ut mechanism and Quick Tools language selector, but Crop Editor is not yet connected to that mechanism.

Therefore, adding a hard-coded practical readiness note in only English, only Romanian, or manually bilingual EN/RO would not be the correct final design.

## Decision

Do not commit the v0.7.50 hard-coded readiness note.

Do not add partial Crop Editor localization in this milestone.

Keep this milestone as an audit/readiness checkpoint.

## Safe next step

A separate future milestone may connect Crop Editor to the existing Voila UI language setting and then add translated EN/RO strings through a guarded, explicit implementation.

## Explicitly unchanged

This milestone does not add:

- OCR Math import behavior changes
- automatic import
- Crop Editor i18n implementation
- Course integration
- Study integration
- Progress integration
- public UI
- tester delivery
- build artifacts
- ZIP package
- share link
- distribution

## Safety contract

No OCR text rewrite.
No Course rewrite.
No Study rewrite.
No Progress rewrite.
No automatic Crop manifest rewrite on GET.
No build.
No ZIP.
No share.
No delivery.
No distribution.
