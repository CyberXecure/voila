# v0.8.92c — Portable runtime strict content exclusion

## Status

Owner-local repair milestone.

No build, ZIP creation, extraction, sharing, delivery, distribution, or public
release is performed by this milestone.

## Root cause

The v0.8.92b runtime ZIP contained no Python cache files, but its static
confidentiality audit detected 208 personal absolute-path occurrences across
139 tracked project files.

The refined audit established:

- zero occurrences in runtime-critical files;
- 109 affected development and tooling files;
- 30 affected packaged documentation files;
- zero files requiring runtime preservation or targeted sanitization.

All 30 reviewed documentation files had zero runtime references and are
excluded from the portable runtime.

## Repair

The initial repository-to-runtime robocopy operation excludes:

- repository metadata;
- project documentation;
- development and release scripts;
- test and fixture directories;
- `.gitignore` and `.gitattributes`.

The complete `scripts` directory is not broadly excluded. Runtime shortcut
helpers under `scripts/runtime` remain available to the builder and are copied
explicitly to the application root.

## Preserved runtime

The repair does not change:

- application services;
- language packs;
- embedded Python;
- Tesseract;
- Java;
- LanguageTool;
- runtime launchers;
- Python cache cleanup introduced by v0.8.92a.

## Next gate

After merge to protected `main`, a completely fresh rebuild must prove:

- zero `__pycache__`, `.pyc`, and `.pyo`;
- zero personal absolute-path occurrences;
- all required runtime components remain present;
- extracted startup and API smoke pass.

The existing v0.8.92 and v0.8.92b ZIP files remain immutable diagnostic
artifacts and must not be edited or adopted as the final tester package.
