from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

old = '''    run_step(
        "10. Export HTML course",
        [str(PROJECT_ROOT / "services" / "api" / "html_exporter.py"), str(course_cleaned)],
        log_lines,
    )
'''

new = '''    run_step(
        "10. Export HTML course",
        [str(PROJECT_ROOT / "services" / "api" / "html_exporter.py"), str(course_cleaned)],
        log_lines,
    )

    course_html = output_dir / "course.cleaned.html"

    run_step(
        "11. Inject course navigation",
        [
            str(PROJECT_ROOT / "services" / "api" / "course_nav_injector.py"),
            str(course_html),
            pdf_path.name,
        ],
        log_lines,
    )
'''

if old not in text:
    raise SystemExit("Could not find HTML export step in web_app.py.")

text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
print("OK: web_app.py now injects navigation into course HTML.")
