# v0.7.92 owner-local formula visual evidence quality filter — no build/no ZIP/no delivery

Scope:
- Adds deterministic owner-local quality metadata to formula visual evidence candidates.
- Keeps raw candidates; does not delete noisy candidates.
- Adds `quality_tier`, `quality_score`, and `noise_reasons`.
- Adds manifest `quality_counts`.
- Viewer sorts high/medium candidates before low/noisy candidates.
- Viewer displays quality tier, score, and noise reasons.

Policy:
- No OCR rewrite.
- No Formula OCR.
- No OCR Review decision write.
- No Study learning logic change.
- No BKT logic change.
- No Progress logic change.
- No generator course rewrite.
- No build.
- No ZIP.
- No share.
- No delivery.
- No distribution.
