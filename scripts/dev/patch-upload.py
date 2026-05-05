from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

text = text.replace(
    "import html\nimport subprocess\nimport sys\n",
    "import html\nimport re\nimport subprocess\nimport sys\nfrom datetime import datetime\n",
)

text = text.replace(
    "from fastapi import FastAPI, Form, Query",
    "from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile",
)

text = text.replace(
    "    .grid {{",
    """
    .upload-box {{
      background: var(--paper-soft);
      border: 1px dashed var(--accent);
      border-radius: 18px;
      padding: 18px;
      margin-bottom: 20px;
    }}

    .upload-box h2 {{
      margin: 0 0 8px;
      color: var(--heading);
      font-size: 20px;
    }}

    .upload-form {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px;
      margin-top: 12px;
    }}

    input[type="file"] {{
      border: 1px solid var(--border);
      background: var(--paper);
      color: var(--text);
      border-radius: 999px;
      padding: 9px 12px;
      max-width: 100%;
    }}

    .grid {{""",
)

text = text.replace(
    "def run_step(label: str, args: list[str], log_lines: list[str], optional: bool = False) -> None:",
    """
def safe_upload_name(filename: str) -> str:
    name = Path(filename or "").name
    suffix = Path(name).suffix.lower()

    if suffix != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    stem = Path(name).stem
    stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", stem).strip(" ._")

    if not stem:
        stem = "document"

    return stem + ".pdf"


def run_step(label: str, args: list[str], log_lines: list[str], optional: bool = False) -> None:""",
)

text = text.replace(
    "@app.get(\"/\", response_class=HTMLResponse)\ndef home(generated: str | None = Query(default=None)) -> HTMLResponse:",
    "@app.get(\"/\", response_class=HTMLResponse)\ndef home(generated: str | None = Query(default=None), uploaded: str | None = Query(default=None)) -> HTMLResponse:",
)

text = text.replace(
    "    cards = []\n\n    for pdf in pdfs():",
    """    cards = []

    upload_box = \"\"\"
        <div class="upload-box">
          <h2>Upload PDF</h2>
          <div class="meta">Choose a PDF from your computer. It will be saved locally in <code>data/input</code>.</div>
          <form class="upload-form" method="post" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file" accept="application/pdf" required>
            <button class="primary" type="submit">Upload PDF</button>
          </form>
        </div>
        \"\"\"

    for pdf in pdfs():""",
)

text = text.replace(
    "        body = \"\"\"\n        <div class=\"notice\">",
    "        body = upload_box + \"\"\"\n        <div class=\"notice\">",
)

text = text.replace(
    """        notice = ""
        if generated:
            notice = f\"\"\"
            <div class="notice">
              Generated: <strong>{html.escape(generated)}</strong>
            </div>
            \"\"\"

        body = f\"\"\"
        {notice}""",
    """        notice = ""

        if uploaded:
            notice += f\"\"\"
            <div class="notice">
              Uploaded: <strong>{html.escape(uploaded)}</strong>
            </div>
            \"\"\"

        if generated:
            notice += f\"\"\"
            <div class="notice">
              Generated: <strong>{html.escape(generated)}</strong>
            </div>
            \"\"\"

        body = upload_box + f\"\"\"
        {notice}""",
)

text = text.replace(
    """
@app.get("/log")
def log(pdf: str = Query(...)) -> PlainTextResponse:
""",
    """
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> RedirectResponse:
    filename = safe_upload_name(file.filename or "document.pdf")
    destination = INPUT_DIR / filename

    if destination.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = INPUT_DIR / f"{destination.stem}_{stamp}.pdf"

    with destination.open("wb") as handle:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)

    return RedirectResponse(
        url="/?uploaded=" + quote(destination.name),
        status_code=303,
    )


@app.get("/log")
def log(pdf: str = Query(...)) -> PlainTextResponse:
""",
)

path.write_text(text, encoding="utf-8")
print("OK: web_app.py updated with browser PDF upload.")
