# Voila! Language Pack Release Candidate Publish Plan

Milestone: v0.3.0-public-beta-language-pack-release-candidate-publish-plan
Status: publish planning
Scope: documentation only; no Git tag, no GitHub release upload, no public ZIP publish, no UI code changes, no language-pack JSON changes, no runtime changes, no schema changes, no LICENSE change

## Purpose

This milestone plans the safe publication of the local Voila! v0.3.0 language-pack release candidate assets.

This milestone does not publish anything.

## Local RC assets

The local build milestone produced these assets under D:\dev\releases:

`	ext
voila-v0.3.0-public-beta-language-pack-rc1.zip
voila-v0.3.0-public-beta-language-pack-rc1.sha256
voila-v0.3.0-public-beta-language-pack-rc1-release-notes.md
voila-v0.3.0-public-beta-language-pack-rc1-final-checklist.md
voila-v0.3.0-public-beta-language-pack-rc1-test-log.md
`

## Verified ZIP checksum

`	ext
BFD42055C8354D1C8DEE4CC3E8F0E1F8105DB4708EF514D76D15E1B09F17B618
`

## Proposed Git tag

`	ext
v0.3.0-public-beta-language-pack-rc1
`

The tag must not be created in this planning milestone.

## Proposed GitHub release title

`	ext
Voila! v0.3.0 Public Beta — Language Pack RC1
`

## Proposed release type

`	ext
GitHub prerelease
`

## Proposed upload assets

Future publish milestone should upload exactly:

`	ext
D:\dev\releases\voila-v0.3.0-public-beta-language-pack-rc1.zip
D:\dev\releases\voila-v0.3.0-public-beta-language-pack-rc1.sha256
D:\dev\releases\voila-v0.3.0-public-beta-language-pack-rc1-release-notes.md
D:\dev\releases\voila-v0.3.0-public-beta-language-pack-rc1-final-checklist.md
D:\dev\releases\voila-v0.3.0-public-beta-language-pack-rc1-test-log.md
`

## Required final checks before publishing

Before a future publish milestone creates a tag or GitHub release, confirm:

`	ext
main is synced
working tree is clean
no open PRs
all validation commands pass
all smoke commands pass
Python compile passes
CodeQL/security checks pass
local RC ZIP exists
SHA256 matches expected value
release notes exist
final checklist exists
test log exists
v0.2.81 _html_escape(str(page)) fix is present
no LICENSE change was introduced
existing v0.2.0 public beta release remains unchanged
`

## Proposed future publish commands

These commands are for a future publish milestone only.

`powershell
cd D:\dev\projects\voila

git switch main
git pull --ff-only

git tag -a v0.3.0-public-beta-language-pack-rc1 -m "Voila v0.3.0 public beta language pack RC1"
git push origin v0.3.0-public-beta-language-pack-rc1

gh release create v0.3.0-public-beta-language-pack-rc1 
  "D:\dev\releases\voila-v0.3.0-public-beta-language-pack-rc1.zip" 
  "D:\dev\releases\voila-v0.3.0-public-beta-language-pack-rc1.sha256" 
  "D:\dev\releases\voila-v0.3.0-public-beta-language-pack-rc1-release-notes.md" 
  "D:\dev\releases\voila-v0.3.0-public-beta-language-pack-rc1-final-checklist.md" 
  "D:\dev\releases\voila-v0.3.0-public-beta-language-pack-rc1-test-log.md" 
  --title "Voila! v0.3.0 Public Beta — Language Pack RC1" 
  --notes-file "D:\dev\releases\voila-v0.3.0-public-beta-language-pack-rc1-release-notes.md" 
  --prerelease
`

## Stop conditions

Do not publish if:

`	ext
checksum differs
GitHub CLI authentication is unavailable
open PRs exist
local build assets are missing
release notes are incomplete
CodeQL/security checks fail
LICENSE/commercial-positioning decision is unclear
a v0.3.0 tag already exists unexpectedly
`

## Publishing remains deferred

This milestone must not:

`	ext
create Git tag
push Git tag
create GitHub release
upload assets
publish ZIP
change LICENSE
`

## Decision

This milestone defines the publish plan only.

Actual publishing remains deferred to a separate explicit publish milestone.
