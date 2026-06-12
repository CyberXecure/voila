# Voila Windows ZIP Candidate Tester Handoff

Milestone:

```text
v0.3.63-voila-windows-zip-candidate-tester-readiness-review
```

## Candidate to hand off

```text
voila-v0.3.61-public-beta-windows-package-candidate.zip
SHA256: 121F3747203BB539033FDE073BC51BD1B0C707C1C562E25A10CE9A77EA24941A
```

## Short message for testers

```text
This is a local Windows public beta test package for Voila.

Please extract the ZIP, open the extracted voila folder, run START-VOILA.bat, then open http://127.0.0.1:8787 in your browser.

When finished, run STOP-VOILA.bat.

Please test only with small non-private PDFs and send feedback if START, upload, course generation, or STOP fails.
```

## Tester checklist

```text
[ ] ZIP downloaded
[ ] ZIP extracted
[ ] START-VOILA.bat launched
[ ] browser opened at http://127.0.0.1:8787
[ ] sample PDF uploaded
[ ] course generation tested
[ ] STOP-VOILA.bat launched
[ ] feedback sent
```

## Feedback requested

Ask testers to report:

```text
Windows version
whether START returned control
whether browser page opened
whether upload worked
whether course generation worked
whether STOP worked
screenshots of any errors
runtime/logs/start-voila.log if START fails
runtime/logs/voila-api.err.log if API fails
runtime/logs/stop-voila.log if STOP fails
```

## Privacy note

Testers should not use confidential, medical, financial, legal, or customer PDFs during the first smoke feedback round.
