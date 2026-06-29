# v0.6.11 Controlled Tester Package Staging Layout Plan — No Create, No Copy, No Build, No Distribution

Status: implementation milestone
Scope: owner-controlled staging layout plan only
Staging layout creation: explicitly blocked
Staging tree creation: explicitly blocked
Copy: explicitly blocked
Build: explicitly blocked
Distribution: explicitly blocked

## Purpose

This milestone records a staging layout plan for a future controlled tester package without creating a staging layout, creating a staging tree, copying runtime files, approving source copies, building, zipping, creating an installer, staging a release archive, or distributing anything.

It follows the v0.6.10 staging readiness dry-run and converts readiness items into a planned layout map only.

This milestone does not create a runnable package and does not copy any package content now.

## Inputs

- v0.6.10 controlled tester package staging readiness dry-run no-copy no-build no-distribution must exist on main.
- v0.6.9 controlled tester package copy validation dry-run no-copy no-build no-distribution must exist on main.
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

- Add this staging-layout plan policy document.
- Add a local validation script.
- Create or refresh a local-only staging-layout plan evidence directory outside the git repository.
- Write a local-only staging-layout plan JSON and README into that evidence directory.
- Plan future staging layout directories and source-to-layout mapping strings.
- Confirm that every planned layout item remains `layout_created_now = false`.
- Confirm that no staging layout, staging tree, runtime file copy, build, or distribution happened.

## Explicitly blocked in this milestone

- No staging layout creation.
- No staging tree creation.
- No staging root creation for package contents.
- No runtime file copy.
- No package content copy.
- No copy execution.
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

## Local staging-layout plan evidence

The local staging-layout plan evidence directory is intentionally outside the repository:

```text
D:\dev\release-assets\voila\v0.6.11-controlled-tester-package-staging-layout-plan-no-create-no-copy-no-build-no-distribution
```

Expected files:

```text
STAGING-LAYOUT-PLAN-README.txt
STAGING-LAYOUT-PLAN-DRY-RUN.json
```

These files are local evidence only and must not be uploaded, shared, packaged, or committed unless a later milestone explicitly requests a sanitized artifact.

## Staging layout plan policy

The staging-layout plan may define future layout names only:

- `app/`
- `runtime/`
- `scripts/`
- `docs/`
- `legal/`
- `validation/`

Every planned layout entry must remain:

```text
planned_only = true
layout_created_now = false
staging_tree_created = false
copy_allowed_now = false
copy_executed_now = false
copied_now = false
approved_for_package_now = false
```

This milestone records staging layout intent only. It does not approve, enforce, copy, stage, build, package, sign, upload, or share any source.

## Decision

The only positive staging-layout plan decision allowed here is:

```text
owner_controlled_staging_layout_plan_created = true
```

This does not approve tester delivery.

## Next step policy

Allowed next milestones:

- STOP
- v0.6.12-controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution

Blocked next actions:

- direct tester activation
- public UI link
- public release
- package distribution
- OneDrive share delivery
- GitHub release publication
- paid distribution
- staging layout creation
- staging tree creation
- staging root creation
- runtime file copy
- package content copy
- copy execution
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
