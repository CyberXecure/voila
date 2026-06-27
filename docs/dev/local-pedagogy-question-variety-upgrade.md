# Local pedagogy question variety upgrade — v0.4.55

Status: local-only question variety upgrade.

## Purpose

v0.4.55 upgrades the deterministic local pedagogy engine so it generates more than simple concept-recognition questions.

This directly follows v0.4.54, where the quality gate correctly detected the previous scaffold questions as repetitive/simple.

## Updated module

```text
services/api/local_pedagogy_engine.py
```

The engine now generates varied question types:

```text
multiple_choice
short_answer
evidence_based
compare_concepts
apply_concept
formula_interpretation
apply_formula
```

## Quality effect

Before v0.4.55:

```text
quality_status = needs_improvement
```

After v0.4.55:

```text
quality_status = pass
quality_gate_pass = true
```

For the local diagnostic sample, this means the quality gate sees real progress.

## Safety constraints

v0.4.55 still does not:

```text
save attempts
update progress
score answers
modify Exam Prep UI
modify weak review
replace live study sessions
replace the legacy generator
enable live consumption
require cloud/API
accept user-provided filesystem roots in web routes
```

## Added check

```text
scripts/dev/check-local-pedagogy-question-variety.ps1
```

The check verifies:

1. local pedagogy outputs are generated
2. `exercise_bank.local.json` contains varied question types
3. the first concept skill has multiple question types
4. formula interpretation questions are present
5. legacy fallback remains declared
6. no cloud/API dependency appears

## Updated check

```text
scripts/dev/check-local-bank-question-quality-gate.ps1
```

The quality gate check now expects the upgraded local sample to pass.

## Recommended next milestone

v0.4.56 — Local-bank dry-run answer evaluation scaffold.

Suggested scope:

- evaluate dry-run answers locally
- do not persist attempts
- do not update progress
- keep live consumption disabled
- keep legacy fallback

