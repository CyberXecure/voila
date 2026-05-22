import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PLANNED_KEYS = [
    "ui.link.previous",
    "ui.link.prev",
    "ui.link.next",
    "ui.link.back_to_ocr_review",

    "ui.message.local_pdf_learning_studio",
    "ui.message.generate_study_quiz_first",
    "ui.message.crop_editor_port_not_responding",
    "ui.message.no_study_questions_found",
    "ui.message.concept_title_cannot_be_empty",
    "ui.message.correction_not_saved_exception",
    "ui.message.ocr_corrections_applied",
    "ui.message.no_pdfs_found",

    "ui.title.correct_ocr",
]


def load_messages(lang: str) -> dict:
    path = ROOT / "language-packs" / "core" / f"{lang}.language-pack.json"
    return json.loads(path.read_text(encoding="utf-8"))["messages"]


class UiFullLocalizationNextBatchCoreKeyTests(unittest.TestCase):
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

        self.assertEqual(en["ui.link.next"], "Next")
        self.assertEqual(ro["ui.link.next"], "Următor")

        self.assertEqual(en["ui.link.back_to_ocr_review"], "Back to OCR Review")
        self.assertEqual(ro["ui.link.back_to_ocr_review"], "Înapoi la revizuirea OCR")

        self.assertEqual(en["ui.message.no_pdfs_found"], "No PDFs found.")
        self.assertEqual(ro["ui.message.no_pdfs_found"], "Nu au fost găsite PDF-uri.")

        self.assertEqual(en["ui.title.correct_ocr"], "Correct OCR · Voila!")
        self.assertEqual(ro["ui.title.correct_ocr"], "Corectare OCR · Voila!")


if __name__ == "__main__":
    unittest.main(verbosity=2)