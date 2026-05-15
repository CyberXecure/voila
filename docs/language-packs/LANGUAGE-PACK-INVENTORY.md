# Voila! Language Pack Inventory

Milestone: v0.2.5-public-beta-language-pack-inventory  
Status: initial translation inventory / documentation only  
Generated: 2026-05-15 07:31:43  
Scope: no runtime changes, no packaging changes, no licensing changes

## Goal

This document captures an initial inventory of possible user-facing strings that may later become part of Voila! language packs.

This milestone is intentionally safe: it does not change application behavior.

## Non-goals

This milestone does not:

- modify runtime localization logic
- add language pack loading
- add JSON language packs
- add a LICENSE
- modify the validated v0.2.0-public-beta release
- introduce paid/pro enforcement

## Scan method

The inventory was generated through a static repository scan.

Scanned extensions:
- .ts
- .tsx
- .js
- .jsx
- .py
- .html
- .vue
- .svelte

Excluded directories:
- .git
- node_modules
- .next
- dist
- build
- out
- .venv
- venv
- __pycache__
- .pytest_cache
- coverage
- release
- releases
- .mypy_cache
- .ruff_cache

Important: this is a candidate inventory. It may include false positives and may miss some strings. It should be reviewed before any runtime localization work.

To keep the repository readable, the detailed candidate string table is intentionally capped.

## Summary

| Metric | Value |
|---|---:|
| Files scanned | 172 |
| Files with candidate strings | 172 |
| Candidate lines found | 45061 |
| Candidate lines listed in this document | 800 |
| Candidate lines omitted from detailed table | 44261 |
| Max listed candidate rows | 800 |
| Max listed rows per file | 20 |

## Candidate files

| File | Candidate lines |
|---|---:|
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 17384 |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 15464 |
| services/api/web_app.py | 887 |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 839 |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 808 |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 651 |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 492 |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 489 |
| services/api/i18n.py | 287 |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 248 |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 232 |
| services/api/static/ocr_review_monaco.js | 222 |
| services/api/course_polisher.py | 186 |
| services/api/ocr_body_columns_tesseract_pages.py | 161 |
| services/api/ocr_tsv_columns_tesseract_pages.py | 149 |
| services/api/figure_exporter_hybrid.py | 143 |
| services/api/ocr_tesseract_advanced.py | 143 |
| services/api/ocr_corrections_engine.py | 141 |
| services/api/crop_editor_app.py | 136 |
| scripts/dev/add-lessons-i18n-keys.py | 133 |
| scripts/dev/write-multilingual-monaco-js.py | 133 |
| services/api/figure_exporter_vision.py | 127 |
| services/api/course_generator.py | 127 |
| services/api/study_quiz_builder.py | 122 |
| services/api/document_language.py | 122 |
| services/api/figure_exporter_auto.py | 118 |
| services/api/study_engine.py | 111 |
| scripts/dev/add-review-ocr-text-ui.py | 106 |
| services/api/ocr_text_cleaner.py | 102 |
| services/api/ocr_columns_tesseract_pages.py | 101 |
| services/api/ocr_tesseract_pages.py | 94 |
| scripts/dev/report-ocr-coverage.py | 94 |
| services/api/figure_exporter_docling_lite.py | 92 |
| scripts/dev/fix-monaco-robust-textarea-toolbar.py | 88 |
| services/api/figure_exporter.py | 87 |
| services/api/content_filter.py | 86 |
| services/api/ocr_course_builder.py | 83 |
| scripts/dev/patch-review-weak-concepts.py | 81 |
| services/api/figure_exporter_visual_fallback.py | 79 |
| scripts/dev/patch-study-quiz-v033.py | 78 |
| services/api/figure_exporter_anchor.py | 78 |
| services/api/figure_exporter_docling.py | 75 |
| scripts/dev/run-ocr-page.py | 74 |
| scripts/dev/add-document-language-module.py | 74 |
| scripts/dev/patch-study-mode.py | 70 |
| scripts/dev/add-lessons-routes.py | 69 |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 69 |
| services/api/ocr_post_cleaner.py | 69 |
| scripts/dev/fix-ocr-autocomplete-syntax.py | 69 |
| scripts/dev/create-monaco-ocr-static-assets.py | 67 |
| services/api/outline_builder.py | 67 |
| services/api/ocr_page_corrections.py | 66 |
| scripts/dev/add-review-concepts-ui.py | 65 |
| services/api/normalize_outline.py | 64 |
| services/api/ocr_gate.py | 64 |
| services/api/html_exporter.py | 63 |
| scripts/dev/add-ocr-text-autocomplete.py | 62 |
| scripts/dev/add-it-es-pt-document-languages.py | 61 |
| scripts/dev/add-course-tools-navigation.py | 59 |
| scripts/dev/add-ocr-correction-workflow.py | 57 |
| scripts/dev/hard-fix-tsv-columns-real-tsv-safe.py | 55 |
| services/api/ocr_tsv_post_cleaner.py | 54 |
| scripts/dev/hard-fix-tsv-columns-real-tsv.py | 54 |
| services/api/figure_exporter_precise.py | 53 |
| services/api/course_cleaned_finalizer.py | 53 |
| scripts/dev/make-ocr-suggestions-vscode-style.py | 53 |
| scripts/dev/patch-tsv-columns-v5-cleanup.py | 52 |
| scripts/dev/patch-progress-dashboard.py | 51 |
| services/api/scanned_course_fallback.py | 50 |
| scripts/dev/install-delete-from-library.py | 46 |
| scripts/dev/fix-tsv-columns-real-tsv.py | 42 |
| services/api/ocr_languagetool.py | 41 |
| scripts/dev/patch-upload.py | 39 |
| scripts/dev/fix-body-columns-ocr-fallback.py | 39 |
| scripts/dev/add-lesson-tools-module.py | 39 |
| services/api/lesson_tools.py | 39 |
| scripts/dev/debug-tesseract-tsv-page41.py | 37 |
| scripts/dev/patch-body-column-ocr-v3-filter.py | 36 |
| scripts/dev/add-it-es-pt-monaco-languages.py | 36 |
| services/api/pdf_image_diagnostics.py | 35 |
| scripts/dev/install-fixed-navigation.py | 35 |
| scripts/dev/add-run-ocr-page-button-monaco.py | 35 |
| services/api/figure_exporter_smart.py | 35 |
| services/api/pdf_extract.py | 34 |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 33 |
| services/api/ocr_report.py | 33 |
| scripts/dev/patch-study-content-filter.py | 33 |
| scripts/dev/add-review-ocr-floating-zoom.py | 33 |
| scripts/dev/patch-hybrid-v2.py | 30 |
| scripts/dev/add-study-questions-builder.py | 30 |
| scripts/dev/fix-tsv-parser-diagnostics.py | 29 |
| scripts/dev/fix-edit-crops-route.py | 29 |
| scripts/dev/add-run-ocr-page-endpoint.py | 29 |
| scripts/dev/add-ocr-best-text-fallback-module.py | 28 |
| scripts/dev/patch-figure-auto-v2.py | 28 |
| scripts/dev/patch-delete-from-library.py | 28 |
| scripts/dev/fix-run-ocr-page-columns.py | 28 |
| services/api/course_nav_injector.py | 28 |
| services/api/study_questions.py | 27 |
| scripts/dev/patch-auto-study-quiz.py | 27 |
| scripts/dev/patch-delete-course.py | 25 |
| services/api/ocr_best_text.py | 25 |
| scripts/dev/wire-monaco-ocr-static-assets.py | 24 |
| scripts/dev/add-quick-tools-route.py | 24 |
| scripts/dev/fix-review-concepts-save.py | 23 |
| scripts/dev/patch-lessons-i18n.py | 22 |
| scripts/dev/patch-visual-fallback-caption-required.py | 22 |
| scripts/dev/patch-study-display-translation.py | 21 |
| scripts/dev/patch-figures-strict-scan-captions.py | 21 |
| scripts/dev/patch-web-edit-crops-autostart.py | 20 |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 20 |
| scripts/dev/patch-hybrid-vector-merge.py | 20 |
| scripts/dev/fix-review-ocr-pan-zoom.py | 20 |
| scripts/dev/fix-languagetool-auto-language.py | 19 |
| scripts/dev/fix-crop-editor-missing-path.py | 19 |
| scripts/dev/smoke-monaco-static-lt.py | 18 |
| scripts/dev/fix-ocr-tesseract-utf8.py | 18 |
| scripts/dev/remove-floating-zoom-add-tip.py | 18 |
| services/api/figures_nav_injector.py | 17 |
| scripts/dev/patch-run-ocr-page-auto-lang.py | 16 |
| scripts/dev/add-lessons-to-course-tools.py | 16 |
| scripts/dev/patch-figures-explicit-caption-only.py | 16 |
| scripts/dev/smoke-document-language.py | 15 |
| scripts/dev/fix-tsv-ocr-file-output.py | 15 |
| scripts/dev/repair-floating-nav.py | 15 |
| scripts/dev/fix-home-fixed-nav.py | 15 |
| services/api/inject_course_nav_all.py | 15 |
| scripts/dev/patch-review-navigation-links.py | 15 |
| scripts/dev/smoke-languagetool-multilang.py | 14 |
| scripts/dev/smoke-tools-navigation.py | 14 |
| services/api/repair_hybrid_figures.py | 14 |
| scripts/dev/patch-scanned-fallback-pipeline.py | 14 |
| scripts/dev/smoke-home-navigation-fixed.py | 14 |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 13 |
| scripts/dev/fix-languagetool-request-annotation.py | 13 |
| scripts/dev/fix-monaco-static-includes.py | 13 |
| scripts/dev/patch-tsv-columns-min-conf.py | 13 |
| scripts/dev/smoke-languagetool-ro-en.py | 13 |
| scripts/dev/fix-monaco-wide-quickfix.py | 12 |
| scripts/dev/install-same-tab-guard.py | 12 |
| scripts/dev/patch-course-nav-pipeline.py | 12 |
| scripts/dev/fix-floating-nav-fstring.py | 12 |
| scripts/dev/hard-fix-vscode-autocomplete-css.py | 12 |
| scripts/dev/patch-visual-fallback-text-filter.py | 11 |
| scripts/dev/patch-study-prefer-study-quiz.py | 11 |
| scripts/dev/smoke-navigation-links.py | 11 |
| scripts/dev/patch-global-course-tools-links.py | 11 |
| scripts/dev/patch-floating-nav.py | 11 |
| scripts/dev/remove-old-ocr-review-button.py | 10 |
| scripts/dev/add-document-language-endpoints.py | 10 |
| scripts/dev/patch-same-tab-navigation.py | 10 |
| scripts/dev/patch-main-ui-crop-editor.py | 10 |
| scripts/dev/fix-run-ocr-page-endpoint-columns.py | 10 |
| scripts/dev/fix-vscode-autocomplete-css-braces.py | 10 |
| scripts/dev/ignore-tessdata-traineddata.py | 10 |
| scripts/dev/fix-homepage-primary-tool-css.py | 9 |
| scripts/dev/sort-lessons-natural.py | 9 |
| scripts/dev/hide-fixed-nav-on-home.py | 9 |
| scripts/dev/wire-study-question-builder.py | 9 |
| scripts/dev/smoke-study-question-builder.py | 8 |
| scripts/dev/patch-edit-crops-links.py | 8 |
| scripts/dev/fix-run-ocr-page-unicode-output.py | 8 |
| scripts/dev/wire-ocr-best-text-fallback.py | 7 |
| scripts/dev/smoke-review-ocr-text.py | 7 |
| scripts/dev/smoke-ocr-correction-workflow.py | 7 |
| scripts/dev/route-links-to-corrected-ocr-review.py | 7 |
| scripts/dev/patch-figure-vision-caption-mask.py | 7 |
| scripts/dev/ignore-local-trash.py | 7 |
| scripts/dev/rename-old-ocr-review-button.py | 6 |
| scripts/dev/add-document-language-selector-css.py | 5 |
| scripts/dev/patch-hybrid-keep-crops.py | 5 |
| scripts/dev/fix-monaco-top-row-visibility.py | 5 |

## Candidate strings

This section lists a capped sample of candidate strings. It is not a full dump.

