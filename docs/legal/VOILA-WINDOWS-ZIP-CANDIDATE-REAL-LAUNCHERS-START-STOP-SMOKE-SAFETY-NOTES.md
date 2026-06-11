# Voila Windows ZIP Candidate Real Launchers START/STOP Smoke Safety Notes

## Purpose

Define safety boundaries for running START/STOP smoke on the Windows ZIP candidate with real launchers.

This is planning-only.

---

## Local-only execution

Run the smoke only on a local validation machine.

Do not run on:

```text
production systems
shared servers
machines with sensitive workloads
unknown or untrusted Windows environments
```

---

## Process safety

The real STOP launcher should stop only package-owned processes using PID/state files.

Do not classify as PASS if the stop process relies on broad commands that kill unrelated:

```text
python
java
tesseract
voila
languagetool
```

---

## Port safety

Before START, document whether ports are free:

```text
8787
8081
```

If a port is already in use, document the process and do not kill it unless it is clearly package-owned.

---

## Log safety

Review generated logs under:

```text
runtime/logs/
```

Do not publish logs externally until checked for:

```text
local usernames
machine paths
private file paths
tokens
secrets
personal data
```

---

## Failure handling

If START fails:

```text
record exit code
record logs
do not retry blindly
check missing runtime files
check port conflicts
```

If STOP fails:

```text
record exit code
record remaining processes
record remaining ports
perform manual cleanup only after documenting state
```

---

## Publication boundary

Smoke PASS is not final publication approval.

A separate release gate should review:

```text
release notes
README wording
legal folder
known limitations
support/feedback channel
public asset upload decision
```
