# v0.8.91 — UI language consistency, silent runtime bootstrap and canonical Review Document flow

## Status

PASS — owner-local implementation and validation completed.

Policy preserved: no build, no ZIP, no tester delivery, no sharing, no distribution and no public release.

## Baseline

- Parent HEAD: `79741947d75edd77e2057789717162b591aeb477`
- Branch: `fix/v0.8.91-ui-language-consistency-and-silent-runtime-bootstrap-no-share-no-delivery`
- Tester UI languages: Romanian and English

## Scope completed

- Consistent RO/EN tester UI with resolved `<html lang>`.
- Canonical Review Document stages: Text and OCR; Formulas and page regions; Concepts to learn.
- The former Crop Editor tester route redirects to Review Document and does not start port 8790.
- Visual page regions are treated as Visual Learning Evidence.
- Semantic fields: visual type, title, meaning, importance, Study uses and linked concepts.
- Accept/edit require semantic completeness; ignore remains valid without metadata.
- Only complete, accepted/edited and eligible visual evidence enters the Prepared Lesson.
- OCR and web subprocesses use Windows `CREATE_NO_WINDOW`.
- Portable runtime startup changes only `-WindowStyle Minimized` to `-WindowStyle Hidden`.

## Validation

The corrected combined final audit confirmed:

```text
FAILURE_COUNT=0
V0_8_91_CORRECTED_COMBINED_FINAL_AUDIT_NO_BUILD=PASS
V0_8_91_COMBINED_FINAL_AUDIT=PASS
COMMIT_ALLOWED=TRUE
BUILD_ALLOWED=FALSE
```

## Preserved and excluded work

The three v0.8.90 package-rebuild-preflight drafts remain untracked and are excluded from this commit.

A build, ZIP, share, delivery or distribution requires a separate explicit milestone.
