# Guarded local-bank first live trial planning document — v0.4.76

Status: planning-only document.

This milestone intentionally makes no live code-path change.

## Purpose

v0.4.76 defines what the first real guarded local-bank live trial would mean after the shadow chain v0.4.60-v0.4.75.

The current production behavior remains:

```text
effective_source = legacy_fallback
```

## Non-goals

v0.4.76 does not:

```text
deliver local-bank questions live
consume local-bank questions live
start live sessions
replace effective source
persist progress
persist sessions
persist attempts
update progress
score live study sessions
modify public Exam Prep navigation
modify weak review
replace live study sessions
replace the legacy generator
enable live consumption
require cloud/API
accept user-provided filesystem roots
```

## Definition of "live"

A future milestone may be considered "live" only when all of the following are true:

```text
a real study session receives local-bank questions instead of legacy questions
the local-bank source becomes the effective source for that guarded request
the user can answer those questions inside a session context
the answer flow has an explicit scoring/evaluation path
the attempt flow has an explicit persistence decision
the progress flow has an explicit update decision
a failure or owner abort returns to legacy_fallback
```

Until all of those are introduced explicitly, the system remains preview/shadow/no-op only.

## Required preconditions before first live trial

The next phase must require:

```text
v0.4.75 consolidation status complete
owner decision gate remains explicit
adapter no-op boundary remains available
shadow report and owner panel remain sanitized
legacy_fallback remains available
quality gate passes immediately before candidate use
CodeQL checks pass
no user-provided filesystem root reaches a web route
all answer/explanation leakage tests pass
```

## Required owner flags

A future first live trial must not rely on one flag only.

It should require a layered owner opt-in:

```text
guarded live-trial flag
decision gate flag
adapter boundary flag
source selector/shadow verification flag
first live trial explicit flag
optional session persistence flag
optional progress update flag
optional scoring flag
```

The first live trial flag must be new and specific. It must not reuse the shadow flag.

## Minimum abort/fallback rules

The first live trial must abort to `legacy_fallback` when:

```text
owner flags are incomplete
quality gate fails
candidate question count is below minimum
question type diversity is below minimum
skill coverage is missing
answer/explanation leakage is detected
candidate payload contains raw source excerpts when not expected
session state cannot be created safely
attempt persistence is not explicitly enabled
progress update is not explicitly enabled
any route accepts user-provided filesystem root
CodeQL reports a new alert
```

Abort behavior must be explicit and testable:

```text
effective_source_after_abort = legacy_fallback
local_bank_questions_delivered = false
attempts_persisted = false
progress_updated = false
live_scoring_enabled = false
```

## Source-selection contract

A future source selector may select local-bank only if:

```text
owner decision is eligible
first live trial flag is enabled
candidate source is local_exercise_bank_adapter
quality gate passes
sanitized question envelope is used
correct answers are withheld from the UI before answer submission
legacy fallback remains available
abort path is tested
```

The source selector must still report:

```text
effective_source
fallback_source
candidate_source
selection_reason
blocking_reasons
abort_reason
```

## Attempt persistence criteria

Attempts must not be persisted in the first live trial unless a separate explicit milestone introduces:

```text
attempt schema
session id policy
question id policy
answer payload policy
score payload policy
data retention policy
idempotency policy
rollback/abort behavior
migration/no-migration decision
```

If attempt persistence is not explicitly enabled:

```text
will_persist_attempts = false
```

## Progress update criteria

Progress must not be updated in the first live trial unless a separate explicit milestone introduces:

```text
progress impact schema
mastery delta policy
weak-review integration policy
rollback behavior
session summary linkage
idempotency policy
owner-only validation report
```

If progress update is not explicitly enabled:

```text
will_update_progress = false
will_persist_progress = false
```

## Scoring criteria

Live scoring must not be enabled until a separate explicit milestone defines:

```text
question-type-specific scoring rules
accepted answer normalization
multiple choice scoring
short answer scoring
evidence-based scoring
compare/apply/rank/open-ended scoring
manual review fallback
score confidence policy
```

If scoring is not explicitly enabled:

```text
will_score_live_session = false
```

## Leakage and XSS risk checklist

Every future live trial route/panel must block:

```text
correct_answer before answer submission
correct_answer_preview in UI/panel output
explanation before answer submission
explanation_preview in UI/panel output
source_excerpt unless explicitly sanitized
raw snapshots
dry_run_items
selected_questions with raw answers
user-controlled HTML
user-controlled query values rendered server-side
user-provided filesystem roots
```

Required mitigations:

```text
safe DOM rendering with createElement/textContent/replaceChildren
no innerHTML for user/candidate content
fixed owner-smoke URLs where possible
no user-controlled HTMLResponse interpolation
explicit CodeQL check before merge
route-level disabled-by-default flags
```

## Minimal first live trial shape

The safest first live trial should be:

```text
owner-only
local-only
disabled by default
single course_id smoke
single skill_id smoke
small question limit
no attempt persistence by default
no progress update by default
no scoring persistence by default
immediate fallback to legacy_fallback on any issue
JSON report before any UI change
```

## Recommended next phase

The next milestone should not yet replace the live study session.

Recommended milestone:

```text
v0.4.77 — Guarded first live trial contract skeleton, disabled by default
```

Suggested scope:

```text
JSON-only contract object
new explicit first-live-trial flag
no web UI
no session replacement
no persistence
no progress update
no scoring
legacy_fallback remains effective unless a later milestone explicitly changes it
```

## Final v0.4.76 guarantee

```text
This milestone is planning-only.
No live code path is changed.
effective_source remains legacy_fallback.
local-bank questions are not delivered live.
```
