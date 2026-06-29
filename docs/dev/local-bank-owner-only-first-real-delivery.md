# Voila Exam Prep v0.5.0 — owner-only local-bank first real delivery

Milestone: `v0.5.0-owner-only-local-bank-first-real-delivery`

This is the first separately approved real-delivery implementation after the
v0.4.94 implementation readiness freeze.

## Scope

Allowed:

- owner-only local execution
- local exercise bank source
- maximum 5 delivered questions
- sanitized question envelopes only
- no public UI
- no `web_app.py` patch
- no attempts persistence
- no session persistence
- no progress persistence or progress update
- no live scoring persistence
- rollback to `legacy_fallback`
- no cloud/API/LLM/costs

## Flags

Real delivery requires:

`VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY=1`

Rollback is forced by:

`VOILA_FORCE_EXAM_PREP_LOCAL_BANK_OWNER_ONLY_FIRST_REAL_DELIVERY_ROLLBACK=1`

The v0.4.94 readiness freeze chain must also be ready.

## Default behavior

Without the v0.5.0 owner-only flag:

```json
{
  "status": "disabled",
  "effective_source": "legacy_fallback",
  "delivery_performed": false,
  "delivered_question_count": 0
}
```

## Owner-only real delivery behavior

With the v0.4.94 readiness freeze chain ready and the v0.5.0 flag enabled:

```json
{
  "status": "owner_only_first_real_delivery_performed",
  "effective_source": "local_bank",
  "delivery_performed": true,
  "delivered_question_count": 5
}
```

The delivered question count is capped at 5 even if more local-bank records are available.

## Validation

Run:

```powershell
scripts/dev/check-local-bank-owner-only-first-real-delivery.ps1
```

Expected result:

```text
=== v0.5.0 CHECK PASS ===
```
