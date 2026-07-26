# v0.8.92a — Portable runtime Python cache cleanup fix

## Scope

This milestone fixes the portable Windows runtime builder so that generated
Python cache content is removed before the runtime ZIP is created.

The diagnosed v0.8.92 build contained:

- 945 __pycache__ / .pyc entries;
- all 945 entries under pp/python/Lib/site-packages;
- zero application cache entries outside the embedded dependency runtime;
- zero .pyo entries;
- zero other forbidden package entries.

## Root cause

The builder performed final cleanup for .tessdata, udit,
.release-cache, and generated data directories, but it did not remove
Python cache directories or bytecode generated while validating standalone
runtime imports.

## Fix

Immediately before the data reset and before Compress-Archive, the builder:

1. finds and removes every __pycache__ directory under $AppDir;
2. removes any remaining .pyc or .pyo file under $AppDir;
3. re-scans the staging tree;
4. fails the build if any Python cache or bytecode remains.

## Validation policy

The fix is source-only in this step.

- no build is executed;
- no existing ZIP is modified;
- no new ZIP is created;
- no extracted validation is executed;
- no tester share is performed;
- no delivery or distribution is performed.

The existing v0.8.92 ZIP remains a blocked diagnostic artifact and must not
be adopted or delivered. A fresh runtime must be rebuilt after this fix is
validated and merged through the controlled workflow.
