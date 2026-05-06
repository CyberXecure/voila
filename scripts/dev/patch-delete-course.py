from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# Ensure imports.
if "import shutil" not in text:
    text = text.replace("import json\n", "import json\nimport shutil\n")

if "from datetime import datetime" not in text:
    text = text.replace("import shutil\n", "import shutil\nfrom datetime import datetime\n")

# Add CSS for inline forms and danger buttons.
css = '''
    .inline-form {{
      display: inline;
      margin: 0;
    }}

    .btn.danger,
    button.danger {{
      background: rgba(151, 75, 58, 0.92);
      color: #fffaf0;
      border-color: rgba(151, 75, 58, 0.92);
    }}
'''

if ".inline-form" not in text:
    text = text.replace("</style>", css + "\n  </style>", 1)

# Add Delete course button after Logs button block if possible.
old = '''        if log_file.exists():
            actions.append(
                f'<a class="btn" href="/log?pdf={quote(pdf.name)}">Logs</a>'
            )
'''

new = '''        if log_file.exists():
            actions.append(
                f'<a class="btn" href="/log?pdf={quote(pdf.name)}">Logs</a>'
            )

        if out_dir.exists():
            actions.append(
                f"""
                <form class="inline-form" method="post" action="/delete-course"
                      onsubmit="return confirm('Delete generated course files for this PDF? The original PDF will be kept.')">
                  <input type="hidden" name="pdf_name" value="{html.escape(pdf.name)}">
                  <button class="btn danger" type="submit">Delete course</button>
                </form>
                """
            )
'''

if old in text and "/delete-course" not in text:
    text = text.replace(old, new)

# Add helper + route before /progress or /study.
route = r'''

def trash_course_output(output_dir: Path) -> Path | None:
    if not output_dir.exists():
        return None

    trash_dir = PROJECT_ROOT / "data" / "trash" / "courses"
    trash_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = trash_dir / f"{output_dir.name}_{stamp}"

    shutil.move(str(output_dir), str(target))

    return target


@app.post("/delete-course")
def delete_course(pdf_name: str = Form(...)) -> RedirectResponse:
    pdf_path = validate_pdf_name(pdf_name)
    output_dir = OUTPUT_DIR / pdf_path.stem

    trash_course_output(output_dir)

    return RedirectResponse(
        url="/",
        status_code=303,
    )

'''

if '@app.post("/delete-course")' not in text:
    if '\n@app.get("/progress"' in text:
        text = text.replace('\n@app.get("/progress"', route + '\n@app.get("/progress"', 1)
    elif '\n@app.get("/study"' in text:
        text = text.replace('\n@app.get("/study"', route + '\n@app.get("/study"', 1)
    else:
        raise SystemExit("Could not find route insertion point.")

path.write_text(text, encoding="utf-8")

print("OK: Delete course option added.")
