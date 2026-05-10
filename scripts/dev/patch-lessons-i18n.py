from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

replacements = {
    ">Deschide lecția<": '>{_ut("open_lesson", "Open lesson")}<',
    ">Studiază lecția<": '>{_ut("study_lesson", "Study lesson")}<',
    ">Citește lecția<": '>{_ut("read_lesson", "Read lesson")}<',
    ">← Lecții<": '>← {_ut("lessons", "Lessons")}<',
    ">Study general<": '>{_ut("general_study", "General study")}<',
    ">Open course<": '>{_ut("open_course", "Open course")}<',
    ">Library<": '>{_ut("library", "Library")}<',
    "<h1>Lecții</h1>": '<h1>{_ut("lessons", "Lessons")}</h1>',
    "Lecții găsite: <strong>{len(lessons)}</strong>": '{_ut("lessons_found", "Lessons found")}: <strong>{len(lessons)}</strong>',
    "<h2>Nu există lecții disponibile</h2>": '<h2>{_ut("no_lessons", "No lessons available")}</h2>',
    "<p>Generează mai întâi cursul / quiz-ul pentru acest PDF.</p>": '<p>{_ut("generate_course_first_short", "Generate the course / quiz for this PDF first.")}</p>',
    "<h1>Lecție negăsită</h1>": '<h1>{_ut("lesson_not_found", "Lesson not found")}</h1>',
    "Înapoi la lecții": '{_ut("back_to_lessons", "Back to lessons")}',
    "Nu există text sursă disponibil pentru această lecție.": '{_ut("no_source_text_for_lesson", "No source text is available for this lesson.")}',
    "Nu există întrebări pentru lecția selectată.": '{_ut("no_questions_for_lesson", "No questions are available for the selected lesson.")}',
    "Pages: <strong>{html.escape(pages)}</strong>": '{_ut("pages", "Pages")}: <strong>{html.escape(pages)}</strong>',
    "Pages: <strong>{html.escape(pages)}</strong><br>": '{_ut("pages", "Pages")}: <strong>{html.escape(pages)}</strong><br>',
}

changed = 0

for old, new in replacements.items():
    count = text.count(old)
    if count:
        text = text.replace(old, new)
        changed += count

path.write_text(text, encoding="utf-8")
print("OK: Lessons route labels translated.")
print("Changed:", changed)
