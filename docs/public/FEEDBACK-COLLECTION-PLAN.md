# Voila Feedback Collection Plan

## Purpose

Collect practical feedback from early Voila public beta testers.

The goal is not to prove that Voila is finished. The goal is to understand:

- whether testers can start Voila
- whether upload and generation are clear
- whether the generated course is useful
- whether lessons, figures, study mode, and progress make sense
- what should be improved before a stronger public release

---

## Tester profile

Ideal early testers:

- use PDFs for learning, work, research, or training
- are comfortable downloading and extracting a ZIP
- can follow simple Windows instructions
- can test with a small, non-confidential PDF
- are willing to give honest feedback

Good tester categories:

- students
- trainers
- engineers
- technical readers
- researchers
- documentation-heavy professionals
- self-learners

---

## Tester instructions

Ask testers to complete this workflow:

1. Download the Voila public beta package.
2. Extract the ZIP.
3. Start Voila using the included start script.
4. Open the local Voila interface.
5. Upload a small, non-confidential PDF.
6. Generate a course.
7. Open the generated course.
8. Review lessons.
9. Open figures.
10. Try study mode.
11. Check progress.
12. Send feedback.

---

## Tester questions

### Setup

1. Were you able to start Voila?
2. Were the instructions clear?
3. Did anything look confusing during startup?
4. Did Windows show any warning that was unclear?
5. Did the browser page open as expected?

### Upload

6. Was it clear how to upload a PDF?
7. Did the upload result make sense?
8. Did you understand what to do after uploading?
9. Did the page limit notice make sense?
10. Did you know which type of PDF to test with?

### Course generation

11. Was the course generation flow clear?
12. Did course generation complete successfully?
13. Did the generated course look useful?
14. Were the available course actions clear?
15. Did you know where to click next?

### Lessons

16. Were the generated lessons easy to read?
17. Did the lesson structure help you understand the PDF?
18. Were lesson titles useful?
19. Did any lesson look wrong or confusing?
20. What would make lessons better?

### Figures

21. Were extracted figures useful?
22. Did the figure gallery help you understand the document?
23. Were any figures wrong, missing, duplicated, or unclear?
24. Were figure titles and page references helpful?
25. Should figures be displayed differently?

### Edit crops / OCR

26. Did you understand what Edit crops does?
27. Were crop controls understandable?
28. Did this feature feel useful or too advanced?
29. What would make crop editing clearer?
30. Did you notice OCR or extraction problems?

### Study mode

31. Was study mode useful?
32. Were recommended questions relevant?
33. Was the expected answer/explanation useful?
34. Did Correct / Incorrect make sense?
35. Would you use study mode again?

### Progress

36. Was the progress dashboard clear?
37. Did mastery percentage make sense?
38. Did study coverage make sense?
39. Was recommended next focus useful?
40. Would progress tracking motivate you to continue?

### Overall

41. What was the most useful part of Voila?
42. What was the most confusing part?
43. What should be improved first?
44. What feature is missing?
45. Would you use Voila again with another PDF?
46. Would you recommend it to someone else?
47. Would you pay for a polished version?
48. What would make it worth paying for?
49. What type of documents would you use with Voila?
50. Any other comments?

---

## Simple feedback form

Recommended fields:

```text
Tester name or ID:
Windows version:
Voila version:
PDF type tested:
PDF page count:
PDF language:
Was setup successful? Yes / No
Was upload successful? Yes / No
Was course generation successful? Yes / No
Did lessons look useful? Yes / Maybe / No
Did figures look useful? Yes / Maybe / No
Was study mode useful? Yes / Maybe / No
Was progress clear? Yes / Maybe / No
Most useful feature:
Most confusing part:
Biggest missing feature:
Would use again? Yes / Maybe / No
Would recommend? Yes / Maybe / No
Would pay for a polished version? Yes / Maybe / No
General comments:
```

---

## Short feedback form

For quick tester feedback, use only these questions:

```text
1. Were you able to start Voila?
2. Were you able to upload a PDF?
3. Were you able to generate a course?
4. Were the lessons useful?
5. Were the figures useful?
6. Was study mode useful?
7. What was confusing?
8. What should be improved first?
9. Would you use Voila again?
10. Any other comments?
```

---

## Success metrics

### Activation metrics

Target for next beta checkpoint:

```text
At least 70% of testers can start Voila without help.
At least 70% can upload a PDF successfully.
At least 60% can generate a course successfully.
```

### Usefulness metrics

Target:

```text
At least 50% say generated lessons are useful.
At least 50% say the generated course is easier to study than the original PDF.
At least 40% try study mode after generating a course.
At least 40% open the figures page.
```

### Clarity metrics

Track repeated confusion around:

```text
startup
Windows warnings
where to upload PDF
what to do after upload
course generation
where to open lessons
what Edit crops means
how progress is calculated
```

### Product signal

Strong signal:

```text
tester tries a second PDF without being asked
tester asks for a higher page limit
tester asks for export features
tester wants to use it for work, school, or training
tester asks when the next version is available
tester would recommend it to another person
```

Weak signal:

```text
tester starts the app but does not upload a PDF
tester uploads a PDF but does not generate a course
tester generates a course but does not open lessons
tester does not understand the generated content
tester says the workflow is too confusing
```

---

## Feedback summary format

Use this format after collecting feedback:

```text
Voila public beta feedback summary

Version:
Testers:
PDFs tested:

Successful starts:
Successful uploads:
Successful course generations:

Most useful features:
- ...

Most confusing areas:
- ...

Top requested improvements:
- ...

Blocking issues:
- ...

Positive product signals:
- ...

Weak product signals:
- ...

Recommended next milestone:
- ...
```

---

## Recommended follow-up milestones

Possible next milestones after feedback:

```text
v0.3.4-voila-public-beta-feedback-summary
v0.3.5-voila-tester-onboarding-polish
v0.3.6-voila-study-and-progress-copy-polish
v0.3.7-voila-ocr-and-figures-usability-polish
```

---

## Boundaries

This feedback plan is documentation only.

It does not add:

- telemetry
- analytics
- backend collection
- cloud forms
- runtime changes
- automatic reporting
- user accounts
- payment flow
