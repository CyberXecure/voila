# v0.6.2 Controlled Tester Package Staging Local-Only — No Distribution

Status: implementation milestone
Scope: owner-controlled local staging only
Distribution: explicitly blocked
Package creation: explicitly blocked

## Purpose

This milestone allows Voila to prepare and validate a local-only controlled tester staging area for a future package milestone.

It does not create a ZIP, EXE, MSI, installer, public release, external share, or distributed tester package.

The staging area is local evidence only. It may contain a dry-run manifest and a README that record the safety gates, but it must not contain a runnable package or release archive.

## Inputs

- v0.6.1 controlled tester package dry-run no-distribution must pass.
- v0.6.0 controlled tester candidate decision must pass through the v0.6.1 check chain.
- Existing hidden owner preview checks must continue to pass.
- Hidden owner Exam Prep preview remains owner-only and local-only.

## Allowed in this milestone

- Add this staging policy document.
- Add a local validation script.
- Create or refresh a local-only staging evidence directory outside the git repository.
- Write a local-only dry-run manifest and README into that evidence directory.
- Confirm that package creation and distribution remain blocked.

## Explicitly blocked in this milestone

- No ZIP creation.
- No EXE creation.
- No MSI creation.
- No installer creation.
- No runnable tester package creation.
- No release archive creation.
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

## Local staging evidence

The local staging evidence directory is intentionally outside the repository:

```text
D:\dev\release-assets\voila\v0.6.2-controlled-tester-staging-local-only
```

Expected files:

```text
STAGING-LOCAL-ONLY-README.txt
STAGING-DRY-RUN-MANIFEST.json
```

These files are local evidence only and must not be uploaded, shared, packaged, or committed unless a later milestone explicitly requests a sanitized artifact.

## Decision

The only positive staging decision allowed here is:

```text
owner_controlled_local_staging_evidence_created = true
```

This does not approve tester delivery.

## Next step policy

Allowed next milestones:

- STOP
- v0.6.3-controlled-tester-package-contents-manifest-no-build-no-distribution

Blocked next actions:

- direct tester activation
- public UI link
- public release
- package distribution
- OneDrive share delivery
- GitHub release publication
- paid distribution
- ZIP/EXE/MSI/installer creation
- attempt/session/progress persistence
- live scoring persistence
- cloud/API requirement
