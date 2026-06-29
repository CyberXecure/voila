# v0.6.9 Controlled Tester Package Copy Validation Dry-Run — No Copy, No Build, No Distribution

Status: implementation milestone
Scope: owner-controlled copy validation dry-run only
Copy: explicitly blocked
Build: explicitly blocked
Distribution: explicitly blocked

## Purpose

This milestone validates the copy plan from v0.6.8 without copying runtime files, creating a staging tree, approving source copies, building, zipping, creating an installer, staging a release archive, or distributing anything.

It follows the v0.6.8 copy plan and records whether each planned copy entry is still valid for a future copy milestone.

This milestone does not create a runnable package and does not copy any package content now.

## Inputs

- v0.6.8 controlled tester package copy plan no-copy no-build no-distribution must exist on main.
- v0.6.7 controlled tester package source allowlist plan no-build no-distribution must exist on main.
- v0.6.6 controlled tester package source validation dry-run no-build no-distribution must exist on main.
- v0.6.5 controlled tester package source selection dry-run no-build no-distribution must exist on main.
- v0.6.4 controlled tester package build plan no-build no-distribution must exist on main.
- v0.6.3 controlled tester package contents manifest no-build no-distribution must exist on main.
- v0.6.2 controlled tester package staging local-only no-distribution must exist on main.
- v0.6.1 controlled tester package dry-run no-distribution must exist on main.
- v0.6.0 controlled tester candidate decision must exist on main.
- Hidden owner Exam Prep preview remains owner-only and local-only.

## Allowed in this milestone

- Add this copy-validation dry-run policy document.
- Add a local validation script.
- Create or refresh a local-only copy-validation evidence directory outside the git repository.
- Write a local-only copy-validation JSON and README into that evidence directory.
- Validate planned source paths and planned destination strings from the copy-plan model.
- Confirm that every validated copy entry remains `copy_allowed_now = false`.
- Confirm that no runtime files were copied and no actual build or distribution happened.

## Explicitly blocked in this milestone

- No runtime file copy.
- No package content copy.
- No copy execution.
- No staging tree creation.
- No package build.
- No package source approval.
- No source allowlist approval.
- No source allowlist enforcement.
- No ZIP creation.
- No EXE creation.
- No MSI creation.
- No installer creation.
- No runnable tester package creation.
- No release archive creation.
- No release asset staging.
- No code signing.
- No checksum publication.
- No OneDrive upload.
- No GitHub release.
- No public website upload.
- No public UI.
- No public navigation.
- No tester UI.
- No activation for external testers.
- No submit flow.
- No session persistence.
- No attempt persistence.
- No progress persistence or update.
- No live scoring.
- No cloud/API requirement.

## Local copy-validation evidence

The local copy-validation evidence directory is intentionally outside the repository:

```text
D:\dev\release-assets\voila\v0.6.9-controlled-tester-package-copy-validation-dry-run-no-copy-no-build-no-distribution
```

Expected files:

```text
COPY-VALIDATION-README.txt
COPY-VALIDATION-DRY-RUN.json
```

These files are local evidence only and must not be uploaded, shared, packaged, or committed unless a later milestone explicitly requests a sanitized artifact.

## Copy validation policy

The copy-validation dry-run may inspect these source paths only:

- `services`
- `services/api`
- `scripts/dev`
- `docs`
- `LICENSE.txt`
- `scripts/dev/check-controlled-tester-package-build-plan-no-build-no-distribution.ps1`

Every validated copy entry must remain:

```text
planned_only = true
source_exists_checked = true
destination_string_checked = true
copy_allowed_now = false
copy_executed_now = false
copied_now = false
approved_for_package_now = false
```

This milestone records copy validation only. It does not approve, enforce, copy, build, package, sign, upload, or share any source.

## Decision

The only positive copy-validation decision allowed here is:

```text
owner_controlled_copy_validation_dry_run_created = true
```

This does not approve tester delivery.

## Next step policy

Allowed next milestones:

- STOP
- v0.6.10-controlled-tester-package-staging-readiness-dry-run-no-copy-no-build-no-distribution

Blocked next actions:

- direct tester activation
- public UI link
- public release
- package distribution
- OneDrive share delivery
- GitHub release publication
- paid distribution
- runtime file copy
- package content copy
- copy execution
- staging tree creation
- package source approval
- source allowlist approval
- source allowlist enforcement
- ZIP/EXE/MSI/installer creation
- release archive creation
- actual package build
- code signing
- checksum publication
- attempt/session/progress persistence
- live scoring persistence
- cloud/API requirement
