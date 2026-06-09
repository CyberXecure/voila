# Voila EULA Draft Outline

## Purpose

This document outlines the structure of a future Voila End User License Agreement.

It is not a final legal agreement.

It is a drafting outline for later review.

## Recommended EULA title

```text
Voila End User License Agreement
```

Alternative title for beta builds:

```text
Voila Public Beta End User License Agreement
```

## Recommended sections

### 1. Introduction

Purpose:

```text
identify the software
identify the publisher/project owner
state that the agreement applies to Voila packages
state that using the software means accepting the terms
```

Draft intent:

```text
This EULA applies to Voila public beta, tester demo, Supporter, Pro, and related Windows packages unless a separate written agreement says otherwise.
```

### 2. License grant

Purpose:

```text
define what the user is allowed to do
keep rights limited
separate beta/personal/internal/commercial use
```

Possible beta wording:

```text
You may install and use Voila beta software for evaluation, testing, feedback, personal learning, or internal non-commercial review, subject to the applicable release notes and beta terms.
```

For future paid builds:

```text
Supporter and Pro rights should be defined by the applicable license tier, invoice, purchase page, or written agreement.
```

### 3. Restrictions

Purpose:

```text
protect proprietary rights
prevent redistribution/repackaging/resale
prevent misleading branding
```

Restrictions to include:

```text
no resale
no unauthorized redistribution
no sublicensing
no rebranding
no commercial hosting without permission
no removing copyright notices
no claiming ownership
no using Voila branding misleadingly
no reverse engineering beyond what law allows
```

### 4. Beta status and limitations

Purpose:

```text
avoid overpromising
make beta status clear
make package limits clear
```

Topics:

```text
beta software
may contain bugs
generated content may contain errors
page-count limits may apply
release notes define package type and limits
not production-certified
```

### 5. User documents and responsibility

Purpose:

```text
clarify that users are responsible for the documents they process
avoid sensitive documents in public testing/feedback
```

Topics:

```text
user must have rights to process documents
user should avoid confidential documents in public demos
user is responsible for reviewing generated content
user should independently verify important output
```

### 6. Generated content disclaimer

Purpose:

```text
generated lessons, OCR, figures, questions, summaries, and study material may be wrong
```

Topics:

```text
OCR errors
extraction errors
formatting errors
incorrect summaries
missing figures
incorrect study questions
not professional advice
not a substitute for expert review
```

### 7. Third-party components

Purpose:

```text
acknowledge bundled/open-source/third-party components
clarify separate licenses
```

Topics:

```text
Python runtime and packages
FastAPI/backend dependencies
frontend dependencies
OCR tooling
Tesseract-related files
LanguageTool
Java/JRE runtime
PDF processing libraries
fonts/icons/assets
```

Reference:

```text
docs/legal/THIRD-PARTY-NOTICES.md
```

### 8. Ownership

Purpose:

```text
state that Voila remains owned by the project owner
```

Topics:

```text
software ownership
documentation ownership
brand ownership
screenshots/public materials
no transfer of ownership
```

### 9. Feedback

Purpose:

```text
allow using feedback to improve Voila
avoid confidential feedback
```

Topics:

```text
users may provide feedback
feedback may be used to improve product/docs/releases
do not include confidential information in feedback
```

### 10. No warranty

Purpose:

```text
make beta/no warranty position clear
```

Topics:

```text
as-is
no guarantee of accuracy
no guarantee of uninterrupted operation
no guarantee of compatibility
no guarantee of fitness for a particular purpose
```

### 11. Limitation of liability

Purpose:

```text
limit risk from incorrect output, data loss, misuse, or reliance
```

Topics:

```text
data loss
incorrect generated content
OCR/extraction errors
business loss
academic/professional reliance
misuse of documents
```

### 12. Termination

Purpose:

```text
define that rights end if terms are violated
```

Topics:

```text
license ends on violation
user must stop using and delete copies if required
```

### 13. Changes to terms

Purpose:

```text
allow future beta/pro terms to evolve
```

Topics:

```text
terms may be updated
new releases may include new terms
older packages remain governed by included terms unless stated otherwise
```

### 14. Contact

Purpose:

```text
provide licensing/support/contact channel
```

Topics:

```text
commercial use
permission requests
partnerships
licensing questions
support/contact path
```

## Drafting notes

Keep the EULA:

```text
short enough to read
specific to Voila
consistent with BETA-TERMS.md
consistent with LICENSE.txt
consistent with release notes
not overly complex before monetization
reviewable by legal counsel later
```

## Open questions

```text
Should beta EULA and paid EULA be separate?
Should Supporter and Pro have separate terms?
Should commercial use require Pro?
Should generated content export rights be limited?
Should privacy policy be separate?
Should package telemetry be absent by default?
Should warranty/limitation wording be country-specific?
```
