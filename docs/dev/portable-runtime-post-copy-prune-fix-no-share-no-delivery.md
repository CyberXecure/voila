# v0.8.92e — Portable runtime post-copy staging prune

## Status

Owner-local source repair milestone.

No build, ZIP creation, extraction, runtime startup, sharing, delivery,
distribution, or public release is performed by this milestone.

## Evidence

The fresh v0.8.92d build completed and produced a diagnostic runtime ZIP.
Python cache cleanup passed, but the direct ZIP-index audit found 552 forbidden
entries.

Diagnostic categories:

- DEVELOPMENT_SCRIPTS: 537
- RELEASE_TOOLING: 15

Root-cause classification:

- DIRECTORY_EXCLUSIONS_NOT_EFFECTIVE

## Root cause

The initial robocopy /XD and /XF arguments did not provide a sufficient
fail-closed guarantee that all repository, development, documentation, PDF,
and draft content was absent from portable staging.

## Repair

Immediately after the initial project copy, the builder now explicitly removes
forbidden content from $AppDir.

The prune removes:

- .github, .git, and .venv;
- docs;
- scripts/dev and scripts/release;
- test, testdata, fixture, and fixtures directories;
- .gitattributes and .gitignore;
- PDF files;
- files matching the preserved v0.8.90 draft name.

A fail-closed verification stops the build if forbidden content remains.

The prune occurs before embedded Python and external runtimes are assembled.
The existing Python-cache cleanup remains before ZIP creation.

## Preserved runtime

The repair preserves:

- scripts/runtime;
- runtime launchers;
- application services;
- language packs;
- embedded Python;
- Tesseract;
- Java;
- LanguageTool.

## Immutable diagnostic evidence

The following artifacts remain unchanged and unadopted:

- the original blocked v0.8.92 ZIP;
- the path-leaking v0.8.92b ZIP;
- the v0.8.92d diagnostic ZIP containing 552 forbidden entries;
- the v0.8.92d diagnostic map;
- the three local v0.8.90 drafts.

## Next gate

After protected-main merge, a separate fresh rebuild must prove:

- zero Python-cache entries;
- zero forbidden-content entries;
- zero personal absolute-path occurrences;
- all required runtime components present.

No existing diagnostic ZIP may be adopted.
