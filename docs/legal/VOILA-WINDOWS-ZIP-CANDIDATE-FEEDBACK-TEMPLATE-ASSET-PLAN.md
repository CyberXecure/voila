# Voila Windows ZIP Candidate Feedback Template Asset Plan

Milestone:

```text
v0.3.64-voila-windows-zip-candidate-release-asset-staging-plan
```

## Purpose

Define the feedback template to include with the staged tester assets.

## Planned FEEDBACK-TEMPLATE.txt

Recommended content:

```text
Voila Windows Beta Feedback

Tester name:
Windows version:
ZIP filename:
Did START-VOILA.bat return control? Yes/No
Did http://127.0.0.1:8787 open? Yes/No
Did /health respond if checked? Yes/No
Did PDF upload work? Yes/No
Did course generation work? Yes/No
Did STOP-VOILA.bat work? Yes/No
Was port 8787 free after STOP if checked? Yes/No

What worked well?

What failed?

Screenshots attached? Yes/No

Logs attached if failure:
- runtime/logs/start-voila.log
- runtime/logs/voila-api.err.log
- runtime/logs/stop-voila.log

Please do not send private PDFs unless explicitly agreed.
```

## Required feedback fields

The template must request:

```text
Windows version
START result
browser/local URL result
upload result
generation result
STOP result
screenshots/logs for failures
privacy reminder
```
