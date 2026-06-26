# Exam Prep generated question quality audit — v0.4.43

Status: PASS — read-only planning audit.

## Purpose

This checkpoint records that Exam Prep is now stable enough to continue toward generated question quality improvements, but the generator itself must not be rewritten blindly.

The previous v0.4.42 real progress data audit confirmed that the current Exam Prep surface is stable: dashboard, skill detail, progress summary, progress interpretation, learning path, weak review, study session entry, compactness, and Romanian terminology are protected by checkpoints.

## Current limitation

The current Exam Prep question layer is still simple and repetitive. The next functional direction should focus on question quality, not more UI polish.

Observed risk areas:

- generated questions are too simple
- generated questions are repetitive
- question types are limited
- explanations are not yet pedagogically rich
- weak review needs similar-but-not-identical practice items
- STEM content needs formula/image-aware questions
- no paid API/cloud dependency should be introduced

## Required constraints

The next implementation must keep:

- no cloud/API cost
- no OpenAI API
- no Mathpix API
- no Ollama/LM Studio requirement yet
- no generator rewrite in this audit checkpoint
- no UI behavior changes
- no progress threshold changes
- no regression of Romanian terminology
- no deprecated `stăpânire` wording

## Recommended architecture

Exam Prep should remain the progress and practice interface.

A new local-first content layer should become the content supplier:

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

## Recommended next step

v0.4.44 — Local Pedagogy Engine scaffold.

Scope:

- create a local-only pedagogy scaffold
- generate `course_analysis.local.json`
- generate `exercise_bank.local.json`
- generate `exam_blueprint.local.json`
- keep legacy quiz/question fallback
- connect nothing destructively
- preserve current Exam Prep routes and health checks

## Acceptance for this checkpoint

This checkpoint is complete when:

- this audit document exists
- the consolidation plan references v0.4.43
- existing Exam Prep health checks still pass
- no runtime generator behavior is changed

