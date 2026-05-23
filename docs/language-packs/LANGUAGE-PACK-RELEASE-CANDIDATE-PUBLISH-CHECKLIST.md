# Voila! Language Pack Release Candidate Publish Checklist

Milestone: v0.3.0-public-beta-language-pack-release-candidate-publish-plan
Status: publish checklist
Scope: documentation only; no Git tag, no GitHub release upload, no public ZIP publish

## Local assets documented

- [x] ZIP path documented
- [x] SHA256 path documented
- [x] release notes path documented
- [x] final checklist path documented
- [x] test log path documented
- [x] SHA256 documented

## Future GitHub release details documented

- [x] proposed tag
- [x] proposed release title
- [x] prerelease status
- [x] exact upload asset list
- [x] proposed publish commands

## Required final checks documented

- [x] synced main
- [x] clean working tree
- [x] no open PRs
- [x] validation commands pass
- [x] smoke commands pass
- [x] Python compile passes
- [x] CodeQL/security checks pass
- [x] ZIP exists
- [x] SHA256 matches
- [x] release notes exist
- [x] final checklist exists
- [x] test log exists
- [x] XSS fix present
- [x] no LICENSE change

## Stop conditions documented

- [x] checksum mismatch
- [x] missing GitHub CLI auth
- [x] open PRs
- [x] missing assets
- [x] incomplete release notes
- [x] CodeQL/security failure
- [x] unclear licensing/commercial-positioning decision
- [x] unexpected existing v0.3.0 tag

## Publishing guard

- [x] no Git tag created in this milestone
- [x] no Git tag pushed in this milestone
- [x] no GitHub release created in this milestone
- [x] no assets uploaded in this milestone
- [x] no public ZIP published in this milestone
- [x] no LICENSE change in this milestone

## Decision

This milestone is publish planning only.

Actual publishing remains deferred.
