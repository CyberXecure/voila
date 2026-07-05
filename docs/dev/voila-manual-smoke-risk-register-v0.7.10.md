# Voila v0.7.10 Owner-local Manual Smoke Risk Register

Milestone: `v0.7.10-owner-local-manual-smoke-evidence-no-build-no-distribution`

Policy:
- no build
- no ZIP
- no delivery
- no distribution
- owner-local only
- no feature changes
- no behavior changes
- no OCR/pages/course/Study/Progress rewrite
- no public UI expansion

## Purpose

This risk register prevents accidental behavior changes while collecting manual smoke evidence.

## Risk categories

| Risk | Examples | Required v0.7.10 handling |
| --- | --- | --- |
| Write-generating action | upload, generate, regenerate, save OCR, save concepts, answer Study/Review | Mark as `SKIPPED_WRITE`; do not automate |
| Destructive action | delete course, delete from library, study reset | Mark as `SKIPPED_DESTRUCTIVE`; do not execute |
| Runtime behavior change | changing Python app code, templates, routes, flags, generation logic | Not allowed |
| Public UI expansion | adding public pages, exposing owner routes publicly | Not allowed |
| Distribution leakage | ZIP, release, upload package, OneDrive share, GitHub release | Not allowed |
| Evidence packaging | screenshot bundle, package, external delivery | Not allowed |
| False confidence | marking unavailable artifact as PASS | Use `BLOCKED_NO_LOCAL_ARTIFACT` instead |
| Fix creep | fixing observed issues inside the evidence milestone | Use `OBSERVED_ISSUE_NO_FIX`; create a separate milestone later |

## Route/action risk classification

| Surface | Risk level | v0.7.10 handling |
| --- | --- | --- |
| GET/read-only pages | Low | Manual observation allowed |
| Owner-local OCR Math report GET routes | Low/Medium | Manual observation allowed only for existing local reports |
| POST answer/save routes | Medium | Skip unless a future explicit test milestone permits controlled fixture state |
| Generate/upload routes | High | Skip in this milestone |
| Delete/reset routes | High | Skip in this milestone |

## Required final statement

Every v0.7.10 final validation must include:

POLICY=no_build_no_zip_no_delivery_no_distribution_owner_local_only_no_behavior_changes