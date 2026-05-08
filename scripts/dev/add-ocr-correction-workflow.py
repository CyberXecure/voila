from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

marker = "# VOILA_OCR_CORRECTION_ROUTES_V1"

if marker in text:
    print("OK: OCR correction routes already exist.")
else:
    block = r'''

# VOILA_OCR_CORRECTION_ROUTES_V1

from fastapi import Request as _VoilaRequest
from fastapi.responses import HTMLResponse as _VoilaHTMLResponse
from fastapi.responses import RedirectResponse as _VoilaRedirectResponse
from fastapi.responses import Response as _VoilaResponse


def _voila_safe_pdf_name(pdf: str) -> str:
    return Path(str(pdf or "")).name


def _voila_ocr_out_dir(pdf: str) -> Path:
    return PROJECT_ROOT / "data" / "output" / Path(_voila_safe_pdf_name(pdf)).stem


def _voila_page_count_for_pdf(pdf: str) -> int:
    import fitz

    pdf_path = PROJECT_ROOT / "data" / "input" / _voila_safe_pdf_name(pdf)

    if not pdf_path.exists():
        return 1

    doc = fitz.open(pdf_path)

    try:
        return max(1, len(doc))
    finally:
        doc.close()


@app.get("/ocr-page-image")
def voila_ocr_page_image(pdf: str = "", page: int = 1, zoom: float = 2.2):
    import fitz

    safe_pdf = _voila_safe_pdf_name(pdf)
    pdf_path = PROJECT_ROOT / "data" / "input" / safe_pdf

    if not pdf_path.exists():
        return _VoilaResponse("PDF not found", status_code=404)

    page_index = max(0, int(page) - 1)

    doc = fitz.open(pdf_path)

    try:
        page_index = min(page_index, len(doc) - 1)
        pix = doc.load_page(page_index).get_pixmap(
            matrix=fitz.Matrix(float(zoom), float(zoom)),
            colorspace=fitz.csRGB,
            alpha=False,
        )
        png = pix.tobytes("png")
    finally:
        doc.close()

    return _VoilaResponse(content=png, media_type="image/png")


@app.get("/review-ocr-corrected")
def voila_review_ocr_corrected(pdf: str = "", page: int = 1, saved: int = 0, applied: int = 0):
    import html
    from urllib.parse import quote
    import ocr_page_corrections as oc

    safe_pdf = _voila_safe_pdf_name(pdf)
    out_dir = _voila_ocr_out_dir(safe_pdf)

    page_count = _voila_page_count_for_pdf(safe_pdf)
    page_number = max(1, min(int(page or 1), page_count))

    original_text = oc.get_page_text(out_dir, page_number)
    corrected_text = oc.get_corrected_text(out_dir, page_number)

    corr_data = oc.load_corrections(out_dir)
    item = corr_data.get("page_corrections", {}).get(str(page_number), {})
    status = item.get("status") if isinstance(item, dict) else ""

    q_pdf = quote(safe_pdf)

    prev_page = max(1, page_number - 1)
    next_page = min(page_count, page_number + 1)

    saved_msg = ""
    if int(saved or 0):
        saved_msg = '<div class="notice ok">Saved correction.</div>'

    applied_msg = ""
    if int(applied or 0):
        applied_msg = '<div class="notice ok">Applied corrected OCR to pages.json / ocr_pages.json.</div>'

    css = """
    :root {
      --bg: #101819;
      --panel: #202d31;
      --panel2: #26363b;
      --text: #f6ead7;
      --muted: #c7ad94;
      --line: #3b4b50;
      --accent: #e0ad68;
      --danger: #b85757;
      --ok: #6fa878;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
    }

    header {
      position: sticky;
      top: 0;
      z-index: 20;
      background: rgba(16, 24, 25, 0.96);
      border-bottom: 1px solid var(--line);
      padding: 14px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }

    h1 {
      margin: 0;
      font-size: 22px;
      line-height: 1.2;
    }

    .muted { color: var(--muted); }

    .actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }

    a, button {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 9px 13px;
      background: var(--panel2);
      color: var(--text);
      text-decoration: none;
      font-weight: 850;
      cursor: pointer;
    }

    button.primary, a.primary {
      background: var(--accent);
      color: white;
      border-color: transparent;
    }

    button.danger {
      background: var(--danger);
      color: white;
      border-color: transparent;
    }

    main {
      display: grid;
      grid-template-columns: minmax(420px, 1fr) minmax(420px, 1fr);
      gap: 16px;
      padding: 16px;
      height: calc(100vh - 76px);
    }

    .pane {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      overflow: hidden;
      min-height: 0;
    }

    .pane-title {
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      color: var(--muted);
      font-weight: 800;
      display: flex;
      justify-content: space-between;
      gap: 10px;
    }

    .scan-wrap {
      width: 100%;
      height: calc(100% - 48px);
      overflow: auto;
      cursor: grab;
      background: #0b1112;
      padding: 16px;
    }

    .scan-wrap:active { cursor: grabbing; }

    .scan-wrap img {
      max-width: none;
      width: 100%;
      display: block;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,.35);
    }

    form.editor {
      height: calc(100% - 48px);
      display: flex;
      flex-direction: column;
      gap: 10px;
      padding: 14px;
    }

    textarea {
      flex: 1;
      min-height: 0;
      width: 100%;
      resize: none;
      border-radius: 16px;
      border: 1px solid var(--line);
      background: #111b1e;
      color: var(--text);
      padding: 14px;
      font-family: Consolas, ui-monospace, monospace;
      font-size: 16px;
      line-height: 1.45;
      outline: none;
    }

    .notice {
      margin: 0 16px 12px;
      padding: 10px 12px;
      border-radius: 14px;
      font-weight: 800;
    }

    .notice.ok {
      background: rgba(111,168,120,.18);
      color: #bde7c3;
      border: 1px solid rgba(111,168,120,.35);
    }

    .hint {
      font-size: 13px;
      color: var(--muted);
      padding: 0 2px 4px;
    }

    @media (max-width: 980px) {
      main {
        grid-template-columns: 1fr;
        height: auto;
      }

      .pane {
        min-height: 70vh;
      }
    }
    """

    html_doc = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Correct OCR · Voila!</title>
  <style>{css}</style>
</head>
<body>
  <header>
    <div>
      <h1>Correct OCR Text</h1>
      <div class="muted">{html.escape(safe_pdf)} · page {page_number} / {page_count} · status: {html.escape(str(status or "not reviewed"))}</div>
    </div>

    <div class="actions">
      <a href="/course-tools?pdf={q_pdf}">Course Tools</a>
      <a href="/review-ocr-corrected?pdf={q_pdf}&page={prev_page}">← Prev</a>
      <a href="/review-ocr-corrected?pdf={q_pdf}&page={next_page}">Next →</a>
      <a href="/review-ocr-text?pdf={q_pdf}&page={page_number}">Old OCR Review</a>
    </div>
  </header>

  {saved_msg}
  {applied_msg}

  <main>
    <section class="pane">
      <div class="pane-title">
        <span>Scanned page</span>
        <span>Tip: Ctrl + mouse wheel zoom, drag with mouse to pan</span>
      </div>
      <div class="scan-wrap" id="scanWrap">
        <img src="/ocr-page-image?pdf={q_pdf}&page={page_number}&zoom=2.4" alt="page scan">
      </div>
    </section>

    <section class="pane">
      <div class="pane-title">
        <span>Editable corrected OCR</span>
        <span>{len(corrected_text)} chars</span>
      </div>

      <form class="editor" method="post" action="/save-ocr-correction">
        <input type="hidden" name="pdf" value="{html.escape(safe_pdf)}">
        <input type="hidden" name="page" value="{page_number}">

        <div class="hint">
          Corectează textul aici. Save păstrează corecția în <code>ocr_corrections.json</code>.
        </div>

        <textarea name="text" spellcheck="false">{html.escape(corrected_text)}</textarea>

        <div class="actions">
          <button class="primary" type="submit" name="status" value="reviewed">Save reviewed page</button>
          <button type="submit" name="status" value="needs_review">Save as needs review</button>
        </div>
      </form>

      <form method="post" action="/apply-corrected-ocr" style="padding:0 14px 14px;">
        <input type="hidden" name="pdf" value="{html.escape(safe_pdf)}">
        <button class="danger" type="submit">Apply corrected OCR to pages.json</button>
      </form>
    </section>
  </main>

  <script>
    const box = document.getElementById('scanWrap');
    let isDown = false;
    let startX = 0;
    let startY = 0;
    let scrollLeft = 0;
    let scrollTop = 0;

    box.addEventListener('mousedown', (e) => {{
      isDown = true;
      startX = e.pageX - box.offsetLeft;
      startY = e.pageY - box.offsetTop;
      scrollLeft = box.scrollLeft;
      scrollTop = box.scrollTop;
    }});

    box.addEventListener('mouseleave', () => {{ isDown = false; }});
    box.addEventListener('mouseup', () => {{ isDown = false; }});

    box.addEventListener('mousemove', (e) => {{
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - box.offsetLeft;
      const y = e.pageY - box.offsetTop;
      box.scrollLeft = scrollLeft - (x - startX);
      box.scrollTop = scrollTop - (y - startY);
    }});
  </script>
</body>
</html>
"""

    return _VoilaHTMLResponse(html_doc)


@app.post("/save-ocr-correction")
async def voila_save_ocr_correction(request: _VoilaRequest):
    import ocr_page_corrections as oc
    from urllib.parse import quote

    form = await request.form()

    pdf = _voila_safe_pdf_name(str(form.get("pdf") or ""))
    page = int(form.get("page") or 1)
    text = str(form.get("text") or "")
    status = str(form.get("status") or "reviewed")

    out_dir = _voila_ocr_out_dir(pdf)

    oc.save_page_correction(
        out_dir=out_dir,
        page_number=page,
        text=text,
        status=status,
    )

    return _VoilaRedirectResponse(
        url=f"/review-ocr-corrected?pdf={quote(pdf)}&page={page}&saved=1",
        status_code=303,
    )


@app.post("/apply-corrected-ocr")
async def voila_apply_corrected_ocr(request: _VoilaRequest):
    import ocr_page_corrections as oc
    from urllib.parse import quote

    form = await request.form()

    pdf = _voila_safe_pdf_name(str(form.get("pdf") or ""))
    out_dir = _voila_ocr_out_dir(pdf)

    oc.apply_page_corrections(out_dir, pdf_name=pdf)

    return _VoilaRedirectResponse(
        url=f"/review-ocr-corrected?pdf={quote(pdf)}&page=1&applied=1",
        status_code=303,
    )
'''
    text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8")
    print("OK: OCR correction routes added.")
