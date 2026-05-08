from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

old = '''    run_step(
        "10. Export HTML course",
        [str(PROJECT_ROOT / "services" / "api" / "html_exporter.py"), str(course_cleaned)],
        log_lines,
    )

    course_html = output_dir / "course.cleaned.html"
'''

new = '''    run_step(
        "10. Export HTML course",
        [str(PROJECT_ROOT / "services" / "api" / "html_exporter.py"), str(course_cleaned)],
        log_lines,
    )

    run_step(
        "10b. Scanned PDF fallback",
        [
            str(PROJECT_ROOT / "services" / "api" / "scanned_course_fallback.py"),
            str(pdf_path),
            str(output_dir),
            "--zoom",
            "1.45",
        ],
        log_lines,
        optional=True,
    )

    course_html = output_dir / "course.cleaned.html"
'''

if old not in text:
    raise SystemExit("Could not find HTML export block in web_app.py.")

text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")

print("OK: scanned course fallback integrated in web_app.py.")
