# v0.6.4 Controlled Tester Package Build Plan — No Build, No Distribution

Status: implementation milestone
Scope: owner-controlled build plan only
Build: explicitly blocked
Distribution: explicitly blocked

## Purpose

This milestone records a controlled tester package build plan without building, copying runtime files, zipping, creating an installer, staging a release archive, or distributing anything.

It follows the v0.6.3 contents manifest and converts the contents categories into a build-plan decision step.

This milestone does not create a runnable package.

## Inputs

- v0.6.3 controlled tester package contents manifest no-build no-distribution must exist on main.
- v0.6.2 controlled tester package staging local-only no-distribution must exist on main.
- v0.6.1 controlled tester package dry-run no-distribution must exist on main.
- v0.6.0 controlled tester candidate decision must exist on main.
- Hidden owner Exam Prep preview remains owner-only and local-only.

## Allowed in this milestone

- Add this build-plan policy document.
- Add a local validation script.
- Create or refresh a local-only build-plan evidence directory outside the git repository.
- Write a local-only build-plan JSON and README into that evidence directory.
- Record planned build phases for a future build milestone.
- Confirm that no actual build, file copy, release archive, or distribution happened.

## Explicitly blocked in this milestone

- No runtime file copy.
- No package build.
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

## Local build-plan evidence

The local build-plan evidence directory is intentionally outside the repository:

```text
D:\dev\release-assets\voila\v0.6.4-controlled-tester-package-build-plan-no-build-no-distribution
```

Expected files:

```text
BUILD-PLAN-README.txt
BUILD-PLAN-DRY-RUN.json
```

These files are local evidence only and must not be uploaded, shared, packaged, or committed unless a later milestone explicitly requests a sanitized artifact.

## Planned future build phases

The future build may be planned around these phases only:

- source/runtime selection review
- package staging root preparation
- launcher and documentation inclusion review
- legal/license inclusion review
- local validation report generation
- archive/checksum creation only if approved by a later milestone

This milestone does not approve any of those actions.

## Decision

The only positive build-plan decision allowed here is:

```text
owner_controlled_build_plan_created = true
```

This does not approve tester delivery.

## Next step policy

Allowed next milestones:

- STOP
- v0.6.5-controlled-tester-package-source-selection-dry-run-no-build-no-distribution

Blocked next actions:

- direct tester activation
- public UI link
- public release
- package distribution
- OneDrive share delivery
- GitHub release publication
- paid distribution
- runtime file copy
- ZIP/EXE/MSI/installer creation
- release archive creation
- actual package build
- code signing
- checksum publication
- attempt/session/progress persistence
- live scoring persistence
- cloud/API requirement
