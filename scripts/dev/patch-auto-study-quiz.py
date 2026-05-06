from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

if "import json" not in text:
    text = text.replace("import html\n", "import html\nimport json\n")

insert_after = '''def generate_for_pdf(pdf_path: Path) -> Path:
'''

helper = '''
def study_min_page_for_pdf(pdf_path: Path) -> int:
    config_path = PROJECT_ROOT / "data" / "study_config.json"

    if not config_path.exists():
        return 1

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        min_page = int(config.get("default_min_page") or 1)
        per_pdf = config.get("per_pdf") or {}
        pdf_config = per_pdf.get(pdf_path.stem) or {}

        if "min_page" in pdf_config:
            min_page = int(pdf_config["min_page"])

        return max(1, min_page)
    except Exception:
        return 1


'''

if "def study_min_page_for_pdf" not in text:
    text = text.replace(insert_after, helper + insert_after)

old = '''    run_step(
        "8. Export figures",
        [str(PROJECT_ROOT / "services" / "api" / "figure_exporter_hybrid.py"), str(pdf_path)],
        log_lines,
        optional=True,
    )

    run_step(
        "9. Export HTML course",
        [str(PROJECT_ROOT / "services" / "api" / "html_exporter.py"), str(course_cleaned)],
        log_lines,
    )
'''

new = '''    study_min_page = study_min_page_for_pdf(pdf_path)

    run_step(
        "8. Build study quiz",
        [
            str(PROJECT_ROOT / "services" / "api" / "study_quiz_builder.py"),
            str(output_dir),
            "--min-page",
            str(study_min_page),
            "--max-per-lesson",
            "4",
            "--max-total",
            "350",
        ],
        log_lines,
    )

    run_step(
        "9. Export figures",
        [str(PROJECT_ROOT / "services" / "api" / "figure_exporter_hybrid.py"), str(pdf_path)],
        log_lines,
        optional=True,
    )

    run_step(
        "10. Export HTML course",
        [str(PROJECT_ROOT / "services" / "api" / "html_exporter.py"), str(course_cleaned)],
        log_lines,
    )
'''

if old not in text:
    raise SystemExit("Target block not found. Patch not applied.")

text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
print("OK: web_app.py now builds quiz.study.json during Generate course.")
