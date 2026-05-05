from pathlib import Path
import re

path = Path("services/api/study_engine.py")
text = path.read_text(encoding="utf-8")

if "from content_filter import should_exclude_study_item" not in text:
    text = text.replace(
        "from typing import Any\n",
        "from typing import Any\n\nfrom content_filter import should_exclude_study_item\n",
    )

old_block = '''        source_text = " ".join(
            str(item.get(key) or "")
            for key in [
                "title",
                "lesson_title",
                "text",
                "source_text",
                "text_preview",
                "context",
                "source",
            ]
        )

        if looks_like_generic_or_junk_question(question, answer):
            continue

        if looks_like_front_matter_text(source_text):
            continue

        questions.append(
'''

new_block = '''        title = str(item.get("title") or item.get("lesson_title") or "").strip()

        source_text = " ".join(
            str(item.get(key) or "")
            for key in [
                "title",
                "lesson_title",
                "text",
                "source_text",
                "text_preview",
                "context",
                "source",
            ]
        )

        if should_exclude_study_item(
            title=title,
            question=question,
            answer=answer,
            source_text=source_text,
            lesson_id=lesson_id,
        ):
            continue

        questions.append(
'''

if old_block in text:
    text = text.replace(old_block, new_block)
else:
    # Fallback patch for slightly different versions.
    text = text.replace(
        '''        questions.append(
            {
                "question_id": str(item.get("question_id") or item.get("id") or f"Q{index:03d}"),''',
        '''        title = str(item.get("title") or item.get("lesson_title") or "").strip()

        source_text = " ".join(
            str(item.get(key) or "")
            for key in [
                "title",
                "lesson_title",
                "text",
                "source_text",
                "text_preview",
                "context",
                "source",
            ]
        )

        if should_exclude_study_item(
            title=title,
            question=question,
            answer=answer,
            source_text=source_text,
            lesson_id=lesson_id,
        ):
            continue

        questions.append(
            {
                "question_id": str(item.get("question_id") or item.get("id") or f"Q{index:03d}"),'''
    )

path.write_text(text, encoding="utf-8")
print("OK: study_engine.py now uses content_filter.py.")
