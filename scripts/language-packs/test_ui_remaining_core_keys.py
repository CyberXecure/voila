import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "language-packs" / "core"

PLANNED_UI_KEYS = {
    "ui.back",
    "ui.tools",
    "ui.course",
    "ui.lessons",
    "ui.library",
    "ui.logs",
    "ui.course_tools",
    "ui.quick_tools",
    "ui.study_mode",
    "ui.review_ocr_text",
    "ui.review_concepts",
    "ui.review_study_concepts",
    "ui.correct_ocr_text",
    "ui.continue_study",
    "ui.toggle_theme",
    "ui.save_title_override",
    "ui.save_page_correction",
    "ui.save_reviewed_page",
    "ui.save_as_needs_review",
    "ui.apply_corrected_ocr",
    "ui.fit_width",
}

PLANNED_MESSAGE_KEYS = {
    "message.choose_pdf_helper",
    "message.no_pdf_files_found",
    "message.open_course_description",
    "message.lessons_description",
    "message.study_mode_description",
    "message.review_ocr_text_description",
    "message.review_concepts_description",
    "message.edit_crops_description",
    "message.figures_description",
    "message.progress_description",
    "message.return_to_library_description",
    "message.source_mode_description",
    "message.apply_corrected_ocr_warning",
}

PLANNED_STATUS_KEYS = {
    "status.uploaded",
    "status.not_generated_yet",
    "status.no_suspicious_pages_detected",
    "status.focused_concept",
    "status.attempts",
    "status.status",
    "status.study_coverage",
    "status.overall_mastery",
    "status.concept_status",
    "status.missing_pdf_name",
    "status.no_ocr_pages_found",
    "status.rebuild_complete",
    "status.rebuild_failed",
    "status.save_title_override_failed",
    "status.save_ocr_text_failed",
}

ALL_PLANNED_KEYS = PLANNED_UI_KEYS | PLANNED_MESSAGE_KEYS | PLANNED_STATUS_KEYS


def load_messages(lang: str) -> dict[str, str]:
    path = CORE / f"{lang}.language-pack.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    messages = data.get("messages")
    if not isinstance(messages, dict):
        raise AssertionError(f"{path} has no messages object")
    return messages


class UiRemainingCoreKeyTests(unittest.TestCase):
    def test_ro_and_en_have_all_planned_keys(self) -> None:
        for lang in ("ro", "en"):
            messages = load_messages(lang)
            missing = sorted(ALL_PLANNED_KEYS - set(messages))
            self.assertEqual([], missing, f"{lang} missing planned keys")

    def test_ro_and_en_planned_key_sets_match(self) -> None:
        ro = load_messages("ro")
        en = load_messages("en")

        ro_keys = {key for key in ro if key in ALL_PLANNED_KEYS}
        en_keys = {key for key in en if key in ALL_PLANNED_KEYS}

        self.assertEqual(ro_keys, en_keys)

    def test_planned_values_are_non_empty_strings(self) -> None:
        for lang in ("ro", "en"):
            messages = load_messages(lang)
            for key in sorted(ALL_PLANNED_KEYS):
                value = messages.get(key)
                self.assertIsInstance(value, str, f"{lang}:{key} must be a string")
                self.assertTrue(value.strip(), f"{lang}:{key} must not be empty")

    def test_expected_representative_values(self) -> None:
        ro = load_messages("ro")
        en = load_messages("en")

        self.assertEqual("Instrumente curs", ro["ui.course_tools"])
        self.assertEqual("Course Tools", en["ui.course_tools"])
        self.assertEqual("Alege un PDF din computer. Va fi salvat local în data/input.", ro["message.choose_pdf_helper"])
        self.assertEqual("Choose a PDF from your computer. It will be saved locally in data/input.", en["message.choose_pdf_helper"])
        self.assertEqual("Negenerat încă", ro["status.not_generated_yet"])
        self.assertEqual("Not generated yet", en["status.not_generated_yet"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
