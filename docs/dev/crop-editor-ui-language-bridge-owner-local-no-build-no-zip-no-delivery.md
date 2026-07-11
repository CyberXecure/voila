# v0.7.51 Crop Editor UI language bridge

Status: COMPLETED / OWNER-LOCAL UI LANGUAGE BRIDGE PASS

Marker:
VOILA_V0_7_51_CROP_EDITOR_UI_LANGUAGE_BRIDGE_CHECK=PASS

## Scope

This milestone connects the standalone Crop Editor to the existing Voila UI language state for a small guarded area.

The bridge reads the existing UI language through `i18n.get_ui_language(PROJECT_ROOT)`.

## Implemented

- adds a local Crop Editor UI language helper
- sets Crop Editor `<html lang="ro">` or `<html lang="en">`
- adds a local EN/RO text helper
- localizes only the OCR Math sidecar import heading, button, browser confirmation, and fine note
- keeps Romanian strings in Python source with Unicode escapes to avoid console encoding corruption
- preserves existing import behavior
- preserves explicit owner-local import
- preserves no-auto-import on GET

## Explicitly unchanged

This milestone does not localize the entire Crop Editor.

This milestone does not change OCR Math importer behavior, Crop manifest write rules, backup behavior, duplicate source_candidate_id skipping, Course, Study, or Progress.

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
