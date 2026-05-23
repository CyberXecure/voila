# Voila! Language Pack Release Candidate Runbook

Milestone: v0.3.0-public-beta-language-pack-release-candidate-checklist
Status: runbook
Scope: documentation only; no release publishing

## Purpose

This runbook explains the safe execution order for a future language-pack release candidate.

## Safe RC order

1. Complete the release-candidate checklist.
2. Create a package-plan milestone.
3. Create a release-notes milestone.
4. Create a build milestone.
5. Build the ZIP in the build milestone only.
6. Generate SHA256 after the ZIP is final.
7. Verify the ZIP contents.
8. Verify the checksum.
9. Confirm CodeQL/security checks.
10. Only then create a publish milestone.

## What this runbook does not authorize

This runbook does not authorize:

```text
Git tag
GitHub release upload
public ZIP publish
release notes asset upload
checksum asset upload
LICENSE addition or change
```

## Recommended next milestones

Recommended next path:

```text
v0.3.0-public-beta-language-pack-release-candidate-package-plan
v0.3.0-public-beta-language-pack-release-candidate-notes
v0.3.0-public-beta-language-pack-release-candidate-build-plan
```

Publishing should remain deferred until an explicit publish milestone.
