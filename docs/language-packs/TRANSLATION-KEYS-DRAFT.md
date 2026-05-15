# Voila! Translation Keys Draft

Milestone: v0.2.9-public-beta-language-pack-review  
Status: draft key list / documentation only  
Scope: no runtime changes

## Goal

This document defines a first draft of stable translation keys for future Voila! language packs.

The list is intentionally small and conservative.

It should be expanded only after reviewing actual user-facing strings from the application.

## Key status legend

| Status | Meaning |
|---|---|
| draft | proposed key, not final |
| sample | already represented in sample packs |
| needs-review | likely useful, but wording/key may change |
| later | useful later, not needed for initial runtime integration |
| possible-pro | candidate for future paid/pro packs, not public core now |

## ui keys

| Key | Status | Purpose |
|---|---|---|
| app.title | sample | Application name |
| app.subtitle | sample | Short application subtitle |
| button.start | sample | Start action |
| button.cancel | sample | Cancel action |
| button.save | sample | Save action |
| button.export | sample | Export action |
| button.import | needs-review | Import action |
| button.open | needs-review | Open action |
| button.close | needs-review | Close action |
| button.retry | needs-review | Retry action |
| button.back | needs-review | Back navigation |
| button.next | needs-review | Next navigation |
| button.previous | needs-review | Previous navigation |
| nav.home | sample | Home navigation |
| nav.settings | sample | Settings navigation |
| nav.documents | needs-review | Documents navigation |
| nav.lessons | needs-review | Lessons navigation |
| nav.export | needs-review | Export navigation |
| status.ready | sample | Ready state |
| status.processing | sample | Processing state |
| status.loading | needs-review | Loading state |
| status.completed | needs-review | Completed state |
| status.failed | needs-review | Failed state |

## messages keys

| Key | Status | Purpose |
|---|---|---|
| message.saved | sample | Generic save confirmation |
| message.export_complete | sample | Export completed message |
| message.file_loaded | sample | File loaded confirmation |
| message.import_complete | needs-review | Import completed message |
| message.processing_started | needs-review | Processing started message |
| message.processing_complete | needs-review | Processing completed message |
| warning.unsaved_changes | sample | Unsaved changes warning |
| warning.large_file | needs-review | Large file warning |
| warning.incomplete_content | needs-review | Incomplete content warning |
| error.file_not_supported | sample | Unsupported file type error |
| error.file_too_large | needs-review | File size error |
| error.processing_failed | needs-review | Generic processing failure |
| error.export_failed | needs-review | Export failure |
| error.invalid_language_pack | later | Language pack validation failure |
| lesson.progress | sample | Lesson progress with placeholders |

## feedback keys

| Key | Status | Purpose |
|---|---|---|
| feedback.correct | sample | Correct answer feedback |
| feedback.try_again | sample | Retry feedback |
| feedback.good_progress | sample | Positive progress feedback |
| feedback.grammar_hint | sample | Generic grammar hint |
| feedback.review_needed | sample | Review suggestion |
| feedback.almost_correct | needs-review | Almost correct feedback |
| feedback.check_spelling | needs-review | Spelling hint |
| feedback.check_word_order | needs-review | Word order hint |
| feedback.vocabulary_hint | needs-review | Vocabulary hint |
| feedback.keep_practicing | needs-review | Encouragement feedback |

## glossary keys

| Key | Status | Purpose |
|---|---|---|
| term.pdf | sample | PDF term |
| term.lesson | sample | Lesson term |
| term.exercise | sample | Exercise term |
| term.translation | sample | Translation term |
| term.grammar | sample | Grammar term |
| term.vocabulary | sample | Vocabulary term |
| term.feedback | sample | Feedback term |
| term.document | needs-review | Document term |
| term.page | needs-review | Page term |
| term.paragraph | needs-review | Paragraph term |
| term.question | needs-review | Question term |
| term.answer | needs-review | Answer term |
| term.progress | needs-review | Progress term |
| term.language_pack | later | Language pack term |
| term.placeholder | later | Placeholder term |
| term.schema | later | Schema term |

## possible future Pro keys

These are not core public keys for now.

| Key | Status | Purpose |
|---|---|---|
| pro.feedback.advanced_grammar | possible-pro | Advanced grammar explanation |
| pro.feedback.teacher_note | possible-pro | Teacher-style note |
| pro.feedback.domain_hint | possible-pro | Domain-specific hint |
| pro.term.legal | possible-pro | Legal terminology pack |
| pro.term.medical | possible-pro | Medical terminology pack |
| pro.term.technical | possible-pro | Technical terminology pack |
| pro.template.lesson_plan | possible-pro | Advanced lesson plan template |
| pro.template.teacher_export | possible-pro | Teacher export template |

## Placeholder-bearing keys

| Key | Required placeholders | Example |
|---|---|---|
| lesson.progress | {current}, {total} | Lesson {current} of {total} |
| message.items_processed | {count} | Processed {count} items |
| message.exported_lessons | {count} | Exported {count} lessons |
| error.field_required | {field} | {field} is required |

## Initial runtime integration recommendation

When runtime integration starts, use only the smallest stable subset first:

- app.title
- app.subtitle
- button.start
- button.cancel
- button.save
- button.export
- status.ready
- status.processing
- message.saved
- message.export_complete
- message.file_loaded
- warning.unsaved_changes
- error.file_not_supported
- lesson.progress
- feedback.correct
- feedback.try_again
- term.lesson
- term.exercise
- term.translation

Do not integrate every draft key at once.

## Review notes

Before a key becomes stable:

- verify it is user-facing
- verify it is not a false positive from the inventory
- verify it belongs in the correct section
- verify the name is generic enough
- verify placeholders are stable
- verify ro/en samples can represent it naturally

## Decision for this milestone

For v0.2.9-public-beta-language-pack-review, this file is a draft only.

No runtime localization should be implemented in this milestone.
