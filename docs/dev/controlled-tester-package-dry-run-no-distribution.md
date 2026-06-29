# v0.6.1 Controlled Tester Package Dry-Run — No Distribution

Status: implementation milestone
Scope: owner-controlled package dry-run report only
Distribution: explicitly blocked
Package creation: explicitly blocked

## Purpose

This milestone records whether Voila can proceed from the v0.6.0 controlled tester candidate decision into a later local-only package staging milestone.

It does not create a tester package, does not stage release assets, does not upload anything, and does not make the hidden owner preview public.

## Inputs

- v0.6.0 controlled tester candidate decision must pass.
- Existing owner preview checks must continue to pass.
- Hidden owner Exam Prep preview remains owner-only and local-only.
- The validated preview source remains local bank with legacy fallback rollback evidence.

## Allowed in this milestone

- Add this decision document.
- Add a local validation script.
- Emit a dry-run JSON decision to the console.
- Confirm that package creation and distribution remain blocked.

## Explicitly blocked in this milestone

- No ZIP, EXE, MSI, installer, or tester package creation.
- No release asset staging directory.
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

## Dry-run decision

The only positive decision allowed here is:

```text
owner_controlled_package_dry_run_pass = true
```

This means the next milestone may separately prepare local-only package staging, still with no distribution.

It does not mean that tester delivery is approved.

## Next step policy

Allowed next milestones:

- STOP
- v0.6.2-controlled-tester-package-staging-local-only-no-distribution

Blocked next actions:

- direct tester activation
- public UI link
- public release
- package distribution
- OneDrive share delivery
- GitHub release publication
- paid distribution
- attempt/session/progress persistence
- live scoring persistence
- cloud/API requirement
```
