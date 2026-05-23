# Voila! Language Pack Release Candidate Build Checklist

Milestone: v0.3.0-public-beta-language-pack-release-candidate-build-plan
Status: build checklist
Scope: documentation only; no ZIP build, no Git tag, no GitHub release upload, no public ZIP publish

## Build outputs planned

- [x] proposed ZIP name
- [x] proposed SHA256 name
- [x] proposed release notes asset name
- [x] proposed final checklist asset name
- [x] proposed test log asset name

## Safe build order documented

- [x] sync main
- [x] confirm clean working tree
- [x] confirm no open PRs
- [x] run validations
- [x] run smokes
- [x] run Python compile
- [x] confirm XSS fix
- [x] create clean staging directory
- [x] copy approved files only
- [x] exclude forbidden files
- [x] create ZIP
- [x] inspect ZIP
- [x] generate SHA256
- [x] write test log
- [x] write final checklist
- [x] defer upload

## Staging documented

- [x] staging directory pattern documented
- [x] candidate staging contents documented
- [x] required exclusions documented
- [x] ZIP inspection documented

## Future artifacts documented

- [x] test log contents
- [x] final checklist contents
- [x] checksum generation rule

## Publishing guard

- [x] no ZIP built in this milestone
- [x] no SHA256 generated in this milestone
- [x] no Git tag created in this milestone
- [x] no GitHub release uploaded in this milestone
- [x] no public ZIP published in this milestone
- [x] no release notes asset uploaded in this milestone
- [x] no checksum asset uploaded in this milestone
- [x] no LICENSE change in this milestone

## Decision

This milestone is build planning only.

Actual build and publishing remain deferred.
