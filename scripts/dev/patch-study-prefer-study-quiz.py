from pathlib import Path
import re

path = Path("services/api/study_engine.py")
text = path.read_text(encoding="utf-8")

text = text.replace(
'''def load_questions(output_dir: Path) -> list[dict]:
    quiz_path = output_dir / "quiz.json"

    if not quiz_path.exists():
        return []

    raw = json.loads(quiz_path.read_text(encoding="utf-8"))
    return normalize_quiz(raw)
''',
'''def load_questions(output_dir: Path) -> list[dict]:
    study_quiz_path = output_dir / "quiz.study.json"
    default_quiz_path = output_dir / "quiz.json"

    if study_quiz_path.exists():
        quiz_path = study_quiz_path
    else:
        quiz_path = default_quiz_path

    if not quiz_path.exists():
        return []

    raw = json.loads(quiz_path.read_text(encoding="utf-8"))
    return normalize_quiz(raw)
'''
)

text = text.replace(
'''                "concept_id": lesson_id,''',
'''                "concept_id": str(item.get("concept_id") or item.get("concept") or lesson_id).strip(),'''
)

path.write_text(text, encoding="utf-8")
print("OK: study_engine.py now prefers quiz.study.json and supports concept_id.")
