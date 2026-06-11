# Voila Windows ZIP Candidate Real Launchers START/STOP Smoke Release Gate

Milestone:

```text
v0.3.45-voila-windows-zip-candidate-real-launchers-start-stop-smoke-plan
```

## Gate before running smoke

Required:

```text
[ ] v0.3.44 ZIP candidate build PASS
[ ] SHA256 available
[ ] extract validation PASS
[ ] real launchers present in extracted ZIP
[ ] local machine ready for service smoke
[ ] ports checked
```

## Gate after smoke PASS

Required before external sharing:

```text
[ ] START/STOP smoke result documented
[ ] service response documented
[ ] process cleanup documented
[ ] port cleanup documented
[ ] logs reviewed
[ ] README reviewed
[ ] release notes reviewed
[ ] legal folder verified
[ ] known limitations documented
```

## Gate before GitHub Release

Required later:

```text
[ ] release notes finalized
[ ] SHA256 asset prepared
[ ] ZIP asset selected
[ ] public wording reviewed
[ ] support/feedback path defined
[ ] legal/commercial claims reviewed
```

## Commercial boundary

START/STOP smoke PASS does not automatically make Voila commercially ready.

Before paid distribution:

```text
[ ] paid terms ready
[ ] EULA reviewed for paid use
[ ] third-party notices complete enough for distribution
[ ] payment/refund wording reviewed
[ ] license/activation plan decided
```
