# Voila Windows ZIP Candidate START/STOP Smoke Safety Notes

## Purpose

Define safety boundaries for running START/STOP smoke tests on a local Windows ZIP candidate.

This is planning-only.

---

## Local-only execution

Run smoke tests only on a local machine where it is safe to start local services.

Do not run this smoke test on:

```text
production systems
shared servers
machines with sensitive workloads
unknown/untrusted Windows environments
```

---

## Before START

Check and document:

```text
current working folder
package extracted folder
expected ports
currently running Voila/LanguageTool processes
available disk space
antivirus/quarantine warnings if any
```

---

## During START

Do not ignore:

```text
blocked scripts
missing runtime files
port conflicts
Java startup errors
Python startup errors
OCR runtime errors
unexpected external network calls
```

---

## During STOP

Confirm:

```text
all expected processes are stopped
ports are released
temporary service windows are closed
no repeated crash/restart loop exists
```

---

## Manual cleanup

If manual cleanup is required, classify result as:

```text
CONDITIONAL
```

unless the failure prevents basic usage, then classify as:

```text
FAIL
```

---

## Publication safety

A local smoke PASS is not a publication approval.

Do not publish until a separate publication/release gate is completed.
