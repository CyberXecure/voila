# Voila Screenshot Showcase Guide

## Purpose

This guide documents the public screenshot set used for the Voila README, landing page copy, tester materials, and future showcase pages.

The current screenshot set is part of:

```text
v0.3.3-voila-readme-and-showcase-refresh
```

Scope:

- documentation only
- public presentation only
- no runtime changes
- no backend changes
- no frontend behavior changes
- no dependency changes

---

## Screenshot folder

Recommended repository folder:

```text
docs/public/screenshots/
```

---

## Current screenshot set

Use these files:

```text
voila-01-upload-pdf.png
voila-02-generated-library.png
voila-03-lessons.png
voila-04-figures-gallery.png
voila-05-edit-crops.png
voila-06-study-mode.png
voila-07-progress-dashboard.png
voila-08-course-tools.png
```

---

## Naming convention

Use this pattern:

```text
voila-XX-short-feature-name.png
```

Rules:

- use lowercase
- use hyphens
- use two-digit ordering numbers
- keep names descriptive
- avoid spaces
- avoid temporary names such as screenshot1.png
- avoid dates in filenames unless the image is explicitly archival
- keep order aligned with the user journey

Recommended order:

1. upload PDF
2. generated library
3. lessons
4. figures gallery
5. edit crops
6. study mode
7. progress dashboard
8. course tools

---

## Recommended image dimensions

Current screenshots:

```text
1920 x 840
```

This is acceptable for:

- GitHub README
- landing page sections
- documentation pages
- public showcase material

Recommended future sizes:

```text
Master screenshots: 1920 x 840
README images: use master PNG files directly
Landing page images: use master PNG files or optimized 1440 px wide copies
Social preview: create separate 1200 x 630 image
Thumbnail previews: create separate 800 px wide copies if needed
```

Do not crop each screenshot differently unless there is a specific reason. Consistency is more important than perfect framing.

---

## Screenshot descriptions

### voila-01-upload-pdf.png

Shows the initial upload screen with Voila branding, local PDF upload, and limited tester demo notice.

Use for:

- README hero
- landing page hero
- first step in user journey
- tester onboarding

Alt text:

```text
Voila upload screen for selecting a local PDF.
```

---

### voila-02-generated-library.png

Shows a generated PDF entry in the local library with actions such as Generate course, Open course, Figures, Edit crops, Study, Progress, Logs, and Delete from library.

Use for:

- generated course workflow
- showing main document actions
- demonstrating local library behavior

Alt text:

```text
Voila generated PDF library entry with course actions.
```

---

### voila-03-lessons.png

Shows generated lessons and lesson cards.

Use for:

- lesson generation feature
- course structure explanation
- learning workflow

Alt text:

```text
Voila lessons page showing generated lesson cards.
```

---

### voila-04-figures-gallery.png

Shows hybrid figure extraction and figure gallery.

Use for:

- figure extraction feature
- visual content explanation
- technical document showcase

Alt text:

```text
Voila figure gallery showing extracted figures from a PDF.
```

---

### voila-05-edit-crops.png

Shows crop editor modal and crop adjustment controls.

Use for:

- OCR and figure cleanup explanation
- advanced PDF review workflow
- crop editing feature

Alt text:

```text
Voila crop editor for adjusting extracted figure regions.
```

---

### voila-06-study-mode.png

Shows recommended question, expected answer, concept mastery, and study buttons.

Use for:

- study mode feature
- active learning explanation
- concept review workflow

Alt text:

```text
Voila study mode with a recommended question and concept mastery cards.
```

---

### voila-07-progress-dashboard.png

Shows overall mastery, study coverage, concept status, and recommended next focus.

Use for:

- progress tracking feature
- dashboard explanation
- learning analytics preview

Alt text:

```text
Voila progress dashboard showing mastery and study coverage.
```

---

### voila-08-course-tools.png

Shows the Course Tools page with available course actions.

Use for:

- course hub explanation
- final workflow screenshot
- feature overview

Alt text:

```text
Voila Course Tools page showing course actions.
```

---

## README markdown pattern

Use this structure:

```markdown
### Upload PDF

![Upload PDF](docs/public/screenshots/voila-01-upload-pdf.png)
```

For longer sections:

```markdown
### Study mode

Study mode recommends questions generated from the course content and lets users mark answers as correct or incorrect.

![Study mode](docs/public/screenshots/voila-06-study-mode.png)
```

---

## Landing page placement

Recommended layout:

```text
Hero:
- voila-01-upload-pdf.png

Section: From PDF to course
- voila-02-generated-library.png

Section: Lessons
- voila-03-lessons.png

Section: Figures
- voila-04-figures-gallery.png

Section: OCR and crops
- voila-05-edit-crops.png

Section: Study
- voila-06-study-mode.png

Section: Progress
- voila-07-progress-dashboard.png

Section: Course Tools
- voila-08-course-tools.png
```

---

## Screenshot quality checklist

Before committing screenshots, verify:

```text
[ ] filenames follow the convention
[ ] files are in docs/public/screenshots/
[ ] screenshots are not blurry
[ ] screenshots do not show private data
[ ] screenshots do not show API keys or secrets
[ ] screenshots use a small sample PDF
[ ] screenshots are visually consistent
[ ] README image paths work
[ ] public beta wording is accurate
```

---

## Current sample document note

The screenshots use a small machine learning sample PDF for demonstration.

Guideline:

- use only public, sample, or non-confidential PDFs in public screenshots
- avoid personal documents
- avoid customer documents
- avoid copyrighted book pages unless permission and usage are clear
- avoid sensitive metadata in paths or browser UI

---

## Future improvements

Possible later showcase additions:

- short GIF or MP4 demo
- 1200 x 630 social preview image
- before/after PDF-to-course visual
- landing page screenshot carousel
- Windows tester quick-start visual guide
- public beta release image