| File | Line | Type | Snippet |
|---|---:|---|---|
| data/output/Manual-de-Supravietuire/course.cleaned.html | 4 | quoted-string | <meta charset="utf-8"> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 5 | quoted-string | <meta name="viewport" content="width=device-width, initial-scale=1"> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 6 | jsx-text | <title>Despre carte:</title> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 9 | quoted-string | const saved = localStorage.getItem("voila-theme"); |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 10 | quoted-string | const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches; |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 11 | quoted-string | const theme = saved \\|\\| (prefersDark ? "dark" : "light"); |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 12 | quoted-string | document.documentElement.setAttribute("data-theme", theme); |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 35 | quoted-string | html[data-theme="dark"] { |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 64 | quoted-string | font-family: "Segoe UI", Arial, sans-serif; |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 69 | quoted-string | html[data-theme="dark"] body { |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 259 | quoted-string | <div class="theme-bar"> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 260 | jsx-text | <button class="theme-toggle" type="button" id="themeToggle">Toggle theme</button> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 264 | jsx-text | <h1>Despre carte:</h1> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 265 | jsx-text | <p>Generated by Voila! v0.1.2</p> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 266 | jsx-text | <p>Mode: source language, no translation, no AI generation</p> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 267 | jsx-text | <p>Text status: OCR-cleaned reading text; original source preserved in pages.md/pages.json</p> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 268 | jsx-text | <p>Source: <code>D:\dev\projects\voila\data\input\Manual-de-Supravietuire.pdf</code></p> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 269 | jsx-text | <h2>L001 — PREFAŢA</h2> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 270 | jsx-text | <p>Source PDF pages: 5, 6</p> |
| data/output/Manual-de-Supravietuire/course.cleaned.html | 271 | jsx-text | <p>Word count: 969</p> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 4 | quoted-string | <meta charset="utf-8"> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 5 | jsx-text | <title>Voila! Visual Figure Extraction</title> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 11 | quoted-string | font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 64 | quoted-string | <div class="wrap"> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 65 | jsx-text | <h1>Voila! Visual Figure Extraction</h1> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 66 | jsx-text | <p>Source: <code>D:\dev\projects\voila\data\input\Manual-de-Supravietuire.pdf</code></p> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 67 | jsx-text | <p>Page range: 1–234</p> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 68 | jsx-text | <p>Detected figures: 55</p> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 70 | quoted-string | <div class="grid"> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 72 | quoted-string | <article class="card"> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 73 | jsx-text | <h2>Figure p207.1</h2> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 74 | jsx-text | <p>Visual figure candidate from PDF page 207</p> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 75 | jsx-text | <p class="meta">PDF page 207 · visual_fallback</p> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 79 | quoted-string | <article class="card"> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 80 | jsx-text | <h2>Figure p207.2</h2> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 81 | jsx-text | <p>Visual figure candidate from PDF page 207</p> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 82 | jsx-text | <p class="meta">PDF page 207 · visual_fallback</p> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 86 | quoted-string | <article class="card"> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 87 | jsx-text | <h2>Figure p207.3</h2> |
| data/output/Manual-de-Supravietuire/figures_hybrid/figures_hybrid.html | 88 | jsx-text | <p>Visual figure candidate from PDF page 207</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 4 | quoted-string | <meta charset="utf-8"> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 5 | quoted-string | <meta name="viewport" content="width=device-width, initial-scale=1"> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 6 | jsx-text | <title>Manualul de Instalatii - Instalatii electrice si de automatizare</title> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 9 | quoted-string | const saved = localStorage.getItem("voila-theme"); |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 10 | quoted-string | const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches; |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 11 | quoted-string | const theme = saved \\|\\| (prefersDark ? "dark" : "light"); |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 12 | quoted-string | document.documentElement.setAttribute("data-theme", theme); |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 35 | quoted-string | html[data-theme="dark"] { |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 64 | quoted-string | font-family: "Segoe UI", Arial, sans-serif; |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 69 | quoted-string | html[data-theme="dark"] body { |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 259 | quoted-string | <div class="theme-bar"> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 260 | jsx-text | <button class="theme-toggle" type="button" id="themeToggle">Toggle theme</button> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 264 | jsx-text | <h1>Manualul de Instalatii - Instalatii electrice si de automatizare</h1> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 265 | jsx-text | <p>Generated by Voila! v0.1.2</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 266 | jsx-text | <p>Mode: source language, no translation, no AI generation</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 267 | jsx-text | <p>Text status: OCR-cleaned reading text; original source preserved in pages.md/pages.json</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 268 | jsx-text | <p>Source: <code>D:\dev\projects\voila\data\input\Manualul Instalatiilor Electrice_20260509_132012.pdf</code></p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 269 | jsx-text | <h2>L001 — Partea li</h2> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 270 | jsx-text | <p>Source PDF pages: 3</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/course.cleaned.html | 271 | jsx-text | <p>Word count: 65</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 4 | quoted-string | <meta charset="utf-8"> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 5 | jsx-text | <title>Voila! Hybrid Figures</title> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 6 | quoted-string | <meta name="viewport" content="width=device-width, initial-scale=1"> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 22 | quoted-string | font-family: "Segoe UI", Arial, sans-serif; |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 82 | jsx-text | <h1>Voila! Hybrid Figure Extraction</h1> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 83 | jsx-text | <p>Source: <code>D:\dev\projects\voila\data\input\Manualul Instalatiilor Electrice_20260509_132012.pdf</code></p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 84 | jsx-text | <p>Page range: 1–480</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 85 | jsx-text | <p>Detected figures: 120</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 86 | quoted-string | <div class="grid"> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 88 | quoted-string | <article class="card"> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 89 | jsx-text | <h2>Figure 1.1.3</h2> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 90 | jsx-text | <p>Distribuţia intensităţ i i</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 91 | jsx-text | <p class="meta">PDF page 19 · fallback_caption_window</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 95 | quoted-string | <article class="card"> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 96 | jsx-text | <h2>Figure 1.1.4</h2> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 97 | jsx-text | <p>Reprezentarea intensităţii</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 98 | jsx-text | <p class="meta">PDF page 19 · fallback_caption_window</p> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 102 | quoted-string | <article class="card"> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 103 | jsx-text | <h2>Figure 1.1.2</h2> |
| data/output/Manualul Instalatiilor Electrice_20260509_132012/figures_hybrid/figures_hybrid.html | 104 | jsx-text | <p>Di stribuţ ia intensit ăţii</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 4 | quoted-string | <meta charset="utf-8"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 5 | quoted-string | <meta name="viewport" content="width=device-width, initial-scale=1"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 6 | jsx-text | <title>WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed</title> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 9 | quoted-string | const saved = localStorage.getItem("voila-theme"); |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 10 | quoted-string | const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches; |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 11 | quoted-string | const theme = saved \\|\\| (prefersDark ? "dark" : "light"); |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 12 | quoted-string | document.documentElement.setAttribute("data-theme", theme); |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 35 | quoted-string | html[data-theme="dark"] { |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 64 | quoted-string | font-family: "Segoe UI", Arial, sans-serif; |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 69 | quoted-string | html[data-theme="dark"] body { |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 259 | quoted-string | <div class="theme-bar"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 260 | jsx-text | <button class="theme-toggle" type="button" id="themeToggle">Toggle theme</button> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 264 | jsx-text | <h1>WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed</h1> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 265 | jsx-text | <p>Generated by Voila! v0.1.2</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 266 | jsx-text | <p>Mode: source language, no translation, no AI generation</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 267 | jsx-text | <p>Text status: OCR-cleaned reading text; original source preserved in pages.md/pages.json</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 268 | jsx-text | <p>Source: <code>D:\dev\projects\voila\data\input\WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed.pdf</code></p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 269 | jsx-text | <h2>L001 — Elsevier Butterworth-Heinemann</h2> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 270 | jsx-text | <p>Source PDF pages: 4</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/course.cleaned.html | 271 | jsx-text | <p>Word count: 105</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 4 | quoted-string | <meta charset="utf-8"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 5 | jsx-text | <title>Voila! Docling Lite Figures</title> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 6 | quoted-string | <meta name="viewport" content="width=device-width, initial-scale=1"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 23 | quoted-string | font-family: "Segoe UI", Arial, sans-serif; |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 89 | jsx-text | <h1>Voila! Docling Lite Figure Extraction</h1> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 90 | jsx-text | <p>Source: <code>D:\dev\projects\voila\data\input\WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed.pdf</code></p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 91 | jsx-text | <p>Page range: 35–75</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 92 | jsx-text | <p>Detected items: 6</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 93 | quoted-string | <div class="grid"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 95 | quoted-string | <article class="card"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 96 | jsx-text | <h2>Picture 1</h2> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 97 | jsx-text | <p>Figure 1.4 Typical Sankey diagrams</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 98 | jsx-text | <p class="meta">PDF page 36</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 102 | quoted-string | <article class="card"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 103 | jsx-text | <h2>Picture 2</h2> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 104 | jsx-text | <p>Figure 1.5 Four-stroke cycle</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 105 | jsx-text | <p class="meta">PDF page 39</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 109 | quoted-string | <article class="card"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 110 | jsx-text | <h2>Picture 3</h2> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_docling_lite/figures_docling_lite.html | 111 | jsx-text | <p>Figure 1.6 Two-stroke cycle</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 4 | quoted-string | <meta charset="utf-8"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 5 | jsx-text | <title>Voila! Hybrid Figures</title> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 6 | quoted-string | <meta name="viewport" content="width=device-width, initial-scale=1"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 22 | quoted-string | font-family: "Segoe UI", Arial, sans-serif; |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 82 | jsx-text | <h1>Voila! Hybrid Figure Extraction</h1> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 83 | jsx-text | <p>Source: <code>D:\dev\projects\voila\data\input\WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed.pdf</code></p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 84 | jsx-text | <p>Page range: 1–914</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 85 | jsx-text | <p>Detected figures: 120</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 86 | quoted-string | <div class="grid"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 88 | quoted-string | <article class="card"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 89 | jsx-text | <h2>Figure 1.1</h2> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 90 | jsx-text | <p>Theoretical heat cycle of true diesel engine</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 91 | jsx-text | <p class="meta">PDF page 31 · vector_drawing_merged</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 95 | quoted-string | <article class="card"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 96 | jsx-text | <h2>Figure 1.3</h2> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 97 | jsx-text | <p>The actual indicator diagram is derived from it by transposition</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 98 | jsx-text | <p class="meta">PDF page 33 · vector_drawing_merged</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 102 | quoted-string | <article class="card"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 103 | jsx-text | <h2>Figure 1.2</h2> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures_hybrid/figures_hybrid.html | 104 | jsx-text | <p>Typical indicator diagram (stroke based)</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 4 | quoted-string | <meta charset="utf-8"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 5 | jsx-text | <title>Voila! Vision Figures</title> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 6 | quoted-string | <meta name="viewport" content="width=device-width, initial-scale=1"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 22 | quoted-string | font-family: "Segoe UI", Arial, sans-serif; |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 82 | jsx-text | <h1>Voila! Vision Figure Crops</h1> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 83 | jsx-text | <p>Source: <code>D:\dev\projects\voila\data\input\WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed.pdf</code></p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 84 | jsx-text | <p>Detected figures: 60</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 85 | quoted-string | <div class="grid"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 87 | quoted-string | <article class="card"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 88 | jsx-text | <h2>Figure 1.1</h2> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 89 | jsx-text | <p>Theoretical heat cycle of true diesel engine</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 90 | jsx-text | <p class="meta">PDF page 31 · vision_candidate</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 94 | quoted-string | <article class="card"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 95 | jsx-text | <h2>Figure 1.3</h2> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 96 | jsx-text | <p>The actual indicator diagram is derived from it by transposition. This form of diagram is useful too when setting injection timing. If electronic indicators are used it is po... |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 97 | jsx-text | <p class="meta">PDF page 33 · vision_candidate</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 101 | quoted-string | <article class="card"> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 102 | jsx-text | <h2>Figure 1.2</h2> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 103 | jsx-text | <p>Typical indicator diagram (stroke based)</p> |
| data/output/WOODYARD_ D. F. _2004_. Pounder_s Marine Diesel Engines and Gas Turbines _8th ed/figures/figures.html | 104 | jsx-text | <p class="meta">PDF page 33 · vision_candidate</p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 4 | quoted-string | <meta charset="utf-8"> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 5 | quoted-string | <meta name="viewport" content="width=device-width, initial-scale=1"> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 6 | jsx-text | <title>Manualul Instalatiilor Electrice</title> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 9 | quoted-string | const saved = localStorage.getItem("voila-theme"); |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 10 | quoted-string | const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches; |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 11 | quoted-string | const theme = saved \\|\\| (prefersDark ? "dark" : "light"); |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 12 | quoted-string | document.documentElement.setAttribute("data-theme", theme); |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 35 | quoted-string | html[data-theme="dark"] { |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 64 | quoted-string | font-family: "Segoe UI", Arial, sans-serif; |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 69 | quoted-string | html[data-theme="dark"] body { |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 259 | quoted-string | <div class="theme-bar"> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 260 | jsx-text | <button class="theme-toggle" type="button" id="themeToggle">Toggle theme</button> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 264 | jsx-text | <h1>Manualul Instalatiilor Electrice</h1> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 265 | jsx-text | <p>Generated by Voila! OCR course builder.</p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 266 | jsx-text | <p>Mode: source language, OCR text, no AI generation.</p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 267 | jsx-text | <p>Text status: Tesseract OCR reading text; original scan preserved in source PDF.</p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 268 | jsx-text | <h2>L001 — Sisteme de iluminat ee = \\|</h2> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 269 | jsx-text | <p>Source PDF pages: 16, 17</p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 270 | jsx-text | <p>Word count: 2032</p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/course.cleaned.html | 271 | jsx-text | <h3>Cleaned source text</h3> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 4 | quoted-string | <meta charset="utf-8"> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 5 | jsx-text | <title>Voila! Visual Figure Extraction</title> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 11 | quoted-string | font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 64 | quoted-string | <div class="wrap"> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 65 | jsx-text | <h1>Voila! Visual Figure Extraction</h1> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 66 | jsx-text | <p>Source: <code>D:\dev\projects\voila\data\input\Manualul Instalatiilor Electrice.pdf</code></p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 67 | jsx-text | <p>Page range: 1–480</p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 68 | jsx-text | <p>Detected figures: 160</p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 70 | quoted-string | <div class="grid"> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 72 | quoted-string | <article class="card"> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 73 | jsx-text | <h2>Figure 1.1.2</h2> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 74 | jsx-text | <p>Distribuția intensității \\| Fig. 1.4 Reprezentarea intensității \\| ea Propune in tae vate</p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 75 | jsx-text | <p class="meta">PDF page 19 · visual_fallback</p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 79 | quoted-string | <article class="card"> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 80 | jsx-text | <h2>Figure 1.2.2</h2> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 81 | jsx-text | <p>indică structura simplificată a sistemului vizual şi carac teristicile sale. Organul vizual sesizează sarcina vizuală (SV) transmitând sem O © alul prin sistemul nervos la co... |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 82 | jsx-text | <p class="meta">PDF page 23 · visual_fallback</p> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 86 | quoted-string | <article class="card"> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 87 | jsx-text | <h2>Figure 1.2.5</h2> |
| data/trash/courses/Manualul Instalatiilor Electrice_20260509_132025/figures_hybrid/figures_hybrid.html | 88 | jsx-text | <p>Vai acuitatii vizuale (1/5)</p> |
| scripts/dev/add-course-tools-navigation.py | 3 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/add-course-tools-navigation.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-course-tools-navigation.py | 6 | quoted-string | if '@app.get("/course-tools")' not in text: |
| scripts/dev/add-course-tools-navigation.py | 16 | quoted-string | return PROJECT_ROOT / "data" / "output" / Path(pdf_name).stem |
| scripts/dev/add-course-tools-navigation.py | 33 | quoted-string | ("Tools", f"/course-tools?pdf={q}", "tools"), |
| scripts/dev/add-course-tools-navigation.py | 34 | quoted-string | ("Course", f"/view-course?pdf={q}", "course"), |
| scripts/dev/add-course-tools-navigation.py | 35 | quoted-string | ("Study", f"/study?pdf={q}", "study"), |
| scripts/dev/add-course-tools-navigation.py | 36 | quoted-string | ("Review OCR Text", f"/review-ocr-text?pdf={q}&page=1", "ocr"), |
| scripts/dev/add-course-tools-navigation.py | 37 | quoted-string | ("Review Concepts", f"/review-concepts?pdf={q}", "concepts"), |
| scripts/dev/add-course-tools-navigation.py | 38 | quoted-string | ("Figures", f"/view-figures?pdf={q}", "figures"), |
| scripts/dev/add-course-tools-navigation.py | 39 | quoted-string | ("Edit crops", f"/edit-crops?pdf={q}", "crops"), |
| scripts/dev/add-course-tools-navigation.py | 40 | quoted-string | ("Progress", f"/progress?pdf={q}", "progress"), |
| scripts/dev/add-course-tools-navigation.py | 41 | quoted-string | ("Library", "/", "library"), |
| scripts/dev/add-course-tools-navigation.py | 47 | quoted-string | cls = "active" if key == active else "" |
| scripts/dev/add-course-tools-navigation.py | 51 | quoted-string | <nav class="voila-tools-bar"> |
| scripts/dev/add-course-tools-navigation.py | 52 | quoted-string | """ + "\n ".join(items) + """ |
| scripts/dev/add-course-tools-navigation.py | 60 | quoted-string | if "voila-tools-bar" in html_doc: |
| scripts/dev/add-course-tools-navigation.py | 102 | quoted-string | if "</head>" in html_doc: |
| scripts/dev/add-course-tools-navigation.py | 103 | jsx-text | html_doc = html_doc.replace("</head>", css + "\n</head>", 1) |
| scripts/dev/add-course-tools-navigation.py | 106 | quoted-string | r"(<body[^>]*>)", |
| scripts/dev/add-document-language-endpoints.py | 3 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/add-document-language-endpoints.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-document-language-endpoints.py | 6 | quoted-string | if '@app.get("/document-language")' not in text: |
| scripts/dev/add-document-language-endpoints.py | 9 | quoted-string | @app.get("/document-language") |
| scripts/dev/add-document-language-endpoints.py | 19 | quoted-string | @app.post("/document-language") |
| scripts/dev/add-document-language-endpoints.py | 29 | quoted-string | pdf = str(payload.get("pdf") or "") |
| scripts/dev/add-document-language-endpoints.py | 30 | quoted-string | language = str(payload.get("language") or payload.get("document_language") or "auto") |
| scripts/dev/add-document-language-endpoints.py | 36 | quoted-string | text = text.rstrip() + "\n\n" + block + "\n" |
| scripts/dev/add-document-language-endpoints.py | 38 | quoted-string | path.write_text(text, encoding="utf-8") |
| scripts/dev/add-document-language-endpoints.py | 39 | quoted-string | print("OK: document-language endpoints added.") |
| scripts/dev/add-document-language-module.py | 3 | quoted-string | path = Path("services/api/document_language.py") |
| scripts/dev/add-document-language-module.py | 14 | quoted-string | "auto": { |
| scripts/dev/add-document-language-module.py | 15 | quoted-string | "label": "Auto detect", |
| scripts/dev/add-document-language-module.py | 16 | quoted-string | "ocr_lang": "eng", |
| scripts/dev/add-document-language-module.py | 17 | quoted-string | "languagetool_lang": "auto", |
| scripts/dev/add-document-language-module.py | 18 | quoted-string | "study_lang": "auto", |
| scripts/dev/add-document-language-module.py | 21 | quoted-string | "label": "Română", |
| scripts/dev/add-document-language-module.py | 22 | quoted-string | "ocr_lang": "ron+eng", |
| scripts/dev/add-document-language-module.py | 23 | quoted-string | "languagetool_lang": "ro-RO", |
| scripts/dev/add-document-language-module.py | 24 | quoted-string | "study_lang": "ro", |
| scripts/dev/add-document-language-module.py | 27 | quoted-string | "label": "English", |
| scripts/dev/add-document-language-module.py | 28 | quoted-string | "ocr_lang": "eng", |
| scripts/dev/add-document-language-module.py | 29 | quoted-string | "languagetool_lang": "en-US", |
| scripts/dev/add-document-language-module.py | 30 | quoted-string | "study_lang": "en", |
| scripts/dev/add-document-language-module.py | 33 | quoted-string | "label": "Français", |
| scripts/dev/add-document-language-module.py | 34 | quoted-string | "ocr_lang": "fra+eng", |
| scripts/dev/add-document-language-module.py | 35 | quoted-string | "languagetool_lang": "fr", |
| scripts/dev/add-document-language-module.py | 36 | quoted-string | "study_lang": "fr", |
| scripts/dev/add-document-language-module.py | 39 | quoted-string | "label": "Deutsch", |
| scripts/dev/add-document-language-module.py | 40 | quoted-string | "ocr_lang": "deu+eng", |
| scripts/dev/add-document-language-selector-css.py | 3 | quoted-string | path = Path("services/api/static/ocr_review_monaco.css") |
| scripts/dev/add-document-language-selector-css.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-document-language-selector-css.py | 6 | quoted-string | if "#voilaDocumentLanguage" not in text: |
| scripts/dev/add-document-language-selector-css.py | 20 | quoted-string | path.write_text(text, encoding="utf-8") |
| scripts/dev/add-document-language-selector-css.py | 21 | quoted-string | print("OK: language selector CSS added.") |
| scripts/dev/add-it-es-pt-document-languages.py | 3 | quoted-string | path = Path("services/api/document_language.py") |
| scripts/dev/add-it-es-pt-document-languages.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-it-es-pt-document-languages.py | 8 | quoted-string | "label": "Русский", |
| scripts/dev/add-it-es-pt-document-languages.py | 9 | quoted-string | "ocr_lang": "rus+eng", |
| scripts/dev/add-it-es-pt-document-languages.py | 10 | quoted-string | "languagetool_lang": "ru-RU", |
| scripts/dev/add-it-es-pt-document-languages.py | 11 | quoted-string | "study_lang": "ru", |
| scripts/dev/add-it-es-pt-document-languages.py | 16 | quoted-string | "label": "Русский", |
| scripts/dev/add-it-es-pt-document-languages.py | 17 | quoted-string | "ocr_lang": "rus+eng", |
| scripts/dev/add-it-es-pt-document-languages.py | 18 | quoted-string | "languagetool_lang": "ru-RU", |
| scripts/dev/add-it-es-pt-document-languages.py | 19 | quoted-string | "study_lang": "ru", |
| scripts/dev/add-it-es-pt-document-languages.py | 22 | quoted-string | "label": "Italiano", |
| scripts/dev/add-it-es-pt-document-languages.py | 23 | quoted-string | "ocr_lang": "ita+eng", |
| scripts/dev/add-it-es-pt-document-languages.py | 24 | quoted-string | "languagetool_lang": "it", |
| scripts/dev/add-it-es-pt-document-languages.py | 25 | quoted-string | "study_lang": "it", |
| scripts/dev/add-it-es-pt-document-languages.py | 28 | quoted-string | "label": "Español", |
| scripts/dev/add-it-es-pt-document-languages.py | 29 | quoted-string | "ocr_lang": "spa+eng", |
| scripts/dev/add-it-es-pt-document-languages.py | 30 | quoted-string | "languagetool_lang": "es", |
| scripts/dev/add-it-es-pt-document-languages.py | 31 | quoted-string | "study_lang": "es", |
| scripts/dev/add-it-es-pt-document-languages.py | 34 | quoted-string | "label": "Português", |
| scripts/dev/add-it-es-pt-document-languages.py | 35 | quoted-string | "ocr_lang": "por+eng", |
| scripts/dev/add-it-es-pt-monaco-languages.py | 3 | quoted-string | path = Path("services/api/static/ocr_review_monaco.js") |
| scripts/dev/add-it-es-pt-monaco-languages.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-it-es-pt-monaco-languages.py | 8 | quoted-string | ''' de: "Deutsch", |
| scripts/dev/add-it-es-pt-monaco-languages.py | 9 | quoted-string | ru: "Русский" |
| scripts/dev/add-it-es-pt-monaco-languages.py | 11 | quoted-string | ''' de: "Deutsch", |
| scripts/dev/add-it-es-pt-monaco-languages.py | 12 | quoted-string | ru: "Русский", |
| scripts/dev/add-it-es-pt-monaco-languages.py | 13 | quoted-string | it: "Italiano", |
| scripts/dev/add-it-es-pt-monaco-languages.py | 14 | quoted-string | es: "Español", |
| scripts/dev/add-it-es-pt-monaco-languages.py | 15 | quoted-string | pt: "Português" |
| scripts/dev/add-it-es-pt-monaco-languages.py | 21 | quoted-string | ''' de: "de-DE", |
| scripts/dev/add-it-es-pt-monaco-languages.py | 22 | quoted-string | ru: "ru-RU" |
| scripts/dev/add-it-es-pt-monaco-languages.py | 24 | quoted-string | ''' de: "de-DE", |
| scripts/dev/add-it-es-pt-monaco-languages.py | 25 | quoted-string | ru: "ru-RU", |
| scripts/dev/add-it-es-pt-monaco-languages.py | 41 | quoted-string | if "scores.it += 3" not in text: |
| scripts/dev/add-it-es-pt-monaco-languages.py | 53 | quoted-string | old = ''' de: ["und", "mit", "der", "die", "das", "abbildung", "kapitel", "druck", "temperatur", "system"] |
| scripts/dev/add-it-es-pt-monaco-languages.py | 56 | quoted-string | new = ''' de: ["und", "mit", "der", "die", "das", "abbildung", "kapitel", "druck", "temperatur", "system"], |
| scripts/dev/add-it-es-pt-monaco-languages.py | 57 | quoted-string | it: ["per", "con", "della", "delle", "figura", "capitolo", "pressione", "temperatura", "sistema"], |
| scripts/dev/add-it-es-pt-monaco-languages.py | 58 | quoted-string | es: ["para", "con", "del", "de la", "figura", "capítulo", "presión", "temperatura", "sistema"], |
| scripts/dev/add-it-es-pt-monaco-languages.py | 59 | quoted-string | pt: ["para", "com", "do", "da", "figura", "capítulo", "pressão", "temperatura", "sistema"] |
| scripts/dev/add-it-es-pt-monaco-languages.py | 62 | quoted-string | if 'it: ["per"' not in text: |
| scripts/dev/add-lesson-tools-module.py | 3 | quoted-string | path = Path("services/api/lesson_tools.py") |
| scripts/dev/add-lesson-tools-module.py | 17 | quoted-string | source = question.get("source") or {} |
| scripts/dev/add-lesson-tools-module.py | 25 | quoted-string | _safe_str(question.get("lesson_id")) |
| scripts/dev/add-lesson-tools-module.py | 26 | quoted-string | or _safe_str(source.get("lesson_id")) |
| scripts/dev/add-lesson-tools-module.py | 27 | quoted-string | or _safe_str(question.get("concept_id")) |
| scripts/dev/add-lesson-tools-module.py | 28 | quoted-string | or _safe_str(source.get("concept_id")) |
| scripts/dev/add-lesson-tools-module.py | 29 | quoted-string | or "lesson" |
| scripts/dev/add-lesson-tools-module.py | 37 | quoted-string | _safe_str(source.get("concept_title")) |
| scripts/dev/add-lesson-tools-module.py | 38 | quoted-string | or _safe_str(source.get("lesson_title")) |
| scripts/dev/add-lesson-tools-module.py | 39 | quoted-string | or _safe_str(source.get("title")) |
| scripts/dev/add-lesson-tools-module.py | 40 | quoted-string | or _safe_str(question.get("concept_title")) |
| scripts/dev/add-lesson-tools-module.py | 41 | quoted-string | or _safe_str(question.get("lesson_title")) |
| scripts/dev/add-lesson-tools-module.py | 50 | quoted-string | source.get("source_pdf_pages") |
| scripts/dev/add-lesson-tools-module.py | 51 | quoted-string | or source.get("pages") |
| scripts/dev/add-lesson-tools-module.py | 52 | quoted-string | or question.get("source_pdf_pages") |
| scripts/dev/add-lesson-tools-module.py | 53 | quoted-string | or question.get("pages") |
| scripts/dev/add-lesson-tools-module.py | 75 | quoted-string | _safe_str(source.get("source_text")) |
| scripts/dev/add-lesson-tools-module.py | 76 | quoted-string | or _safe_str(source.get("text")) |
| scripts/dev/add-lesson-tools-module.py | 77 | quoted-string | or _safe_str(question.get("source_text")) |
| scripts/dev/add-lesson-tools-module.py | 78 | quoted-string | or _safe_str(question.get("answer")) |
| scripts/dev/add-lessons-i18n-keys.py | 3 | quoted-string | path = Path("services/api/i18n.py") |
| scripts/dev/add-lessons-i18n-keys.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-lessons-i18n-keys.py | 6 | quoted-string | marker = "# VOILA_LESSONS_I18N_EXTENSIONS_V1" |
| scripts/dev/add-lessons-i18n-keys.py | 15 | quoted-string | "lessons": "Lecții", |
| scripts/dev/add-lessons-i18n-keys.py | 16 | quoted-string | "lesson": "Lecție", |
| scripts/dev/add-lessons-i18n-keys.py | 17 | quoted-string | "open_lesson": "Deschide lecția", |
| scripts/dev/add-lessons-i18n-keys.py | 18 | quoted-string | "study_lesson": "Studiază lecția", |
| scripts/dev/add-lessons-i18n-keys.py | 19 | quoted-string | "read_lesson": "Citește lecția", |
| scripts/dev/add-lessons-i18n-keys.py | 20 | quoted-string | "general_study": "Studiu general", |
| scripts/dev/add-lessons-i18n-keys.py | 21 | quoted-string | "open_course": "Deschide cursul", |
| scripts/dev/add-lessons-i18n-keys.py | 22 | quoted-string | "library": "Bibliotecă", |
| scripts/dev/add-lessons-i18n-keys.py | 23 | quoted-string | "lessons_found": "Lecții găsite", |
| scripts/dev/add-lessons-i18n-keys.py | 24 | quoted-string | "no_lessons": "Nu există lecții disponibile", |
| scripts/dev/add-lessons-i18n-keys.py | 25 | quoted-string | "generate_course_first_short": "Generează mai întâi cursul / quiz-ul pentru acest PDF.", |
| scripts/dev/add-lessons-i18n-keys.py | 26 | quoted-string | "lesson_not_found": "Lecție negăsită", |
| scripts/dev/add-lessons-i18n-keys.py | 27 | quoted-string | "back_to_lessons": "Înapoi la lecții", |
| scripts/dev/add-lessons-i18n-keys.py | 28 | quoted-string | "no_source_text_for_lesson": "Nu există text sursă disponibil pentru această lecție.", |
| scripts/dev/add-lessons-i18n-keys.py | 29 | quoted-string | "no_questions_for_lesson": "Nu există întrebări pentru lecția selectată.", |
| scripts/dev/add-lessons-i18n-keys.py | 30 | quoted-string | "pages": "Pagini", |
| scripts/dev/add-lessons-i18n-keys.py | 33 | quoted-string | "lessons": "Lessons", |
| scripts/dev/add-lessons-routes.py | 3 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/add-lessons-routes.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-lessons-routes.py | 6 | quoted-string | if '@app.get("/lessons"' not in text: |
| scripts/dev/add-lessons-routes.py | 11 | quoted-string | @app.get("/lessons", response_class=HTMLResponse) |
| scripts/dev/add-lessons-routes.py | 26 | quoted-string | lesson_id = str(lesson.get("lesson_id") or "") |
| scripts/dev/add-lessons-routes.py | 27 | quoted-string | title = str(lesson.get("title") or lesson_id) |
| scripts/dev/add-lessons-routes.py | 28 | quoted-string | pages = ", ".join(str(p) for p in lesson.get("pages") or []) or "-" |
| scripts/dev/add-lessons-routes.py | 29 | quoted-string | preview = str(lesson.get("preview") or "") |
| scripts/dev/add-lessons-routes.py | 30 | quoted-string | questions_count = int(lesson.get("questions_count") or 0) |
| scripts/dev/add-lessons-routes.py | 33 | quoted-string | <article class="card"> |
| scripts/dev/add-lessons-routes.py | 34 | jsx-text | <div class="meta">#{index} · ID: <code>{html.escape(lesson_id)}</code> · {_ut("questions", "Questions")}: <strong>{questions_count}</strong> · Pages: <strong>{html.escape(pages)... |
| scripts/dev/add-lessons-routes.py | 37 | quoted-string | <div class="actions"> |
| scripts/dev/add-lessons-routes.py | 44 | quoted-string | content = "\n".join(rows) if rows else """ |
| scripts/dev/add-lessons-routes.py | 45 | quoted-string | <article class="card"> |
| scripts/dev/add-lessons-routes.py | 46 | jsx-text | <h2>Nu există lecții disponibile</h2> |
| scripts/dev/add-lessons-routes.py | 47 | jsx-text | <p>Generează mai întâi cursul / quiz-ul pentru acest PDF.</p> |
| scripts/dev/add-lessons-routes.py | 52 | jsx-text | <h1>Lecții</h1> |
| scripts/dev/add-lessons-routes.py | 54 | quoted-string | <div class="notice"> |
| scripts/dev/add-lessons-routes.py | 59 | quoted-string | <div class="actions"> |
| scripts/dev/add-lessons-routes.py | 66 | quoted-string | <div class="grid"> |
| scripts/dev/add-lessons-to-course-tools.py | 3 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/add-lessons-to-course-tools.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-lessons-to-course-tools.py | 7 | quoted-string | if '("Lessons", f"/lessons?pdf={q}", "lessons")' not in text: |
| scripts/dev/add-lessons-to-course-tools.py | 9 | quoted-string | ''' ("Course", f"/view-course?pdf={q}", "course"), |
| scripts/dev/add-lessons-to-course-tools.py | 10 | quoted-string | ("Study", f"/study?pdf={q}", "study"), |
| scripts/dev/add-lessons-to-course-tools.py | 12 | quoted-string | ''' ("Course", f"/view-course?pdf={q}", "course"), |
| scripts/dev/add-lessons-to-course-tools.py | 13 | quoted-string | ("Lessons", f"/lessons?pdf={q}", "lessons"), |
| scripts/dev/add-lessons-to-course-tools.py | 14 | quoted-string | ("Study", f"/study?pdf={q}", "study"), |
| scripts/dev/add-lessons-to-course-tools.py | 19 | quoted-string | if 'card("Lessons"' not in text: |
| scripts/dev/add-lessons-to-course-tools.py | 21 | quoted-string | ''' card("Open course", "Read the generated course with navigation.", f"/view-course?pdf={q}", checks["course"]), |
| scripts/dev/add-lessons-to-course-tools.py | 22 | quoted-string | card("Study mode", "Practice questions generated from the course.", f"/study?pdf={q}", checks["study"]), |
| scripts/dev/add-lessons-to-course-tools.py | 24 | quoted-string | ''' card("Open course", "Read the generated course with navigation.", f"/view-course?pdf={q}", checks["course"]), |
| scripts/dev/add-lessons-to-course-tools.py | 25 | quoted-string | card("Lessons", "Choose a lesson, read it, then study only that lesson.", f"/lessons?pdf={q}", checks["study"]), |
| scripts/dev/add-lessons-to-course-tools.py | 26 | quoted-string | card("Study mode", "Practice questions generated from the course.", f"/study?pdf={q}", checks["study"]), |
| scripts/dev/add-lessons-to-course-tools.py | 30 | quoted-string | path.write_text(text, encoding="utf-8") |
| scripts/dev/add-lessons-to-course-tools.py | 31 | quoted-string | print("OK: Course Tools includes Lessons link/card.") |
| scripts/dev/add-ocr-best-text-fallback-module.py | 5 | quoted-string | path = Path("services/api/ocr_best_text.py") |
| scripts/dev/add-ocr-best-text-fallback-module.py | 16 | quoted-string | "ocr_corrections.json", |
| scripts/dev/add-ocr-best-text-fallback-module.py | 17 | quoted-string | "ocr_pages.manual.json", |
| scripts/dev/add-ocr-best-text-fallback-module.py | 18 | quoted-string | "ocr_pages.post_clean.json", |
| scripts/dev/add-ocr-best-text-fallback-module.py | 19 | quoted-string | "ocr_tsv_columns_pages.post_clean.json", |
| scripts/dev/add-ocr-best-text-fallback-module.py | 20 | quoted-string | "ocr_body_columns_pages.post_clean.json", |
| scripts/dev/add-ocr-best-text-fallback-module.py | 21 | quoted-string | "ocr_pages.json", |
| scripts/dev/add-ocr-best-text-fallback-module.py | 22 | quoted-string | "ocr_tsv_columns_pages.json", |
| scripts/dev/add-ocr-best-text-fallback-module.py | 23 | quoted-string | "ocr_body_columns_pages.json", |
| scripts/dev/add-ocr-best-text-fallback-module.py | 29 | quoted-string | return json.loads(path.read_text(encoding="utf-8", errors="replace")) |
| scripts/dev/add-ocr-best-text-fallback-module.py | 45 | quoted-string | # Shape: {"pages": [{"page_number": 3, "text": "..."}]} |
| scripts/dev/add-ocr-best-text-fallback-module.py | 46 | quoted-string | if isinstance(data, dict) and isinstance(data.get("pages"), list): |
| scripts/dev/add-ocr-best-text-fallback-module.py | 47 | quoted-string | for item in data["pages"]: |
| scripts/dev/add-ocr-best-text-fallback-module.py | 52 | quoted-string | item.get("page_number") |
| scripts/dev/add-ocr-best-text-fallback-module.py | 53 | quoted-string | or item.get("page") |
| scripts/dev/add-ocr-best-text-fallback-module.py | 54 | quoted-string | or item.get("page_index") |
| scripts/dev/add-ocr-best-text-fallback-module.py | 61 | quoted-string | if "page_index" in item and "page_number" not in item and page >= 0: |
| scripts/dev/add-ocr-best-text-fallback-module.py | 66 | quoted-string | item.get("text") |
| scripts/dev/add-ocr-best-text-fallback-module.py | 67 | quoted-string | or item.get("corrected_text") |
| scripts/dev/add-ocr-best-text-fallback-module.py | 68 | quoted-string | or item.get("body") |
| scripts/dev/add-ocr-correction-workflow.py | 3 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/add-ocr-correction-workflow.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-ocr-correction-workflow.py | 6 | quoted-string | marker = "# VOILA_OCR_CORRECTION_ROUTES_V1" |
| scripts/dev/add-ocr-correction-workflow.py | 9 | quoted-string | print("OK: OCR correction routes already exist.") |
| scripts/dev/add-ocr-correction-workflow.py | 26 | quoted-string | return PROJECT_ROOT / "data" / "output" / Path(_voila_safe_pdf_name(pdf)).stem |
| scripts/dev/add-ocr-correction-workflow.py | 32 | quoted-string | pdf_path = PROJECT_ROOT / "data" / "input" / _voila_safe_pdf_name(pdf) |
| scripts/dev/add-ocr-correction-workflow.py | 45 | quoted-string | @app.get("/ocr-page-image") |
| scripts/dev/add-ocr-correction-workflow.py | 50 | quoted-string | pdf_path = PROJECT_ROOT / "data" / "input" / safe_pdf |
| scripts/dev/add-ocr-correction-workflow.py | 53 | quoted-string | return _VoilaResponse("PDF not found", status_code=404) |
| scripts/dev/add-ocr-correction-workflow.py | 66 | quoted-string | png = pix.tobytes("png") |
| scripts/dev/add-ocr-correction-workflow.py | 70 | quoted-string | return _VoilaResponse(content=png, media_type="image/png") |
| scripts/dev/add-ocr-correction-workflow.py | 73 | quoted-string | @app.get("/review-ocr-corrected") |
| scripts/dev/add-ocr-correction-workflow.py | 89 | quoted-string | item = corr_data.get("page_corrections", {}).get(str(page_number), {}) |
| scripts/dev/add-ocr-correction-workflow.py | 90 | quoted-string | status = item.get("status") if isinstance(item, dict) else "" |
| scripts/dev/add-ocr-correction-workflow.py | 99 | jsx-text | saved_msg = '<div class="notice ok">Saved correction.</div>' |
| scripts/dev/add-ocr-correction-workflow.py | 103 | jsx-text | applied_msg = '<div class="notice ok">Applied corrected OCR to pages.json / ocr_pages.json.</div>' |
| scripts/dev/add-ocr-correction-workflow.py | 282 | quoted-string | <meta charset="utf-8"> |
| scripts/dev/add-ocr-correction-workflow.py | 283 | jsx-text | <title>Correct OCR · Voila!</title> |
| scripts/dev/add-ocr-correction-workflow.py | 289 | jsx-text | <h1>Correct OCR Text</h1> |
| scripts/dev/add-ocr-correction-workflow.py | 290 | quoted-string | <div class="muted">{html.escape(safe_pdf)} · page {page_number} / {page_count} · status: {html.escape(str(status or "not reviewed"))}</div> |
| scripts/dev/add-ocr-text-autocomplete.py | 4 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/add-ocr-text-autocomplete.py | 5 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-ocr-text-autocomplete.py | 8 | quoted-string | if '@app.get("/review-ocr-text/suggestions")' not in text: |
| scripts/dev/add-ocr-text-autocomplete.py | 11 | quoted-string | @app.get("/review-ocr-text/suggestions") |
| scripts/dev/add-ocr-text-autocomplete.py | 12 | quoted-string | def review_ocr_text_suggestions(pdf: str = "", q: str = "", limit: int = 12): |
| scripts/dev/add-ocr-text-autocomplete.py | 20 | quoted-string | return JSONResponse({"suggestions": []}) |
| scripts/dev/add-ocr-text-autocomplete.py | 28 | quoted-string | return JSONResponse({"suggestions": []}) |
| scripts/dev/add-ocr-text-autocomplete.py | 31 | quoted-string | "instalații", "electrice", "automatizare", "iluminat", "tensiune", |
| scripts/dev/add-ocr-text-autocomplete.py | 32 | quoted-string | "curent", "putere", "energie", "circuit", "circuite", "protecție", |
| scripts/dev/add-ocr-text-autocomplete.py | 33 | quoted-string | "alimentare", "distribuție", "comandă", "măsurare", "reglare", |
| scripts/dev/add-ocr-text-autocomplete.py | 34 | quoted-string | "control", "siguranță", "conductoare", "conductor", "echipamente", |
| scripts/dev/add-ocr-text-autocomplete.py | 35 | quoted-string | "tablouri", "aparate", "relee", "contactoare", "senzori", |
| scripts/dev/add-ocr-text-autocomplete.py | 36 | quoted-string | "rezistență", "impedanță", "frecvență", "factor", "defazaj", |
| scripts/dev/add-ocr-text-autocomplete.py | 37 | quoted-string | "luminos", "luminanță", "iluminare", "randament", "transformator", |
| scripts/dev/add-ocr-text-autocomplete.py | 38 | quoted-string | "motor", "monofazat", "trifazat", "împământare", "legare", |
| scripts/dev/add-ocr-text-autocomplete.py | 39 | quoted-string | "scurtcircuit", "suprasarcină", "declanșare", "automat", |
| scripts/dev/add-ocr-text-autocomplete.py | 40 | quoted-string | "automată", "sisteme", "scheme", "tehnologice", "principiu", |
| scripts/dev/add-ocr-text-autocomplete.py | 41 | quoted-string | "regulatoare", "traductoare", "ventilare", "climatizare", |
| scripts/dev/add-ocr-text-autocomplete.py | 42 | quoted-string | "temperatură", "presiune", "umiditate", "debit", "mărimi", |
| scripts/dev/add-ocr-text-autocomplete.py | 43 | quoted-string | "documentație", "obiective", "investiții", "publice", "tehnico", |
| scripts/dev/add-quick-tools-route.py | 3 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/add-quick-tools-route.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-quick-tools-route.py | 6 | quoted-string | if '@app.get("/quick-tools")' not in text: |
| scripts/dev/add-quick-tools-route.py | 9 | quoted-string | @app.get("/quick-tools") |
| scripts/dev/add-quick-tools-route.py | 14 | quoted-string | input_dir = PROJECT_ROOT / "data" / "input" |
| scripts/dev/add-quick-tools-route.py | 15 | quoted-string | output_dir = PROJECT_ROOT / "data" / "output" |
| scripts/dev/add-quick-tools-route.py | 17 | quoted-string | pdfs = sorted(input_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True) |
| scripts/dev/add-quick-tools-route.py | 26 | quoted-string | "course": (out / "course.cleaned.html").exists(), |
| scripts/dev/add-quick-tools-route.py | 27 | quoted-string | "study": (out / "quiz.study.json").exists(), |
| scripts/dev/add-quick-tools-route.py | 28 | quoted-string | "figures": (out / "figures_hybrid" / "figures_hybrid.html").exists(), |
| scripts/dev/add-quick-tools-route.py | 29 | quoted-string | "ocr": (out / "ocr_pages.json").exists() or (out / "pages.json").exists(), |
| scripts/dev/add-quick-tools-route.py | 34 | quoted-string | status.append(f"<span class='{key if ok else 'missing'}'>{key}: {'OK' if ok else '-'}</span>") |
| scripts/dev/add-quick-tools-route.py | 37 | quoted-string | <section class="card"> |
| scripts/dev/add-quick-tools-route.py | 40 | quoted-string | <div class="actions"> |
| scripts/dev/add-quick-tools-route.py | 54 | quoted-string | <meta charset="utf-8"> |
| scripts/dev/add-quick-tools-route.py | 55 | jsx-text | <title>Quick Tools · Voila!</title> |
| scripts/dev/add-quick-tools-route.py | 147 | quoted-string | <div class="wrap"> |
| scripts/dev/add-quick-tools-route.py | 148 | quoted-string | <div class="top"> |
| scripts/dev/add-quick-tools-route.py | 149 | jsx-text | <h1>Quick Tools</h1> |
| scripts/dev/add-quick-tools-route.py | 152 | jsx-text | {''.join(cards) if cards else '<p>No PDFs found.</p>'} |
| scripts/dev/add-review-concepts-ui.py | 3 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/add-review-concepts-ui.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-review-concepts-ui.py | 6 | quoted-string | if '@app.get("/review-concepts")' not in text: |
| scripts/dev/add-review-concepts-ui.py | 15 | quoted-string | return PROJECT_ROOT / "data" / "output" / Path(safe_name).stem |
| scripts/dev/add-review-concepts-ui.py | 23 | quoted-string | return json.loads(path.read_text(encoding="utf-8")) |
| scripts/dev/add-review-concepts-ui.py | 32 | quoted-string | encoding="utf-8", |
| scripts/dev/add-review-concepts-ui.py | 51 | quoted-string | letters = len(re.findall(r"[A-Za-zĂÂÎȘȚăâîșț]", title)) |
| scripts/dev/add-review-concepts-ui.py | 57 | quoted-string | if re.search(r"\b(jj\\|ixii\\|v0\\|01g\\|lll\\|iiii\\|xii!)\b", lower): |
| scripts/dev/add-review-concepts-ui.py | 60 | quoted-string | if re.search(r"[^\w\săâîșțĂÂÎȘȚ.,:;()/-]", title): |
| scripts/dev/add-review-concepts-ui.py | 63 | quoted-string | if len(re.findall(r"[A-Za-zĂÂÎȘȚăâîșț]{3,}", title)) < 1: |
| scripts/dev/add-review-concepts-ui.py | 69 | quoted-string | @app.get("/review-concepts") |
| scripts/dev/add-review-concepts-ui.py | 76 | jsx-text | return HTMLResponse("<h1>Missing PDF name</h1>", status_code=400) |
| scripts/dev/add-review-concepts-ui.py | 79 | quoted-string | quiz_path = output_dir / "quiz.study.json" |
| scripts/dev/add-review-concepts-ui.py | 80 | quoted-string | overrides_path = output_dir / "study_concept_overrides.json" |
| scripts/dev/add-review-concepts-ui.py | 82 | quoted-string | quiz = _load_json_file(quiz_path, {"questions": []}) |
| scripts/dev/add-review-concepts-ui.py | 83 | quoted-string | overrides = _load_json_file(overrides_path, {"overrides": {}}).get("overrides", {}) |
| scripts/dev/add-review-concepts-ui.py | 87 | quoted-string | for question in quiz.get("questions", []): |
| scripts/dev/add-review-concepts-ui.py | 88 | quoted-string | lesson_id = question.get("lesson_id") or "" |
| scripts/dev/add-review-concepts-ui.py | 89 | quoted-string | concept_title = question.get("concept_title") or question.get("lesson_title") or "" |
| scripts/dev/add-review-concepts-ui.py | 96 | quoted-string | "lesson_id": lesson_id, |
| scripts/dev/add-review-ocr-floating-zoom.py | 4 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/add-review-ocr-floating-zoom.py | 5 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-review-ocr-floating-zoom.py | 7 | quoted-string | start = text.find('@app.get("/review-ocr-text")') |
| scripts/dev/add-review-ocr-floating-zoom.py | 8 | quoted-string | end = text.find('@app.post("/review-ocr-text/save")', start) |
| scripts/dev/add-review-ocr-floating-zoom.py | 11 | quoted-string | raise SystemExit("Could not find review OCR text route.") |
| scripts/dev/add-review-ocr-floating-zoom.py | 18 | jsx-text | else '<div class="no-img">No rendered page image found for this page.</div>' |
| scripts/dev/add-review-ocr-floating-zoom.py | 24 | quoted-string | <div class="scan-shell"> |
| scripts/dev/add-review-ocr-floating-zoom.py | 25 | quoted-string | <div class="scan-toolbar"> |
| scripts/dev/add-review-ocr-floating-zoom.py | 26 | quoted-string | <button type="button" onclick="zoomScan(-0.15)">−</button> |
| scripts/dev/add-review-ocr-floating-zoom.py | 27 | quoted-string | <button type="button" onclick="resetScanZoom()">100%</button> |
| scripts/dev/add-review-ocr-floating-zoom.py | 28 | jsx-text | <button type="button" onclick="fitScanWidth()">Fit width</button> |
| scripts/dev/add-review-ocr-floating-zoom.py | 29 | quoted-string | <button type="button" onclick="zoomScan(0.15)">+</button> |
| scripts/dev/add-review-ocr-floating-zoom.py | 30 | quoted-string | <span class="zoom-pill" data-zoom-label>100%</span> |
| scripts/dev/add-review-ocr-floating-zoom.py | 33 | quoted-string | <div class="scan-viewport" id="scanViewport"> |
| scripts/dev/add-review-ocr-floating-zoom.py | 37 | quoted-string | <div class="scan-floating-zoom"> |
| scripts/dev/add-review-ocr-floating-zoom.py | 38 | quoted-string | <button type="button" onclick="zoomScan(-0.15)">−</button> |
| scripts/dev/add-review-ocr-floating-zoom.py | 39 | quoted-string | <button type="button" onclick="resetScanZoom()">100%</button> |
| scripts/dev/add-review-ocr-floating-zoom.py | 40 | jsx-text | <button type="button" onclick="fitScanWidth()">Fit</button> |
| scripts/dev/add-review-ocr-floating-zoom.py | 41 | quoted-string | <button type="button" onclick="zoomScan(0.15)">+</button> |
| scripts/dev/add-review-ocr-floating-zoom.py | 42 | quoted-string | <span class="zoom-pill" data-zoom-label>100%</span> |
| scripts/dev/add-review-ocr-text-ui.py | 4 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/add-review-ocr-text-ui.py | 5 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-review-ocr-text-ui.py | 9 | quoted-string | r"from fastapi import ([^\n]+)", |
| scripts/dev/add-review-ocr-text-ui.py | 11 | quoted-string | "from fastapi import " |
| scripts/dev/add-review-ocr-text-ui.py | 14 | quoted-string | [part.strip() for part in m.group(1).split(",")] + ["Form"] |
| scripts/dev/add-review-ocr-text-ui.py | 22 | quoted-string | if '@app.get("/review-ocr-text")' not in text: |
| scripts/dev/add-review-ocr-text-ui.py | 27 | quoted-string | output_dir / "ocr_pages.json", |
| scripts/dev/add-review-ocr-text-ui.py | 28 | quoted-string | output_dir / "pages.json", |
| scripts/dev/add-review-ocr-text-ui.py | 38 | quoted-string | pages = data.get("pages") or data.get("items") or [] |
| scripts/dev/add-review-ocr-text-ui.py | 50 | quoted-string | page_number = int(page.get("page_number") or page.get("pdf_page") or idx) |
| scripts/dev/add-review-ocr-text-ui.py | 51 | quoted-string | page_text = str(page.get("text") or page.get("content") or "") |
| scripts/dev/add-review-ocr-text-ui.py | 55 | quoted-string | "page_number": page_number, |
| scripts/dev/add-review-ocr-text-ui.py | 56 | quoted-string | "text": page_text, |
| scripts/dev/add-review-ocr-text-ui.py | 68 | quoted-string | "version": "voila_ocr_text_review_v1", |
| scripts/dev/add-review-ocr-text-ui.py | 69 | quoted-string | "text_source": "manual_reviewed_ocr", |
| scripts/dev/add-review-ocr-text-ui.py | 70 | quoted-string | "pages": pages, |
| scripts/dev/add-review-ocr-text-ui.py | 73 | quoted-string | for target_name in ["ocr_pages.json", "pages.json"]: |
| scripts/dev/add-review-ocr-text-ui.py | 77 | quoted-string | backup = output_dir / f"{target_name}.before_text_review.json" |
| scripts/dev/add-review-ocr-text-ui.py | 80 | quoted-string | backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8") |
| scripts/dev/add-review-ocr-text-ui.py | 85 | quoted-string | f"# Reviewed OCR pages for {output_dir.name}", |
| scripts/dev/add-run-ocr-page-button-monaco.py | 3 | quoted-string | path = Path("services/api/static/ocr_review_monaco.js") |
| scripts/dev/add-run-ocr-page-button-monaco.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-run-ocr-page-button-monaco.py | 6 | quoted-string | if 'runOcrPageButton' not in text: |
| scripts/dev/add-run-ocr-page-button-monaco.py | 8 | quoted-string | ''' const checkButton = document.createElement("button"); |
| scripts/dev/add-run-ocr-page-button-monaco.py | 9 | quoted-string | checkButton.type = "button"; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 10 | quoted-string | checkButton.id = "checkOcrButton"; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 11 | quoted-string | checkButton.textContent = "Verifică text"; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 12 | quoted-string | checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor."; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 14 | quoted-string | ''' const runOcrPageButton = document.createElement("button"); |
| scripts/dev/add-run-ocr-page-button-monaco.py | 15 | quoted-string | runOcrPageButton.type = "button"; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 16 | quoted-string | runOcrPageButton.id = "runOcrPageButton"; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 17 | quoted-string | runOcrPageButton.className = "voila-primary"; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 18 | quoted-string | runOcrPageButton.textContent = "Rulează OCR pagină"; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 19 | quoted-string | runOcrPageButton.title = "Generează OCR pentru pagina curentă, dacă textul este gol sau incomplet."; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 21 | quoted-string | const checkButton = document.createElement("button"); |
| scripts/dev/add-run-ocr-page-button-monaco.py | 22 | quoted-string | checkButton.type = "button"; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 23 | quoted-string | checkButton.id = "checkOcrButton"; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 24 | quoted-string | checkButton.textContent = "Verifică text"; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 25 | quoted-string | checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor."; |
| scripts/dev/add-run-ocr-page-button-monaco.py | 42 | quoted-string | ''' checkButton.addEventListener("click", async function () { |
| scripts/dev/add-run-ocr-page-endpoint.py | 4 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/add-run-ocr-page-endpoint.py | 5 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/add-run-ocr-page-endpoint.py | 7 | quoted-string | if '@app.post("/run-ocr-page")' not in text: |
| scripts/dev/add-run-ocr-page-endpoint.py | 10 | quoted-string | @app.post("/run-ocr-page") |
| scripts/dev/add-run-ocr-page-endpoint.py | 21 | quoted-string | pdf = str(payload.get("pdf") or "").strip() |
| scripts/dev/add-run-ocr-page-endpoint.py | 22 | quoted-string | page = int(payload.get("page") or 1) |
| scripts/dev/add-run-ocr-page-endpoint.py | 23 | quoted-string | psm = int(payload.get("psm") or 6) |
| scripts/dev/add-run-ocr-page-endpoint.py | 24 | quoted-string | zoom = float(payload.get("zoom") or 3.0) |
| scripts/dev/add-run-ocr-page-endpoint.py | 30 | quoted-string | "message": "PDF lipsă.", |
| scripts/dev/add-run-ocr-page-endpoint.py | 35 | quoted-string | script = PROJECT_ROOT / "scripts" / "dev" / "run-ocr-page.py" |
| scripts/dev/add-run-ocr-page-endpoint.py | 41 | quoted-string | "message": f"Nu găsesc scriptul OCR: {script}", |
| scripts/dev/add-run-ocr-page-endpoint.py | 49 | quoted-string | "--pdf", |
| scripts/dev/add-run-ocr-page-endpoint.py | 51 | quoted-string | "--page", |
| scripts/dev/add-run-ocr-page-endpoint.py | 53 | quoted-string | "--lang", |
| scripts/dev/add-run-ocr-page-endpoint.py | 54 | quoted-string | "auto", |
| scripts/dev/add-run-ocr-page-endpoint.py | 55 | quoted-string | "--psm", |
| scripts/dev/add-run-ocr-page-endpoint.py | 57 | quoted-string | "--zoom", |
| scripts/dev/add-run-ocr-page-endpoint.py | 66 | quoted-string | encoding="utf-8", |
| scripts/dev/add-run-ocr-page-endpoint.py | 67 | quoted-string | errors="replace", |
| scripts/dev/add-run-ocr-page-endpoint.py | 75 | quoted-string | "message": "OCR a durat prea mult și a fost oprit.", |
| scripts/dev/add-study-questions-builder.py | 3 | quoted-string | path = Path("services/api/study_questions.py") |
| scripts/dev/add-study-questions-builder.py | 13 | quoted-string | "ro": "Ce idee importantă susține sursa despre „{concept}”?", |
| scripts/dev/add-study-questions-builder.py | 14 | quoted-string | "en": "What important idea does the source support about “{concept}”?", |
| scripts/dev/add-study-questions-builder.py | 15 | quoted-string | "fr": "Quelle idée importante la source soutient-elle à propos de « {concept} » ?", |
| scripts/dev/add-study-questions-builder.py | 16 | quoted-string | "de": "Welche wichtige Idee unterstützt die Quelle zu „{concept}“?", |
| scripts/dev/add-study-questions-builder.py | 17 | quoted-string | "ru": "Какую важную идею источник поддерживает относительно «{concept}»?", |
| scripts/dev/add-study-questions-builder.py | 18 | quoted-string | "it": "Quale idea importante sostiene la fonte su “{concept}”?", |
| scripts/dev/add-study-questions-builder.py | 19 | quoted-string | "es": "¿Qué idea importante sostiene la fuente sobre «{concept}»?", |
| scripts/dev/add-study-questions-builder.py | 20 | quoted-string | "pt": "Que ideia importante a fonte sustenta sobre “{concept}”?", |
| scripts/dev/add-study-questions-builder.py | 25 | quoted-string | r"^What technical point does the source state about\s+(.+?)\??$", |
| scripts/dev/add-study-questions-builder.py | 26 | quoted-string | r"^Under what condition or operating situation does the source describe\s+(.+?)\??$", |
| scripts/dev/add-study-questions-builder.py | 27 | quoted-string | r"^Name one key point supported by the source text in\s+['\"“”‘’](.+?)['\"“”‘’]\.?$", |
| scripts/dev/add-study-questions-builder.py | 28 | quoted-string | r"^Name one key point supported by the source text in\s+(.+?)\.?$", |
| scripts/dev/add-study-questions-builder.py | 29 | quoted-string | r"^What does the source state about\s+(.+?)\??$", |
| scripts/dev/add-study-questions-builder.py | 30 | quoted-string | r"^What does the text say about\s+(.+?)\??$", |
| scripts/dev/add-study-questions-builder.py | 31 | quoted-string | r"^What is stated about\s+(.+?)\??$", |
| scripts/dev/add-study-questions-builder.py | 32 | quoted-string | r"^What is the source saying about\s+(.+?)\??$", |
| scripts/dev/add-study-questions-builder.py | 44 | quoted-string | raw_question = str(question.get("question") or question.get("prompt") or "").strip() |
| scripts/dev/add-study-questions-builder.py | 55 | quoted-string | "concept_title", |
| scripts/dev/add-study-questions-builder.py | 56 | quoted-string | "lesson_title", |
| scripts/dev/create-monaco-ocr-static-assets.py | 4 | quoted-string | static_dir = root / "services" / "api" / "static" |
| scripts/dev/create-monaco-ocr-static-assets.py | 7 | quoted-string | (static_dir / "ocr_review_monaco.css").write_text(r''' |
| scripts/dev/create-monaco-ocr-static-assets.py | 47 | quoted-string | ''', encoding="utf-8") |
| scripts/dev/create-monaco-ocr-static-assets.py | 49 | quoted-string | (static_dir / "ocr_review_monaco.js").write_text(r''' |
| scripts/dev/create-monaco-ocr-static-assets.py | 55 | quoted-string | const script = document.createElement("script"); |
| scripts/dev/create-monaco-ocr-static-assets.py | 64 | quoted-string | if (document.readyState === "loading") { |
| scripts/dev/create-monaco-ocr-static-assets.py | 65 | quoted-string | document.addEventListener("DOMContentLoaded", fn); |
| scripts/dev/create-monaco-ocr-static-assets.py | 72 | quoted-string | const textarea = document.getElementById("ocrText"); |
| scripts/dev/create-monaco-ocr-static-assets.py | 75 | quoted-string | const form = textarea.closest("form"); |
| scripts/dev/create-monaco-ocr-static-assets.py | 76 | quoted-string | const actions = form ? form.querySelector(".actions") : null; |
| scripts/dev/create-monaco-ocr-static-assets.py | 78 | quoted-string | const host = document.createElement("div"); |
| scripts/dev/create-monaco-ocr-static-assets.py | 79 | quoted-string | host.id = "voilaMonacoEditor"; |
| scripts/dev/create-monaco-ocr-static-assets.py | 81 | quoted-string | const status = document.createElement("div"); |
| scripts/dev/create-monaco-ocr-static-assets.py | 82 | quoted-string | status.id = "voilaMonacoStatus"; |
| scripts/dev/create-monaco-ocr-static-assets.py | 83 | jsx-text | status.innerHTML = "<strong>Editor:</strong> se încarcă Monaco..."; |
| scripts/dev/create-monaco-ocr-static-assets.py | 85 | quoted-string | textarea.classList.add("voila-monaco-hidden"); |
| scripts/dev/create-monaco-ocr-static-assets.py | 86 | quoted-string | textarea.insertAdjacentElement("afterend", host); |
| scripts/dev/create-monaco-ocr-static-assets.py | 87 | quoted-string | host.insertAdjacentElement("afterend", status); |
| scripts/dev/create-monaco-ocr-static-assets.py | 94 | quoted-string | textarea.classList.remove("voila-monaco-hidden"); |
| scripts/dev/create-monaco-ocr-static-assets.py | 95 | quoted-string | host.style.display = "none"; |
| scripts/dev/debug-tesseract-tsv-page41.py | 8 | quoted-string | pdf = project / "data" / "input" / "Manualul Instalatiilor Electrice.pdf" |
| scripts/dev/debug-tesseract-tsv-page41.py | 9 | quoted-string | out_dir = project / "data" / "output" / "Manualul Instalatiilor Electrice" / "_debug_tsv" |
| scripts/dev/debug-tesseract-tsv-page41.py | 12 | quoted-string | tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe" |
| scripts/dev/debug-tesseract-tsv-page41.py | 13 | quoted-string | tessdata = project / ".tessdata" |
| scripts/dev/debug-tesseract-tsv-page41.py | 17 | quoted-string | env["TESSDATA_PREFIX"] = str(tessdata) |
| scripts/dev/debug-tesseract-tsv-page41.py | 23 | quoted-string | png = out_dir / "page_041_zoom_2_8.png" |
| scripts/dev/debug-tesseract-tsv-page41.py | 26 | quoted-string | print("PNG:", png) |
| scripts/dev/debug-tesseract-tsv-page41.py | 27 | quoted-string | print("PNG exists:", png.exists(), "size:", png.stat().st_size if png.exists() else 0) |
| scripts/dev/debug-tesseract-tsv-page41.py | 30 | quoted-string | print("=== Tesseract version ===") |
| scripts/dev/debug-tesseract-tsv-page41.py | 32 | quoted-string | [tesseract, "--version"], |
| scripts/dev/debug-tesseract-tsv-page41.py | 34 | quoted-string | encoding="utf-8", |
| scripts/dev/debug-tesseract-tsv-page41.py | 35 | quoted-string | errors="replace", |
| scripts/dev/debug-tesseract-tsv-page41.py | 38 | quoted-string | print("returncode:", r.returncode) |
| scripts/dev/debug-tesseract-tsv-page41.py | 42 | quoted-string | print("=== Tesseract langs ===") |
| scripts/dev/debug-tesseract-tsv-page41.py | 44 | quoted-string | [tesseract, "--list-langs"], |
| scripts/dev/debug-tesseract-tsv-page41.py | 46 | quoted-string | encoding="utf-8", |
| scripts/dev/debug-tesseract-tsv-page41.py | 47 | quoted-string | errors="replace", |
| scripts/dev/debug-tesseract-tsv-page41.py | 51 | quoted-string | print("returncode:", r.returncode) |
| scripts/dev/debug-tesseract-tsv-page41.py | 55 | quoted-string | ("stdout_tsv", [tesseract, str(png), "stdout", "-l", "ron+eng", "--psm", "6", "tsv"]), |
| scripts/dev/debug-tesseract-tsv-page41.py | 56 | quoted-string | ("file_tsv", [tesseract, str(png), str(out_dir / "ocr_file"), "-l", "ron+eng", "--psm", "6", "tsv"]), |
| scripts/dev/fix-body-columns-ocr-fallback.py | 4 | quoted-string | path = Path("services/api/ocr_body_columns_tesseract_pages.py") |
| scripts/dev/fix-body-columns-ocr-fallback.py | 5 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/fix-body-columns-ocr-fallback.py | 8 | quoted-string | if "def run_tesseract_text(" not in text: |
| scripts/dev/fix-body-columns-ocr-fallback.py | 9 | quoted-string | marker = "\ndef parse_tsv_lines(tsv: str) -> list[dict]:" |
| scripts/dev/fix-body-columns-ocr-fallback.py | 22 | quoted-string | env["TESSDATA_PREFIX"] = tessdata_prefix |
| scripts/dev/fix-body-columns-ocr-fallback.py | 27 | quoted-string | image_path = Path(tmp) / "crop.png" |
| scripts/dev/fix-body-columns-ocr-fallback.py | 33 | quoted-string | "stdout", |
| scripts/dev/fix-body-columns-ocr-fallback.py | 36 | quoted-string | "--psm", |
| scripts/dev/fix-body-columns-ocr-fallback.py | 43 | quoted-string | encoding="utf-8", |
| scripts/dev/fix-body-columns-ocr-fallback.py | 44 | quoted-string | errors="replace", |
| scripts/dev/fix-body-columns-ocr-fallback.py | 49 | quoted-string | return (result.stdout or "").replace("\f", "").strip(), time.time() - start, result.returncode |
| scripts/dev/fix-body-columns-ocr-fallback.py | 55 | quoted-string | if "def plain_text_to_body_text(" not in text: |
| scripts/dev/fix-body-columns-ocr-fallback.py | 56 | quoted-string | marker = "\ndef ocr_image_text(" |
| scripts/dev/fix-body-columns-ocr-fallback.py | 70 | quoted-string | if re.match(r"^[\\\|\-—–_.,;:()\[\]{}<>/\\0-9\s%°]+$", value): |
| scripts/dev/fix-body-columns-ocr-fallback.py | 73 | quoted-string | letters = len(re.findall(rf"[{RO_LETTERS}]", value)) |
| scripts/dev/fix-body-columns-ocr-fallback.py | 84 | jsx-text | if digits > letters * 2 and letters < 20: |
| scripts/dev/fix-body-columns-ocr-fallback.py | 87 | quoted-string | if re.search(r"\b(y[o0]\\|wey\\|fOr\\|isu\\|vv\\|sns\\|fires)\b", lower): |
| scripts/dev/fix-body-columns-ocr-fallback.py | 111 | quoted-string | or re.match(r"^\s*[0-9a-z]\s*[-–]", lower) |
| scripts/dev/fix-body-columns-ocr-fallback.py | 112 | quoted-string | or re.match(r"^\s*[0-9]+\s*[-–]", lower) |
| scripts/dev/fix-body-columns-ocr-fallback.py | 113 | quoted-string | or re.search(r"\b(balonul\\|filamentul\\|electrodul\\|suportul\\|soclu\\|tubul\\|intrare curent\\|înveliș)\b", lower) |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 3 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 65 | quoted-string | "Tip: Ctrl + mouse wheel zoom, drag with mouse to pan", |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 66 | quoted-string | "Tip: Ctrl + mouse wheel = zoom doar pe imagine; click + drag = mută pagina" |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 69 | quoted-string | old = """ const box = document.getElementById('scanWrap'); |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 76 | quoted-string | box.addEventListener('mousedown', (e) => {{ |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 84 | quoted-string | box.addEventListener('mouseleave', () => {{ isDown = false; }}); |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 85 | quoted-string | box.addEventListener('mouseup', () => {{ isDown = false; }}); |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 87 | quoted-string | box.addEventListener('mousemove', (e) => {{ |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 96 | quoted-string | new = """ const box = document.getElementById('scanWrap'); |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 97 | quoted-string | const img = box.querySelector('img'); |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 108 | quoted-string | img.style.setProperty('--scan-zoom', scanZoom + '%'); |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 113 | quoted-string | box.addEventListener('wheel', (e) => {{ |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 131 | quoted-string | box.addEventListener('mousedown', (e) => {{ |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 139 | quoted-string | box.addEventListener('mouseleave', () => {{ isDown = false; }}); |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 140 | quoted-string | box.addEventListener('mouseup', () => {{ isDown = false; }}); |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 142 | quoted-string | box.addEventListener('mousemove', (e) => {{ |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 152 | quoted-string | raise SystemExit("Could not find scan JS block to replace.") |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 156 | quoted-string | path.write_text(text, encoding="utf-8") |
| scripts/dev/fix-corrected-ocr-image-only-zoom.py | 157 | quoted-string | print("OK: corrected OCR review zoom is now image-only and layout-stable.") |
| scripts/dev/fix-crop-editor-missing-path.py | 4 | quoted-string | path = Path("services/api/crop_editor_app.py") |
| scripts/dev/fix-crop-editor-missing-path.py | 5 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/fix-crop-editor-missing-path.py | 10 | quoted-string | raw_path = item.get("path") |
| scripts/dev/fix-crop-editor-missing-path.py | 15 | quoted-string | rel = item.get("relative_path") |
| scripts/dev/fix-crop-editor-missing-path.py | 18 | quoted-string | output_path = OUTPUT_DIR / pdf.stem / "figures_hybrid" / rel |
| scripts/dev/fix-crop-editor-missing-path.py | 19 | quoted-string | item["path"] = str(output_path) |
| scripts/dev/fix-crop-editor-missing-path.py | 22 | quoted-string | raise KeyError("Figure item has neither 'path' nor 'relative_path'.") |
| scripts/dev/fix-crop-editor-missing-path.py | 25 | quoted-string | if "def item_output_path" not in text: |
| scripts/dev/fix-crop-editor-missing-path.py | 27 | quoted-string | "def clamp_rect(rect: list[float], page: fitz.Page) -> list[float]:", |
| scripts/dev/fix-crop-editor-missing-path.py | 28 | quoted-string | helper + "\n\ndef clamp_rect(rect: list[float], page: fitz.Page) -> list[float]:", |
| scripts/dev/fix-crop-editor-missing-path.py | 33 | quoted-string | ''' output_path = Path(item["path"]) |
| scripts/dev/fix-crop-editor-missing-path.py | 43 | quoted-string | ''' mtime = Path(item["path"]).stat().st_mtime if Path(item["path"]).exists() else time.time() |
| scripts/dev/fix-crop-editor-missing-path.py | 52 | quoted-string | ''' return json.loads(manifest_path.read_text(encoding="utf-8")) |
| scripts/dev/fix-crop-editor-missing-path.py | 54 | quoted-string | ''' manifest = json.loads(manifest_path.read_text(encoding="utf-8")) |
| scripts/dev/fix-crop-editor-missing-path.py | 56 | quoted-string | for item in manifest.get("figure_crops", []): |
| scripts/dev/fix-crop-editor-missing-path.py | 57 | quoted-string | if "path" not in item and item.get("relative_path"): |
| scripts/dev/fix-crop-editor-missing-path.py | 58 | quoted-string | item["path"] = str(OUTPUT_DIR / pdf.stem / "figures_hybrid" / item["relative_path"]) |
| scripts/dev/fix-crop-editor-missing-path.py | 64 | quoted-string | path.write_text(text, encoding="utf-8") |
| scripts/dev/fix-crop-editor-missing-path.py | 66 | quoted-string | print("OK: crop_editor_app.py now supports manifests without item['path'].") |
| scripts/dev/fix-edit-crops-route.py | 4 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/fix-edit-crops-route.py | 5 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/fix-edit-crops-route.py | 30 | quoted-string | "uvicorn", |
| scripts/dev/fix-edit-crops-route.py | 31 | quoted-string | "crop_editor_app:app", |
| scripts/dev/fix-edit-crops-route.py | 32 | quoted-string | "--app-dir", |
| scripts/dev/fix-edit-crops-route.py | 33 | quoted-string | str(PROJECT_ROOT / "services" / "api"), |
| scripts/dev/fix-edit-crops-route.py | 34 | quoted-string | "--host", |
| scripts/dev/fix-edit-crops-route.py | 36 | quoted-string | "--port", |
| scripts/dev/fix-edit-crops-route.py | 38 | quoted-string | "--log-level", |
| scripts/dev/fix-edit-crops-route.py | 39 | quoted-string | "info", |
| scripts/dev/fix-edit-crops-route.py | 52 | quoted-string | start = text.find("def ensure_crop_editor_running()") |
| scripts/dev/fix-edit-crops-route.py | 55 | quoted-string | previous = text.rfind("\ndef crop_editor_is_running()", 0, start) |
| scripts/dev/fix-edit-crops-route.py | 59 | quoted-string | end = text.find("\n\napp = FastAPI(", start) |
| scripts/dev/fix-edit-crops-route.py | 61 | quoted-string | raise SystemExit("Could not find end of crop editor helper block.") |
| scripts/dev/fix-edit-crops-route.py | 63 | quoted-string | text = text[:start] + new_block + "\n\n" + text[end + 2:] |
| scripts/dev/fix-edit-crops-route.py | 65 | quoted-string | marker = "app = FastAPI(" |
| scripts/dev/fix-edit-crops-route.py | 68 | quoted-string | raise SystemExit("Could not find FastAPI marker.") |
| scripts/dev/fix-edit-crops-route.py | 69 | quoted-string | text = text[:pos] + new_block + "\n\n" + text[pos:] |
| scripts/dev/fix-edit-crops-route.py | 73 | quoted-string | @app.get("/edit-crops") |
| scripts/dev/fix-edit-crops-route.py | 83 | jsx-text | <h1>Crop Editor did not start</h1> |
| scripts/dev/fix-floating-nav-fstring.py | 3 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/fix-floating-nav-fstring.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/fix-floating-nav-fstring.py | 45 | quoted-string | start = text.find(" .floating-nav {") |
| scripts/dev/fix-floating-nav-fstring.py | 47 | quoted-string | start = text.find(" .floating-nav {{") |
| scripts/dev/fix-floating-nav-fstring.py | 50 | quoted-string | end = text.find(" </style>", start) |
| scripts/dev/fix-floating-nav-fstring.py | 52 | quoted-string | raise SystemExit("Could not find </style> after floating nav CSS.") |
| scripts/dev/fix-floating-nav-fstring.py | 57 | quoted-string | "window.scrollTo({ top: 0, behavior: 'smooth' })", |
| scripts/dev/fix-floating-nav-fstring.py | 58 | quoted-string | "window.scrollTo({{ top: 0, behavior: 'smooth' }})" |
| scripts/dev/fix-floating-nav-fstring.py | 62 | quoted-string | "window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })", |
| scripts/dev/fix-floating-nav-fstring.py | 63 | quoted-string | "window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }})" |
| scripts/dev/fix-floating-nav-fstring.py | 66 | quoted-string | path.write_text(text, encoding="utf-8") |
| scripts/dev/fix-floating-nav-fstring.py | 68 | quoted-string | print("OK: floating nav braces fixed for Python f-string.") |
| scripts/dev/fix-home-fixed-nav.py | 3 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/fix-home-fixed-nav.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/fix-home-fixed-nav.py | 13 | quoted-string | if ".app-fixed-nav[hidden]" not in text: |
| scripts/dev/fix-home-fixed-nav.py | 14 | quoted-string | text = text.replace(" .app-fixed-nav [hidden] {{", css_fix + "\n .app-fixed-nav [hidden] {{", 1) |
| scripts/dev/fix-home-fixed-nav.py | 17 | quoted-string | old_start = text.find('<script id="hide-fixed-nav-on-home">') |
| scripts/dev/fix-home-fixed-nav.py | 19 | quoted-string | old_end = text.find("</script>", old_start) |
| scripts/dev/fix-home-fixed-nav.py | 21 | quoted-string | old_end += len("</script>") |
| scripts/dev/fix-home-fixed-nav.py | 25 | quoted-string | <script id="hide-fixed-nav-on-home"> |
| scripts/dev/fix-home-fixed-nav.py | 29 | quoted-string | const nav = document.getElementById("appFixedNav"); |
| scripts/dev/fix-home-fixed-nav.py | 31 | quoted-string | if ((path === "/" \\|\\| path === "") && nav) {{ |
| scripts/dev/fix-home-fixed-nav.py | 39 | quoted-string | if (document.readyState === "loading") {{ |
| scripts/dev/fix-home-fixed-nav.py | 40 | quoted-string | document.addEventListener("DOMContentLoaded", hideHomeNav); |
| scripts/dev/fix-home-fixed-nav.py | 48 | jsx-text | text = text.replace("</body>", script + "\n</body>", 1) |
| scripts/dev/fix-home-fixed-nav.py | 50 | quoted-string | path.write_text(text, encoding="utf-8") |
| scripts/dev/fix-home-fixed-nav.py | 52 | quoted-string | print("OK: fixed nav is now fully removed on Home page.") |
| scripts/dev/fix-homepage-primary-tool-css.py | 4 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/fix-homepage-primary-tool-css.py | 5 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/fix-homepage-primary-tool-css.py | 7 | quoted-string | page_start = text.find("def page(") |
| scripts/dev/fix-homepage-primary-tool-css.py | 8 | quoted-string | page_end = text.find("\n\ndef ", page_start + 1) |
| scripts/dev/fix-homepage-primary-tool-css.py | 11 | quoted-string | raise SystemExit("Could not find page() function.") |
| scripts/dev/fix-homepage-primary-tool-css.py | 53 | quoted-string | print("No bad primary-tool CSS block found inside page(). Nothing replaced.") |
| scripts/dev/fix-homepage-primary-tool-css.py | 55 | quoted-string | print(f"Replaced bad primary-tool CSS block: {count}") |
| scripts/dev/fix-homepage-primary-tool-css.py | 59 | quoted-string | path.write_text(text, encoding="utf-8") |
| scripts/dev/fix-homepage-primary-tool-css.py | 60 | quoted-string | print("OK: homepage CSS braces fixed.") |
| scripts/dev/fix-languagetool-auto-language.py | 3 | quoted-string | path = Path("services/api/static/ocr_review_monaco.js") |
| scripts/dev/fix-languagetool-auto-language.py | 4 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/fix-languagetool-auto-language.py | 7 | quoted-string | if "function detectVoilaOcrLanguage" not in text: |
| scripts/dev/fix-languagetool-auto-language.py | 19 | quoted-string | "pentru", "este", "sunt", "care", "prin", "în", "din", "funcție", |
| scripts/dev/fix-languagetool-auto-language.py | 20 | quoted-string | "tensiune", "curent", "lămpii", "instalații", "capitolul", "figura" |
| scripts/dev/fix-languagetool-auto-language.py | 24 | quoted-string | "the", "and", "with", "from", "figure", "chapter", "valve", |
| scripts/dev/fix-languagetool-auto-language.py | 25 | quoted-string | "engine", "fuel", "injection", "pressure", "temperature", "system" |
| scripts/dev/fix-languagetool-auto-language.py | 39 | quoted-string | if (enScore > roScore) return "en-US"; |
| scripts/dev/fix-languagetool-auto-language.py | 40 | quoted-string | return "ro-RO"; |
| scripts/dev/fix-languagetool-auto-language.py | 45 | quoted-string | raise SystemExit("Nu găsesc locul pentru detectVoilaOcrLanguage.") |
| scripts/dev/fix-languagetool-auto-language.py | 51 | quoted-string | ''' language: "ro-RO"''', |
| scripts/dev/fix-languagetool-auto-language.py | 52 | quoted-string | ''' language: detectVoilaOcrLanguage(textarea.value \\|\\| "")''' |
| scripts/dev/fix-languagetool-auto-language.py | 57 | jsx-text | ''' setStatus("<strong>LanguageTool:</strong> verific textul...");''', |
| scripts/dev/fix-languagetool-auto-language.py | 58 | quoted-string | ''' const detectedLanguage = detectVoilaOcrLanguage(textarea.value \\|\\| ""); |
| scripts/dev/fix-languagetool-auto-language.py | 59 | jsx-text | setStatus("<strong>LanguageTool:</strong> verific textul cu limba " + detectedLanguage + "...");''' |
| scripts/dev/fix-languagetool-auto-language.py | 64 | quoted-string | ''' language: detectVoilaOcrLanguage(textarea.value \\|\\| "")''', |
| scripts/dev/fix-languagetool-auto-language.py | 65 | quoted-string | ''' language: detectedLanguage''' |
| scripts/dev/fix-languagetool-auto-language.py | 68 | quoted-string | path.write_text(text, encoding="utf-8") |
| scripts/dev/fix-languagetool-auto-language.py | 69 | quoted-string | print("OK: Monaco LanguageTool now auto-detects ro-RO / en-US per manual text.") |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 4 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 5 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 7 | quoted-string | pattern = r'\n@app\.post\("/check-ocr-languagetool"\)[\s\S]*?(?=\n@app\.\\|\Z)' |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 11 | quoted-string | @app.post("/check-ocr-languagetool") |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 23 | quoted-string | text=str(payload.get("text") or ""), |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 24 | quoted-string | language=str(payload.get("language") or "ro-RO"), |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 29 | quoted-string | "provider": "LanguageTool", |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 30 | quoted-string | "matches": [], |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 31 | quoted-string | "message": "Eroare internă la verificarea LanguageTool.", |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 32 | quoted-string | "error": str(exc), |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 41 | quoted-string | raise SystemExit("Nu am găsit endpoint-ul /check-ocr-languagetool de înlocuit.") |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 43 | quoted-string | path.write_text(text, encoding="utf-8") |
| scripts/dev/fix-languagetool-endpoint-json-safe.py | 44 | quoted-string | print("OK: LanguageTool endpoint made self-contained and JSON-safe.") |
| scripts/dev/fix-languagetool-request-annotation.py | 4 | quoted-string | path = Path("services/api/web_app.py") |
| scripts/dev/fix-languagetool-request-annotation.py | 5 | quoted-string | text = path.read_text(encoding="utf-8") |
| scripts/dev/fix-languagetool-request-annotation.py | 7 | quoted-string | pattern = r'\n@app\.post\("/check-ocr-languagetool"\)[\s\S]*?(?=\n@app\.\\|\Z)' |
| scripts/dev/fix-languagetool-request-annotation.py | 11 | quoted-string | @app.post("/check-ocr-languagetool") |
| scripts/dev/fix-languagetool-request-annotation.py | 23 | quoted-string | text=str(payload.get("text") or ""), |
| scripts/dev/fix-languagetool-request-annotation.py | 24 | quoted-string | language=str(payload.get("language") or "ro-RO"), |
| scripts/dev/fix-languagetool-request-annotation.py | 29 | quoted-string | "provider": "LanguageTool", |
| scripts/dev/fix-languagetool-request-annotation.py | 30 | quoted-string | "matches": [], |
| scripts/dev/fix-languagetool-request-annotation.py | 31 | quoted-string | "message": "Eroare internă la verificarea LanguageTool.", |
| scripts/dev/fix-languagetool-request-annotation.py | 32 | quoted-string | "error": str(exc), |
| scripts/dev/fix-languagetool-request-annotation.py | 41 | quoted-string | raise SystemExit("Nu am găsit endpoint-ul /check-ocr-languagetool de înlocuit.") |
| scripts/dev/fix-languagetool-request-annotation.py | 43 | quoted-string | path.write_text(text, encoding="utf-8") |
| scripts/dev/fix-languagetool-request-annotation.py | 44 | quoted-string | print("OK: LanguageTool endpoint fixed with Request annotation.") |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 3 | quoted-string | js_path = Path("services/api/static/ocr_review_monaco.js") |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 4 | quoted-string | js = js_path.read_text(encoding="utf-8") |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 8 | quoted-string | ''' lightbulb: { enabled: true },''', |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 9 | quoted-string | ''' lightbulb: { enabled: false },''' |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 13 | quoted-string | ''' lightbulb: { enabled: true }''', |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 14 | quoted-string | ''' lightbulb: { enabled: false }''' |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 18 | quoted-string | if 'voilaOcrColumns' not in js: |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 22 | quoted-string | const runOcrPageButton = document.createElement("button"); |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 26 | quoted-string | const ocrColumnsSelect = document.createElement("select"); |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 27 | quoted-string | ocrColumnsSelect.id = "voilaOcrColumns"; |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 28 | quoted-string | ocrColumnsSelect.title = "Mod OCR pentru pagina curentă"; |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 31 | quoted-string | ["0", "OCR normal"], |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 32 | quoted-string | ["2", "OCR 2 coloane"], |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 33 | quoted-string | ["3", "OCR 3 coloane"] |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 35 | quoted-string | const option = document.createElement("option"); |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 43 | quoted-string | const runOcrPageButton = document.createElement("button"); |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 66 | quoted-string | if 'voilaLtPanel' not in js: |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 68 | quoted-string | ''' const status = document.createElement("div"); |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 69 | quoted-string | status.id = "voilaMonacoStatus"; |
| scripts/dev/fix-lt-panel-and-ocr-columns-ui.py | 70 | jsx-text | status.innerHTML = "<strong>Editor:</strong> se încarcă Monaco..."; |
| scripts/dev/fix-monaco-robust-textarea-toolbar.py | 3 | quoted-string | static_dir = Path("services/api/static") |
| scripts/dev/fix-monaco-robust-textarea-toolbar.py | 6 | quoted-string | (static_dir / "ocr_review_monaco.css").write_text(r''' |
| scripts/dev/fix-monaco-robust-textarea-toolbar.py | 57 | quoted-string | ''', encoding="utf-8") |
| scripts/dev/fix-monaco-robust-textarea-toolbar.py | 59 | quoted-string | (static_dir / "ocr_review_monaco.js").write_text(r''' |
| scripts/dev/fix-monaco-robust-textarea-toolbar.py | 65 | quoted-string | if (document.readyState === "loading") { |
| scripts/dev/fix-monaco-robust-textarea-toolbar.py | 66 | quoted-string | document.addEventListener("DOMContentLoaded", fn); |
| scripts/dev/fix-monaco-robust-textarea-toolbar.py | 76 | quoted-string | const script = document.createElement("script"); |
| scripts/dev/fix-monaco-robust-textarea-toolbar.py | 86 | quoted-string | document.getElementById("ocrText") \\|\\| |
| scripts/dev/fix-monaco-robust-textarea-toolbar.py | 87 | quoted-string | document.querySelector('textarea[name="text"]') \\|\\| |

## Review checklist

Before runtime localization, review each candidate and classify it as:

- user-facing text
- developer-only text
- log/debug text
- configuration value
- import/module path
- false positive

## Recommended next milestone

v0.2.6-public-beta-language-pack-schema

Suggested next work:

- define translation key naming rules
- define JSON schema for language packs
- create sample ro/en language pack files
- add validation script
- keep runtime unchanged until schema and samples are reviewed

## Decision for this milestone

For v0.2.5-public-beta-language-pack-inventory, the correct action is to commit this compact inventory document only.

No application runtime files should be modified.
