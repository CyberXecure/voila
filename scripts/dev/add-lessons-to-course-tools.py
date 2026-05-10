from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# Add Lessons in nav items, if that block exists.
if '("Lessons", f"/lessons?pdf={q}", "lessons")' not in text:
    text = text.replace(
'''        ("Course", f"/view-course?pdf={q}", "course"),
        ("Study", f"/study?pdf={q}", "study"),
''',
'''        ("Course", f"/view-course?pdf={q}", "course"),
        ("Lessons", f"/lessons?pdf={q}", "lessons"),
        ("Study", f"/study?pdf={q}", "study"),
'''
    )

# Add Lessons card in Course Tools.
if 'card("Lessons"' not in text:
    text = text.replace(
'''        card("Open course", "Read the generated course with navigation.", f"/view-course?pdf={q}", checks["course"]),
        card("Study mode", "Practice questions generated from the course.", f"/study?pdf={q}", checks["study"]),
''',
'''        card("Open course", "Read the generated course with navigation.", f"/view-course?pdf={q}", checks["course"]),
        card("Lessons", "Choose a lesson, read it, then study only that lesson.", f"/lessons?pdf={q}", checks["study"]),
        card("Study mode", "Practice questions generated from the course.", f"/study?pdf={q}", checks["study"]),
'''
    )

path.write_text(text, encoding="utf-8")
print("OK: Course Tools includes Lessons link/card.")
