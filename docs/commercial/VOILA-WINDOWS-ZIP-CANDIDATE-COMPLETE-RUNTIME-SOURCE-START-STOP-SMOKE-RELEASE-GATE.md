# Voila Windows ZIP Candidate Complete Runtime Source START/STOP Smoke Release Gate

Milestone:

```text
v0.3.56-voila-windows-zip-candidate-complete-runtime-source-start-stop-smoke-plan
```

## Gate before smoke execution

Required:

```text
[ ] ZIP build result PASS
[ ] SHA256 verified
[ ] extracted package root exists
[ ] START/STOP smoke plan accepted
[ ] safety notes accepted
[ ] no external tester sharing before smoke result
```

## Gate after smoke execution

If PASS:

```text
[ ] consider tester-readiness review
[ ] review README/release notes
[ ] confirm known limitations
[ ] decide whether to publish or keep local-only
```

If CONDITIONAL:

```text
[ ] identify blocker
[ ] create next focused milestone
[ ] do not claim full tester readiness
```

If FAIL:

```text
[ ] stop release progression
[ ] fix launcher/runtime issue
[ ] rerun smoke before any sharing
```

## Commercial boundary

START/STOP smoke does not imply commercial readiness, paid distribution approval, final legal approval, or public release approval.
