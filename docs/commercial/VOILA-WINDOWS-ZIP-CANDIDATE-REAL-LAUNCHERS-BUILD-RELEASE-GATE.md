# Voila Windows ZIP Candidate Real Launchers Build Release Gate

Milestone:

```text
v0.3.43-voila-windows-zip-candidate-real-launchers-build-plan
```

## Gate before local rebuild

Required:

```text
[ ] real launchers helper exists
[ ] real launchers helper smoke PASS
[ ] real launchers staging DryRun PASS
[ ] build helper exists
[ ] legal helper exists
[ ] validation helper exists
[ ] runtime source selected
[ ] output root selected
```

## Gate before START/STOP smoke

Required after rebuild:

```text
[ ] ZIP candidate created
[ ] SHA256 generated
[ ] extract validation passed
[ ] real launchers present in extracted ZIP
[ ] README reviewed
[ ] release notes reviewed
[ ] legal folder verified
```

## Gate before external sharing

Required later:

```text
[ ] START/STOP smoke PASS or clearly documented CONDITIONAL
[ ] known limitations documented
[ ] feedback/support path defined
[ ] public wording reviewed
[ ] no final/commercial claims overstated
```

## Commercial boundary

A rebuilt ZIP with real launchers is still not automatically commercial-ready.

Before paid distribution:

```text
[ ] paid terms ready
[ ] EULA reviewed for paid use
[ ] third-party notices complete enough for distribution
[ ] payment/refund wording reviewed
[ ] license/activation plan decided
```
