from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

if "def _build_study_question_display(" not in text:
    marker = '''def _ut(key: str, fallback: str) -> str:
    return str(_ui_texts().get(key) or fallback)
'''

    insert = marker + r'''

def _build_study_question_display(question: dict, pdf_name: str) -> str:
    try:
        import study_questions
        return study_questions.build_study_question(PROJECT_ROOT, pdf_name, question)
    except Exception:
        try:
            return _study_question_display(str(question.get("question") or ""))
        except Exception:
            return str(question.get("question") or "")
'''

    if marker not in text:
        raise SystemExit("Nu găsesc _ut helper.")

    text = text.replace(marker, insert, 1)

replacements = {
    '<p style="font-size: 20px;"><strong>{html.escape(str(current.get("question")))}</strong></p>':
        '<p style="font-size: 20px;"><strong>{html.escape(_build_study_question_display(current, pdf_path.name))}</strong></p>',

    '<p style="font-size: 20px;"><strong>{html.escape(_study_question_display(str(current.get("question"))))}</strong></p>':
        '<p style="font-size: 20px;"><strong>{html.escape(_build_study_question_display(current, pdf_path.name))}</strong></p>',
}

changed = 0

for old, new in replacements.items():
    count = text.count(old)
    if count:
        text = text.replace(old, new)
        changed += count

path.write_text(text, encoding="utf-8")

print("OK: Study Mode now uses study_questions.build_study_question.")
print("Replacements:", changed)
