# Local Pedagogy Engine scaffold — v0.4.44

Status: scaffold.

## Purpose

This milestone introduces the first local-only content layer for improving Voila lessons and Exam Prep question quality without API costs.

It follows the v0.4.43 generated question quality audit recommendation: keep Exam Prep stable, then add a better local content supplier.

## Non-goals

This milestone does not:

- call OpenAI or any paid API
- call Mathpix
- require Ollama or LM Studio
- replace the legacy quiz/question generator
- change Exam Prep progress thresholds
- rewrite the Exam Prep dashboard or skill detail UI
- perform LaTeX OCR
- remove existing fallbacks

## Added scaffold

New module:

```text
services/api/local_pedagogy_engine.py
```

New check:

```text
scripts/dev/check-local-pedagogy-engine.ps1
```

Generated output shape:

```text
course_analysis.local.json
exercise_bank.local.json
exam_blueprint.local.json
```

## Intended integration model

```text
PDF / OCR / Course
        ↓
Local Pedagogy Engine
        ↓
course_analysis.local.json
exercise_bank.local.json
exam_blueprint.local.json
        ↓
Exam Prep
        ↓
Dashboard / Study / Progress / Review weak / Exam mode
```

## Current behavior

The module can create deterministic JSON outputs from plain course text:

- `course_analysis.local.json` records concept, objective, sentence, and signal metadata
- `exercise_bank.local.json` creates a safe initial bank of local exercises
- `exam_blueprint.local.json` records a future selection policy for balanced Exam Prep sessions

The output is intentionally conservative. It is a scaffold, not the final pedagogy engine.

## Safety and cost constraints

This scaffold is local-first and dependency-free. It uses no network access, no paid OCR, no LLM API, and no hidden cloud provider.

## Next milestone

Recommended next step:

v0.4.45 — Local exercise bank integration planning/checkpoint.

Possible scope:

- define how Exam Prep discovers `exercise_bank.local.json`
- keep fallback to existing `quiz.json` / legacy question source
- add source labels for future debugging
- keep UI changes minimal
- preserve weak review and progress behavior

