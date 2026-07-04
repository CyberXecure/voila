# OCR Math Report — v0.7.7 owner-local fixture

Diagnostic local · read-only

## Summary

- Sugestii detectate: 2
- Linii posibil afectate: 3
- Report source: local owner-only fixture
- Scope: evidence check only

## Sugestii

### Suggestion 1

Line: 12

Original:

```text
lim x->0 sin x / x = 0
```

Expected diagnostic note:

```text
Potential OCR/math issue: expected classical limit equals 1.
```

### Suggestion 2

Line: 27

Original:

```text
∫_0^1 x dx = 1
```

Expected diagnostic note:

```text
Potential OCR/math issue: expected integral equals 1/2.
```

## Raw Markdown expectation

The owner-local viewer must preserve a raw Markdown report link expectation without mutating OCR, pages, course, Study, or Progress data.

[Open raw Markdown report](ocr_math_report.md)

## Safety marker

This fixture is local-only evidence. It must not trigger generation, regeneration, delivery, packaging, upload, ZIP, build, or distribution.