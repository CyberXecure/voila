# Voila! Language Pack Release Readiness Runbook

Milestone: v0.2.98-public-beta-language-pack-release-readiness-checklist
Status: runbook
Scope: documentation only; no release publishing

## Use this runbook when preparing a future language-pack release

1. Sync `main`.
2. Confirm the working tree is clean.
3. Confirm there are no open PRs.
4. Run the required validation commands from `LANGUAGE-PACK-RELEASE-READINESS-CHECKLIST.md`.
5. Confirm the v0.2.81 `_html_escape(str(page))` fix remains present.
6. Confirm release notes, ZIP name, checksum name, and GitHub asset names are final.
7. Confirm no LICENSE/commercial-positioning decision has changed.
8. Only then create a dedicated release milestone.

## Important

This runbook does not authorize a release by itself.

A future release milestone must explicitly authorize:

```text
Git tag
GitHub release upload
public ZIP publish
release notes asset
checksum asset
```

## Recommended next milestone

Recommended next milestone after this checklist:

```text
v0.2.99-public-beta-language-pack-release-readiness-docs
```

or, if publishing is explicitly approved:

```text
v0.3.0-public-beta-language-pack-release-candidate-plan
```
