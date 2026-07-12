# v0.7.57 Fix visible raw bottom navigation JavaScript

Status: COMPLETED / RAW JAVASCRIPT TEXT FIXED

Marker:
VOILA_V0_7_57_FIX_VISIBLE_RAW_BOTTOM_NAV_JAVASCRIPT_CHECK=PASS

Evidence root:
D:\dev\tester-runs\voila-v0.7.57-fix-visible-raw-bottom-nav-javascript-owner-local-no-build-no-zip-no-delivery

Evidence files:
- V0.7.57-BOTTOM-NAV-SOURCE-HITS.json
- V0.7.57-BOTTOM-NAV-HTML-BEFORE-EVIDENCE.json
- V0.7.57-BOTTOM-NAV-HTML-AFTER-EVIDENCE.json
- V0.7.57-course-tools-before.html
- V0.7.57-course-tools-after.html
- V0.7.57-quick-tools-before.html
- V0.7.57-quick-tools-after.html

## Scope

This milestone fixes the visible raw JavaScript text at the bottom of the Course Tools / Quick Tools pages.

It does not change Course Tools OCR Math lookup, which was already fixed in v0.7.56.

## Root cause

The bottom navigation JavaScript block uses the script tag marker:

`<script id="voila-tester-flow-bottom-nav-v0724">`

A later bottom navigation polish CSS block accidentally targeted the script marker selector:

`#voila-tester-flow-bottom-nav-v0724`

That made the script tag render visibly as raw JavaScript text in the page.

## Fix

v0.7.57 changes the bottom navigation polish CSS selectors to target the injected nav element instead of the script tag marker.

Before:

- `.voila-tester-flow-bottom-nav-v0724`
- `#voila-tester-flow-bottom-nav-v0724`
- `.voila-tester-flow-bottom-nav-v0724 a`
- `#voila-tester-flow-bottom-nav-v0724 a`

After:

- `.voila-tester-flow-bottom-nav`
- `#voilaTesterFlowBottomNav`
- `.voila-tester-flow-bottom-nav a`
- `#voilaTesterFlowBottomNav a`

## HTTP / HTML validation

After patch:

- `/course-tools?pdf=03-pag-30-34-vectori-trigonometrie.pdf` returns HTTP 200
- `/quick-tools` returns HTTP 200
- `css_targets_script_marker` is false
- `css_targets_nav_id` is true
- `css_targets_nav_class` is true
- `has_raw_js_visual_risk` is false
- no traceback marker is present

## Manual visual validation

Manual browser validation confirmed:

- Course Tools still opens
- OCR Math card remains unavailable and does not block
- raw JavaScript text is no longer visible at the bottom of the page

## Possible visual polish follow-up

A small empty outline/spacing artifact may still be visible near the bottom-left area of the page.

This milestone does not treat that as the same blocker because the visible raw JavaScript text is fixed.

If needed, handle that as a separate small visual polish milestone.

## Tester decision

DO NOT package for testers yet.
DO NOT create ZIP.
DO NOT share.
DO NOT deliver.

A full tester-readiness audit must be rerun after this fix before any tester package.

## Explicitly unchanged

No OCR Math lookup change.
No import click.
No import logic change.
No OCR text rewrite.
No Course rewrite.
No Study rewrite.
No Progress rewrite.
No build.
No ZIP.
No share.
No delivery.
No distribution.
