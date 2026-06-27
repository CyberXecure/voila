# Local bank dry-run answer evaluation — v0.4.56

Status: dry-run answer evaluation scaffold.

## Purpose

This milestone evaluates answers to local-bank dry-run questions without turning those evaluations into live attempts or progress.

It follows:

```text
v0.4.55 — Local pedagogy question variety upgrade
```

## Added module

```text
services/api/exam_prep_local_bank_dry_run_answer_evaluation.py
```

## Evaluation strategy

The evaluator is local and deterministic:

```text
multiple_choice -> normalized exact match
open answers -> normalized exact match or keyword overlap
```

Supported open-answer style types include:

```text
short_answer
evidence_based
compare_concepts
apply_concept
formula_interpretation
apply_formula
```

## Added check

```text
scripts/dev/check-local-bank-dry-run-answer-evaluation.ps1
```

The check verifies:

1. correct sample answers are evaluated as correct
2. wrong sample answers are evaluated as incorrect
3. feedback previews are generated locally
4. no attempts are persisted
5. no progress is updated
6. no live study score is written

## Safety constraints

v0.4.56 still does not:

```text
persist attempts
update progress
score live study sessions
modify Exam Prep UI
modify weak review
replace live study sessions
replace the legacy generator
enable live consumption
require cloud/API
accept user-provided filesystem roots
```

## Non-goals

This milestone does not:

- enable local-bank live study sessions
- save answer attempts
- update progress
- alter mastery thresholds
- add public UI
- add a web route
- add OpenAI, Mathpix, Ollama, LM Studio, or API costs

## Recommended next milestone

v0.4.57 — Local-bank dry-run attempt envelope.

Suggested scope:

- wrap dry-run question + answer + feedback in an attempt-like object
- do not persist it
- do not update progress
- prepare the shape needed for future live integration

