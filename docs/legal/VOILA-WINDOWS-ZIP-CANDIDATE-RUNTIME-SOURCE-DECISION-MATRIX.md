# Voila Windows ZIP Candidate Runtime Source Decision Matrix

## Purpose

Compare possible runtime sources for the first controlled Voila Windows ZIP candidate.

This is planning-only.

---

## Decision criteria

Use these criteria:

```text
repeatability
freshness
runtime confidence
legal/package readiness
risk of private files
risk of stale docs
ease of smoke testing
auditability
```

---

## Option A: latest validated tester package source

Score:

```text
repeatability: medium
freshness: medium
runtime confidence: high
legal/package readiness: medium
private file risk: low/medium
stale docs risk: medium
smoke testing: high
auditability: medium
```

Best when:

```text
a recent package was already validated and is easy to identify
```

Do not use if:

```text
tester package is old
tester package has outdated README/legal wording
tester package has demo-only limits not intended for the ZIP candidate
```

---

## Option B: fresh runtime staging generated from repository

Score:

```text
repeatability: high
freshness: high
runtime confidence: medium until smoke-tested
legal/package readiness: high
private file risk: low if scripted
stale docs risk: low
smoke testing: medium/high
auditability: high
```

Best when:

```text
the goal is a clean repeatable package pipeline
```

Recommended:

```text
Yes
```

---

## Option C: previous public beta runtime package

Score:

```text
repeatability: medium
freshness: low/medium
runtime confidence: high if previously tested
legal/package readiness: low/medium
private file risk: low
stale docs risk: high
smoke testing: high
auditability: medium
```

Best when:

```text
needing a conservative public beta baseline
```

Do not use if:

```text
current legal/package docs differ materially
```

---

## Option D: internal manual staging folder

Score:

```text
repeatability: low
freshness: variable
runtime confidence: variable
legal/package readiness: variable
private file risk: medium/high
stale docs risk: medium/high
smoke testing: variable
auditability: low
```

Best when:

```text
only doing local experiments
```

Do not use for:

```text
shareable candidate unless fully documented and validated
```

---

## Recommendation

Use:

```text
Option B: fresh runtime staging generated from repository
```

Fallback:

```text
Option A: latest validated Windows tester package source
```

Avoid:

```text
Option D for shareable ZIP candidate
```
