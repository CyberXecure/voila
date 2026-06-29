# v0.6.6 Controlled Tester Package Source Validation Dry-Run — No Build, No Distribution

Status: implementation milestone
Scope: owner-controlled source validation dry-run only
Build: explicitly blocked
Distribution: explicitly blocked

## Purpose

This milestone validates the candidate source paths recorded in v0.6.5 without copying runtime files, approving package sources, building, zipping, creating an installer, staging a release archive, or distributing anything.

It is a validation/report step only.

This milestone does not create a runnable package and does not approve any source for packaging now.

## Inputs

- v0.6.5 controlled tester package source selection dry-run no-build no-distribution must exist on main.
- v0.6.4 controlled tester package build plan no-build no-distribution must exist on main.
- v0.6.3 controlled tester package contents manifest no-build no-distribution must exist on main.
- v0.6.2 controlled tester package staging local-only no-distribution must exist on main.
- v0.6.1 controlled tester package dry-run no-distribution must exist on main.
- v0.6.0 controlled tester candidate decision must exist on main.
- Hidden owner Exam Prep preview remains owner-only and local-only.

## Allowed in this milestone

- Add this source-validation dry-run policy document.
- Add a local validation script.
- Create or refresh a local-only source-validation evidence directory outside the git repository.
- Write a local-only source-validation JSON and README into that evidence directory.
- Validate that candidate source paths exist or are absent.
- Validate that every candidate remains `approved_for_package_now = false`.
- Confirm that no runtime files were copied and no actual build or distribution happened.

## Explicitly blocked in this milestone

- No runtime file copy.
- No package build.
- No package source approval.
- No source allowlist approval.
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

## Local source-validation evidence

The local source-validation evidence directory is intentionally outside the repository:

```text
D:\dev\release-assets\voila\v0.6.6-controlled-tester-package-source-validation-dry-run-no-build-no-distribution
```

Expected files:

```text
SOURCE-VALIDATION-README.txt
SOURCE-VALIDATION-DRY-RUN.json
```

These files are local evidence only and must not be uploaded, shared, packaged, or committed unless a later milestone explicitly requests a sanitized artifact.

## Candidate validation policy

The source-validation dry-run may inspect these candidate paths only:

- `services`
- `services/api`
- `scripts/dev`
- `docs`
- `LICENSE.txt`
- `scripts/dev/check-controlled-tester-package-build-plan-no-build-no-distribution.ps1`

This milestone records path existence and type only. It does not approve, copy, build, package, sign, upload, or share any candidate source.

## Decision

The only positive source-validation decision allowed here is:

```text
owner_controlled_source_validation_dry_run_created = true
```

This does not approve tester delivery.

## Next step policy

Allowed next milestones:

- STOP
- v0.6.7-controlled-tester-package-source-allowlist-plan-no-build-no-distribution

Blocked next actions:

- direct tester activation
- public UI link
- public release
- package distribution
- OneDrive share delivery
- GitHub release publication
- paid distribution
- runtime file copy
- package source approval
- source allowlist approval
- ZIP/EXE/MSI/installer creation
- release archive creation
- actual package build
- code signing
- checksum publication
- attempt/session/progress persistence
- live scoring persistence
- cloud/API requirement
