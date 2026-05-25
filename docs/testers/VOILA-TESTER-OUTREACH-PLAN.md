# Voila! Tester Outreach Plan

## Milestone

v0.3.1-public-beta-tester-outreach

## Purpose

Prepare a small, controlled outreach round for the local Windows tester package.

This is not a public release.

The goal is to send the validated Windows tester ZIP manually to 2-3 trusted testers and collect practical feedback before deciding whether to publish a GitHub prerelease.

## Current local tester package

Local ZIP:

voila-v0.3.1-public-beta-windows-tester-package.zip

SHA256:

CB7F5C7C9FB35DBFB5AE40371365253463B6BC78FDC7C0D97F59BD8E58D84427

Validated behavior:

- .venv included
- .release-cache excluded
- data folder is clean
- no old PDFs included
- START-VOILA.bat starts in background
- STOP-VOILA.bat stops in background
- DEBUG launchers included
- Voila responds on http://127.0.0.1:8787 with 200 OK
- STOP releases ports 8081 and 8787

## Recommended first testers

Start with 2-3 trusted testers only.

Best tester profiles:

- someone comfortable downloading and extracting a ZIP
- someone who works with PDFs
- someone who has training, manuals, procedures or course materials
- someone who will give honest feedback
- someone who will not upload sensitive documents

Avoid for first outreach:

- public posting with broad download link
- cold outreach to strangers
- enterprise/compliance users
- users with only sensitive documents
- non-Windows users

## What testers should receive

Each tester should receive:

- the ZIP package
- the SHA256 checksum
- short instructions
- limitations note
- feedback questions
- warning not to use sensitive documents

## Distribution options

Recommended:

- private Google Drive link
- OneDrive link
- direct file transfer
- private GitHub release draft asset only if needed

Not recommended yet:

- public GitHub release
- public LinkedIn download link
- public Reddit download link
- paid supporter package
- installer distribution

## Test duration

Recommended first round:

- 3 to 7 days
- maximum 2-3 testers
- collect feedback before changing code
- do not add features during feedback round

## Success criteria

The outreach is successful if testers can answer:

- Did download and extraction work?
- Did START-VOILA.bat work?
- Did the browser open?
- Did Voila respond locally?
- Could they test with a small PDF?
- Was the product idea clear?
- Which use case felt strongest?
- Which output was most useful?
- What blocked them?
- Would they test again?
- Would a supporter package make sense?

## Scope

Included:

- outreach plan
- tester message
- feedback tracker template
- tester handoff checklist

Excluded:

- no code changes
- no ZIP rebuild
- no GitHub release upload
- no Git tag
- no LICENSE
- no payment flow
- no installer
- no new language packs
