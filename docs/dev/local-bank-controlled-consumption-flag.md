# Local bank controlled consumption flag — v0.4.52

Status: disabled-by-default consumption flag scaffold.

## Purpose

This milestone introduces an explicit flag for future controlled consumption of local-bank Exam Prep questions.

The default behavior remains legacy fallback.

## Added module

```text
services/api/exam_prep_local_bank_consumption_flag.py
```

## Added flag

```text
VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_CONSUMPTION
```

Default:

```text
OFF
```

## Behavior

When the flag is OFF:

```text
selected_source = legacy_fallback
```

When the flag is ON and a valid local preview is available:

```text
selected_source = local_exercise_bank_adapter
```

## Safety constraints

v0.4.52 still does not:

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

## Path safety

The diagnostic module does not accept a filesystem root from user input. It generates an internal temporary sample for source-selection checks.

## Added check

```text
scripts/dev/check-local-bank-consumption-flag.ps1
```

The check verifies:

1. flag OFF selects `legacy_fallback`
2. flag ON selects `local_exercise_bank_adapter`
3. legacy fallback remains available
4. local preview is available only as a controlled diagnostic source
5. no attempts/scoring/progress/live consumption behavior is enabled

## Non-goals

This milestone does not:

- wire local bank into live study sessions
- persist attempts
- score answers
- update progress
- change weak review
- add public UI
- add a web route
- add OpenAI, Mathpix, Ollama, LM Studio, or API costs

## Recommended next milestone

v0.4.53 — Local bank source selection adapter for dry-run study sessions.

