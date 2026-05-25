# Voila! Tester Handoff Checklist

## Before sending

- [ ] Confirm ZIP exists locally
- [ ] Confirm SHA256 matches
- [ ] Confirm the ZIP was tested after extraction
- [ ] Confirm START-VOILA.bat starts in background
- [ ] Confirm http://127.0.0.1:8787 returns 200 OK
- [ ] Confirm STOP-VOILA.bat releases ports 8081 and 8787
- [ ] Confirm no old PDFs are included
- [ ] Confirm data folder is clean
- [ ] Confirm no LICENSE file was added
- [ ] Confirm no GitHub release was uploaded
- [ ] Confirm no v0.3.1 tag was created

## What to send

Send tester:

- ZIP file or private download link
- SHA256 checksum
- short instructions
- limitations note
- feedback questions

## Tester instructions

Ask the tester to:

1. Download ZIP.
2. Extract ZIP.
3. Open extracted folder.
4. Double-click START-VOILA.bat.
5. Wait 10-20 seconds.
6. Open http://127.0.0.1:8787 if browser does not open.
7. Test with a small, non-confidential PDF.
8. Review generated outputs.
9. Double-click STOP-VOILA.bat when finished.
10. Send feedback.

## Troubleshooting instructions

If START-VOILA.bat does not work:

- use START-VOILA-DEBUG.bat
- copy the visible error
- send screenshot or text output

If STOP-VOILA.bat does not work:

- use STOP-VOILA-DEBUG.bat
- copy the visible error
- send screenshot or text output

## Safety reminders

Tell testers:

- do not use confidential documents
- do not use personal data
- do not use legal, medical, financial, safety-critical or compliance-critical files
- generated content must be reviewed by a human
- this is a public beta tester package, not a finished product
