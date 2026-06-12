# Voila Windows ZIP Candidate Tester Known Limitations

Milestone:

```text
v0.3.63-voila-windows-zip-candidate-tester-readiness-review
```

## Public beta status

This is a public beta candidate for limited testing.

It is not final production software.

## Known limitations

```text
Windows ZIP package, not installer
local-only app served from 127.0.0.1:8787
browser does not necessarily open automatically
tester may see SmartScreen/Windows security warnings because there is no signed installer
first start may take several seconds
large PDFs may be slow or limited depending on current demo/runtime constraints
OCR quality depends on source PDF quality
LanguageTool/OCR dependencies may be deferred depending on packaged runtime path
no payment/licensing activation is included
no formal support SLA is included
```

## Tester data guidance

Use:

```text
small public/sample PDFs
non-private test documents
documents that can be shared back if debugging is needed
```

Avoid:

```text
private contracts
medical records
financial records
identity documents
customer documents
confidential company files
```

## Failure handling

If START fails, collect:

```text
runtime/logs/start-voila.log
runtime/logs/voila-api.err.log
screenshot of terminal/window
Windows version
```

If STOP fails, collect:

```text
runtime/logs/stop-voila.log
port/process status if available
```
