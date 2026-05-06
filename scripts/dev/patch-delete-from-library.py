from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# Ensure imports.
if "import shutil" not in text:
    if "import json" in text:
        text = text.replace("import json\n", "import json\nimport shutil\n")
    else:
        text = text.replace("import html\n", "import html\nimport shutil\n")

if "from datetime import datetime" not in text:
    text = text.replace("import shutil\n", "import shutil\nfrom datetime import datetime\n")

# Remove previous delete-course button block if present.
text = re.sub(
    r'\n\s*if out_dir\.exists\(\):\s*\n\s*actions\.append\(\s*\n\s*f"""\s*\n\s*<form class="inline-form" method="post" action="/delete-course".*?</form>\s*\n\s*"""\s*\n\s*\)\s*\n',
    "\n",
    text,
    flags=re.DOTALL,
)

text = re.sub(
    r'\n\s*actions\.append\(\s*\n\s*f"""\s*\n\s*<form class="inline-form" method="post" action="/delete-course".*?</form>\s*\n\s*"""\s*\n\s*\)\s*\n',
    "\n",
    text,
    flags=re.DOTALL,
)

# Add delete button for every PDF card, not only generated courses.
delete_button = '''        actions.append(
            f"""
            <form class="inline-form" method="post" action="/delete-course"
                  onsubmit="return confirm('Remove this PDF and its generated course from the library? Files will be moved to data/trash, not permanently deleted.')">
              <input type="hidden" name="pdf_name" value="{html.escape(pdf.name)}">
              <button class="btn danger" type="submit">Delete from library</button>
            </form>
            """
        )
'''

if 'Delete from library' not in text:
    text = text.replace("        actions = []\n", "        actions = []\n" + delete_button + "\n", 1)

# Add helper to move original PDF to trash.
helper = r'''

def trash_input_pdf(pdf_path: Path) -> Path | None:
    if not pdf_path.exists():
        return None

    trash_dir = PROJECT_ROOT / "data" / "trash" / "pdfs"
    trash_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = trash_dir / f"{pdf_path.stem}_{stamp}{pdf_path.suffix}"

    shutil.move(str(pdf_path), str(target))

    return target

'''

if "def trash_input_pdf" not in text:
    text = text.replace('\n@app.post("/delete-course")', helper + '\n@app.post("/delete-course")', 1)

# Replace delete route so it removes both generated output and original PDF from active library.
route_pattern = r'''@app\.post\("/delete-course"\)
def delete_course\(pdf_name: str = Form\(\.\.\.\)\) -> RedirectResponse:
    pdf_path = validate_pdf_name\(pdf_name\)
    output_dir = OUTPUT_DIR / pdf_path\.stem

    trash_course_output\(output_dir\)

    return RedirectResponse\(
        url="/",
        status_code=303,
    \)
'''

route_replacement = '''@app.post("/delete-course")
def delete_course(pdf_name: str = Form(...)) -> RedirectResponse:
    pdf_path = validate_pdf_name(pdf_name)
    output_dir = OUTPUT_DIR / pdf_path.stem

    trash_course_output(output_dir)
    trash_input_pdf(pdf_path)

    return RedirectResponse(
        url="/",
        status_code=303,
    )
'''

text = re.sub(route_pattern, route_replacement, text)

# Rename any old labels / confirmations.
text = text.replace("Delete course", "Delete from library")
text = text.replace(
    "Delete generated course files for this PDF? The original PDF will be kept.",
    "Remove this PDF and its generated course from the library? Files will be moved to data/trash, not permanently deleted."
)

path.write_text(text, encoding="utf-8")

print("OK: Delete from library now moves PDF + course output to trash.")
