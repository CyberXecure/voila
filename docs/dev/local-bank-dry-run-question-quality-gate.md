# Local bank dry-run question quality gate — v0.4.54

Status: dry-run quality gate.

## Purpose

This milestone adds a quality gate before any future live use of local-bank Exam Prep questions.

The current local pedagogy scaffold generates simple concept-recognition questions. v0.4.54 detects this and marks the local bank as `needs_improvement`.

## Added module

```text
services/api/exam_prep_local_bank_question_quality_gate.py
```

## Added check

```text
scripts/dev/check-local-bank-question-quality-gate.ps1
```

## Gate signals

The gate checks:

```text
question count
question type diversity
repetitive prefix usage
simple concept-recognition wording
required fields
explanation presence
correct answer presence
```

Expected current result:

```text
quality_status = needs_improvement
quality_gate_pass = false
```

This is a successful detection, not a failed milestone.

## Safety constraints

v0.4.54 still does not:

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
accept user-provided filesystem roots
```

## Why this matters

Before local-bank questions are used in study sessions, Voila needs to detect and block low-quality question patterns such as:

```text
Care afirmație identifică cel mai bine conceptul...
```

These questions are useful for scaffolding but not enough for real Exam Prep quality.

## Recommended next milestone

v0.4.55 — Local pedagogy question variety upgrade.

Suggested scope:

- generate more than concept-recognition questions
- add explain/apply/compare/formula questions
- preserve local-only/no API design
- keep live consumption disabled

## v0.4.55 update

After the local pedagogy question variety upgrade, the diagnostic local sample is expected to pass the quality gate.

The gate remains useful because it will still detect future regressions such as repetitive concept-recognition-only output.

