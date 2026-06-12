# Voila Windows ZIP Candidate Complete Runtime Source START/STOP Smoke Safety Notes

Milestone:

```text
v0.3.56-voila-windows-zip-candidate-complete-runtime-source-start-stop-smoke-plan
```

## Safety goal

Run a local smoke test without damaging the developer machine, repository, or unrelated processes.

## Package root safety

The extracted package root must be under a temp/output folder. It must not be repository root, docs/, scripts/, services/, or .git/.

## Process safety

START/STOP must only manage package-owned processes. STOP must rely on package state/PID files and must not broadly kill all Python, Java, Tesseract, Voila, or LanguageTool processes.

## Port safety

Check ports before and after:

```text
8787 for Voila API
8081 for LanguageTool if applicable
```

If a port is already occupied before START, stop and document the blocker instead of killing unknown processes.

## Artifact safety

The smoke must not create EXE installer, MSI installer, GitHub release, release upload, or payment/licensing artifacts.

## Data safety

The smoke should use the packaged runtime only and should not process private PDFs or user documents.

## Cleanup expectation

After STOP, port 8787 should be free and package-owned process should be stopped. Temporary package folder may be kept for inspection.
