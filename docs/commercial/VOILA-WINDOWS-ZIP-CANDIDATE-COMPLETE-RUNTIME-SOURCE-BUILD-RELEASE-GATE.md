# Voila Windows ZIP Candidate Complete Runtime Source Build Release Gate

Milestone:

```text
v0.3.54-voila-windows-zip-candidate-complete-runtime-source-build-plan
```

## Gate before executing the build

Required:

```text
[ ] helper smoke PASS recorded
[ ] build plan accepted
[ ] version selected
[ ] output root selected
[ ] package-local .venv strategy accepted
[ ] LanguageTool/OCR deferral or bundling decision accepted
[ ] no external publication planned for this milestone
```

## Gate after successful ZIP build

Required before any external tester sharing:

```text
[ ] ZIP/SHA256 build PASS
[ ] extract validation PASS
[ ] complete runtime files verified in extracted ZIP
[ ] START/STOP smoke performed in a later milestone
[ ] README reviewed
[ ] release notes reviewed
[ ] legal folder verified
[ ] known limitations documented
```

## Commercial boundary

A complete runtime source ZIP candidate does not imply:

```text
commercial readiness
paid distribution approval
final legal approval
public release approval
```

Before paid distribution:

```text
[ ] EULA reviewed for paid use
[ ] third-party notices complete enough for distribution
[ ] payment/refund terms ready
[ ] license/activation plan decided
[ ] support obligations reviewed
```
