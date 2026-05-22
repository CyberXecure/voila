import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PLANNED_KEYS = [
    "ui.heading.home",
    "ui.heading.review",
    "ui.heading.review_question",
    "ui.heading.no_review_questions",
    "ui.heading.review_weak_concepts",
    "ui.heading.progress",
    "ui.heading.progress_dashboard",
    "ui.heading.crop_editor_not_started",
    "ui.heading.source_page",
    "ui.heading.editable_ocr_text",
    "ui.heading.suspicious_pages",

    "ui.button.save_page_correction",
    "ui.button.save_reviewed_page",
    "ui.button.save_as_needs_review",
    "ui.button.apply_corrected_ocr",

    "ui.link.back",
    "ui.link.next_review",
    "ui.link.study",
    "ui.link.progress",
    "ui.link.continue_study",
    "ui.link.course_tools",
    "ui.link.top",
    "ui.link.bottom",
    "ui.link.back_to_voila",
    "ui.link.reload",
    "ui.link.concepts",
    "ui.link.course",
    "ui.link.review_ocr",

    "ui.label.correct_concept_title",
]


def load_messages(lang: str) -> dict:
    path = ROOT / "language-packs" / "core" / f"{lang}.language-pack.json"
    return json.loads(path.read_text(encoding="utf-8"))["messages"]


class UiFullLocalizationCoreKeyTests(unittest.TestCase):
    def test_ro_and_en_have_all_planned_keys(self):
        for lang in ["ro", "en"]:
            messages = load_messages(lang)
            missing = [key for key in PLANNED_KEYS if key not in messages]
            self.assertEqual(missing, [], f"{lang} is missing planned keys")

    def test_ro_and_en_planned_key_sets_match(self):
        ro_messages = load_messages("ro")
        en_messages = load_messages("en")

        ro_keys = {key for key in ro_messages if key in PLANNED_KEYS}
        en_keys = {key for key in en_messages if key in PLANNED_KEYS}

        self.assertEqual(ro_keys, en_keys)

    def test_planned_values_are_non_empty_strings(self):
        for lang in ["ro", "en"]:
            messages = load_messages(lang)
            for key in PLANNED_KEYS:
                value = messages[key]
                self.assertIsInstance(value, str)
                self.assertTrue(value.strip(), f"{lang}:{key} must not be empty")

    def test_expected_representative_values(self):
        en = load_messages("en")
        ro = load_messages("ro")

        self.assertEqual(en["ui.heading.review_question"], "Review question")
        self.assertEqual(ro["ui.heading.review_question"], "Întrebare de revizuire")

        self.assertEqual(en["ui.button.save_page_correction"], "Save page correction")
        self.assertEqual(ro["ui.button.save_page_correction"], "Salvează corecția paginii")

        self.assertEqual(en["ui.link.back"], "Back")
        self.assertEqual(ro["ui.link.back"], "Înapoi")

        self.assertEqual(en["ui.label.correct_concept_title"], "Correct concept title")
        self.assertEqual(ro["ui.label.correct_concept_title"], "Corectează titlul conceptului")


if __name__ == "__main__":
    unittest.main(verbosity=2)