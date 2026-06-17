from __future__ import annotations

import html
import json
import time
from pathlib import Path
from urllib.parse import quote

import fitz
from fastapi import FastAPI, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "data" / "input"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

app = FastAPI(title="Voila! Crop Editor")

app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")


def latest_pdf() -> Path | None:
    pdfs = sorted(INPUT_DIR.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pdfs[0] if pdfs else None


def validate_pdf_name(pdf_name: str | None) -> Path:
    if pdf_name:
        pdf = INPUT_DIR / Path(pdf_name).name
    else:
        pdf = latest_pdf()

    if not pdf or not pdf.exists() or pdf.suffix.lower() != ".pdf":
        raise FileNotFoundError("No valid PDF found in data/input.")

    return pdf


def output_url(*parts: str) -> str:
    raw = "/".join(str(part).replace("\\", "/") for part in parts)
    return "/output/" + quote(raw, safe="/")


def manifest_path_for(pdf: Path) -> Path:
    return OUTPUT_DIR / pdf.stem / "figures_hybrid" / "figures_manifest.hybrid.json"


def load_manifest(pdf: Path) -> dict:
    manifest_path = manifest_path_for(pdf)

    if not manifest_path.exists():
        raise FileNotFoundError(f"Hybrid manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for item in manifest.get("figure_crops", []):
        if "path" not in item and item.get("relative_path"):
            item["path"] = str(OUTPUT_DIR / pdf.stem / "figures_hybrid" / item["relative_path"])

    return manifest


def save_manifest(pdf: Path, manifest: dict) -> None:
    manifest_path = manifest_path_for(pdf)
    backup_path = manifest_path.with_suffix(".json.bak")

    if manifest_path.exists() and not backup_path.exists():
        backup_path.write_text(manifest_path.read_text(encoding="utf-8"), encoding="utf-8")

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )




def item_output_path(pdf: Path, item: dict) -> Path:
    raw_path = item.get("path")

    if raw_path:
        return Path(raw_path)

    rel = item.get("relative_path")

    if rel:
        output_path = OUTPUT_DIR / pdf.stem / "figures_hybrid" / rel
        item["path"] = str(output_path)
        return output_path

    raise KeyError("Figure item has neither 'path' nor 'relative_path'.")


def clamp_rect(rect: list[float], page: fitz.Page) -> list[float]:
    x0, y0, x1, y1 = rect

    x0 = max(0, min(page.rect.width, x0))
    x1 = max(0, min(page.rect.width, x1))
    y0 = max(0, min(page.rect.height, y0))
    y1 = max(0, min(page.rect.height, y1))

    min_size = 12

    if x1 - x0 < min_size:
        x1 = min(page.rect.width, x0 + min_size)

    if y1 - y0 < min_size:
        y1 = min(page.rect.height, y0 + min_size)

    return [x0, y0, x1, y1]


def rerender_crop(pdf: Path, item: dict, zoom: float) -> None:
    page_no = int(item["pdf_page"])
    rect = item["crop_rect"]

    doc = fitz.open(pdf)
    page = doc[page_no - 1]

    rect = clamp_rect(rect, page)
    item["crop_rect"] = rect

    clip = fitz.Rect(rect)

    output_path = item_output_path(pdf, item)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(zoom, zoom),
        clip=clip,
        alpha=False,
    )
    pixmap.save(output_path)

    doc.close()


def adjust_item(pdf: Path, index: int, side: str, direction: str, amount: float) -> dict:
    manifest = load_manifest(pdf)
    items = manifest.get("figure_crops", [])

    if index < 0 or index >= len(items):
        raise IndexError("Invalid figure index.")

    item = items[index]
    rect = [float(value) for value in item["crop_rect"]]

    x0, y0, x1, y1 = rect

    if side == "left":
        x0 = x0 - amount if direction == "expand" else x0 + amount

    if side == "right":
        x1 = x1 + amount if direction == "expand" else x1 - amount

    if side == "top":
        y0 = y0 - amount if direction == "expand" else y0 + amount

    if side == "bottom":
        y1 = y1 + amount if direction == "expand" else y1 - amount

    doc = fitz.open(pdf)
    page = doc[int(item["pdf_page"]) - 1]
    item["crop_rect"] = clamp_rect([x0, y0, x1, y1], page)
    doc.close()

    zoom = float(manifest.get("render_zoom") or 3.0)

    rerender_crop(pdf, item, zoom)
    save_manifest(pdf, manifest)

    return item


def item_image_url(pdf: Path, item: dict) -> str:
    rel = Path(item["relative_path"]).as_posix()
    return output_url(pdf.stem, "figures_hybrid", rel)


def rect_label(item: dict) -> str:
    return ", ".join(f"{float(v):.1f}" for v in item.get("crop_rect", []))


def item_is_rejected(item: dict) -> bool:
    return str(item.get("status", "accepted")).strip().lower() == "rejected"


def rebuild_gallery(pdf: Path, manifest: dict) -> None:
    from figure_exporter_hybrid import build_gallery_html

    gallery_path = OUTPUT_DIR / pdf.stem / "figures_hybrid" / "figures_hybrid.html"
    build_gallery_html(manifest, gallery_path)


def set_item_rejection(pdf: Path, index: int, rejected: bool) -> dict:
    manifest = load_manifest(pdf)
    items = manifest.get("figure_crops", [])

    if index < 0 or index >= len(items):
        raise IndexError("Invalid figure index.")

    item = items[index]

    if rejected:
        item["status"] = "rejected"
        item["reject_reason"] = "false_figure"
    else:
        item["status"] = "accepted"
        item.pop("reject_reason", None)

    save_manifest(pdf, manifest)
    rebuild_gallery(pdf, manifest)

    return item


def page(title: str, body: str) -> HTMLResponse:
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg: #e8dfd0;
      --paper: #f5ecd9;
      --paper-soft: #efe3cc;
      --text: #2f2a24;
      --heading: #241e19;
      --muted: #75695c;
      --accent: #8a5a32;
      --border: #d7c5a8;
      --shadow: rgba(62, 45, 28, 0.16);
      --overlay: rgba(31, 25, 18, 0.72);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: linear-gradient(180deg, #eee4d2 0%, var(--bg) 100%);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      line-height: 1.55;
    }}

    body.modal-open {{
      overflow: hidden;
    }}

    main {{
      max-width: 1280px;
      margin: 34px auto;
      padding: 28px;
      background: var(--paper);
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: 0 22px 58px var(--shadow);
    }}

    h1 {{
      margin: 0 0 8px;
      color: var(--heading);
      font-size: 34px;
      letter-spacing: -0.03em;
    }}

    .meta {{
      color: var(--muted);
      margin-bottom: 20px;
    }}

    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 18px 0 24px;
    }}

    .btn,
    button {{
      border: 1px solid var(--border);
      background: var(--paper-soft);
      color: var(--text);
      border-radius: 999px;
      padding: 8px 12px;
      font-weight: 700;
      cursor: pointer;
      text-decoration: none;
      font-size: 13px;
    }}

    button:hover,
    .btn:hover {{
      border-color: var(--accent);
    }}

    button.primary,
    .btn.primary {{
      background: var(--accent);
      color: #fffaf0;
      border-color: var(--accent);
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(390px, 1fr));
      gap: 22px;
    }}

    .card {{
      background: rgba(255,255,255,0.34);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
    }}

    .card h2 {{
      margin: 0 0 8px;
      color: var(--heading);
      font-size: 22px;
    }}

    .card p {{
      margin: 6px 0;
    }}

    img {{
      width: 100%;
      height: auto;
      display: block;
      margin: 14px 0;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: white;
    }}

    .card-actions {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 10px;
    }}

    .fine {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 13px;
    }}

    code {{
      background: var(--paper-soft);
      border: 1px solid var(--border);
      border-radius: 7px;
      padding: 2px 6px;
    }}

    .modal {{
      position: fixed;
      inset: 0;
      z-index: 999;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: var(--overlay);
    }}

    .modal.open {{
      display: flex;
    }}

    .modal-panel {{
      width: min(1180px, 96vw);
      max-height: 94vh;
      overflow: hidden;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 330px;
      gap: 18px;
      background: var(--paper);
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: 0 28px 80px rgba(0,0,0,0.34);
      padding: 20px;
    }}

    .modal-image-wrap {{
      overflow: auto;
      background: rgba(255,255,255,0.34);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 14px;
      max-height: calc(94vh - 40px);
    }}

    .modal-image-wrap img {{
      width: 100%;
      height: auto;
      margin: 0;
    }}

    .modal-side {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-height: calc(94vh - 40px);
      overflow: auto;
    }}

    .modal-side h2 {{
      margin: 0;
      color: var(--heading);
      font-size: 24px;
      line-height: 1.2;
    }}

    .modal-side p {{
      margin: 0;
    }}

    .modal-controls {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}

    .modal-controls button {{
      width: 100%;
    }}

    .amount-box {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      background: var(--paper-soft);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 12px;
    }}

    .amount-box label {{
      font-size: 13px;
      color: var(--muted);
      grid-column: 1 / -1;
    }}

    .amount-box input {{
      width: 100%;
      border: 1px solid var(--border);
      background: var(--paper);
      color: var(--text);
      border-radius: 999px;
      padding: 8px 10px;
      font-weight: 700;
    }}

    .modal-footer {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: auto;
    }}

    .status {{
      min-height: 20px;
      color: var(--muted);
      font-size: 13px;
    }}

    @media (max-width: 860px) {{
      .modal-panel {{
        grid-template-columns: 1fr;
      }}

      .modal-side {{
        max-height: none;
      }}
    }}
  </style>
</head>
<body>
  <main>
    {body}
  </main>
</body>
</html>
"""
    return HTMLResponse(doc)


@app.get("/", response_class=HTMLResponse)
def editor(pdf: str | None = Query(default=None)) -> HTMLResponse:
    try:
        pdf_path = validate_pdf_name(pdf)
        manifest = load_manifest(pdf_path)
    except Exception as exc:
        body = f"""
        <h1>Voila! Crop Editor</h1>
        <div class="meta">Cannot open crop editor.</div>
        <p><strong>Error:</strong> {html.escape(str(exc))}</p>
        <p>First generate hybrid figures for the PDF.</p>
        """
        return page("Voila! Crop Editor", body)

    items = manifest.get("figure_crops", [])
    accepted_count = sum(1 for item in items if not item_is_rejected(item))
    rejected_count = len(items) - accepted_count
    cards = []

    for index, item in enumerate(items):
        src = item_image_url(pdf_path, item)
        image_path = item_output_path(pdf_path, item)
        mtime = image_path.stat().st_mtime if image_path.exists() else time.time()

        number = html.escape(str(item.get("number", "")))
        caption = html.escape(str(item.get("caption", "")))
        pdf_page = html.escape(str(item.get("pdf_page", "")))
        method = html.escape(str(item.get("crop_method", "")))
        rect = html.escape(rect_label(item))
        rejected = item_is_rejected(item)
        card_class = "card rejected" if rejected else "card"
        status_label = '<p class="meta rejected-label">Rejected as false figure</p>' if rejected else ""
        action_label = "Restore" if rejected else "Mark as false figure"
        action_rejected = "false" if rejected else "true"
        action_class = "" if rejected else "danger"

        cards.append(
            f"""
            <article class="{card_class}" id="card-{index}">
              <h2>Figure {number}</h2>
              <p class="caption">{caption}</p>
              <p class="meta">PDF page {pdf_page} · {method}</p>
              {status_label}
              <img id="card-img-{index}" src="{src}?v={mtime}" alt="Figure {number}">
              <div class="card-actions">
                <button class="primary" type="button" onclick="openEditor({index})">Edit crop</button>
                <button class="{action_class}" type="button" onclick="markFalseFigure({index}, {action_rejected})">{action_label}</button>
              </div>
              <div class="fine">
                crop_rect: <code id="card-rect-{index}">{rect}</code>
              </div>
            </article>
            """
        )

    gallery_url = output_url(pdf_path.stem, "figures_hybrid", "figures_hybrid.html")
    items_json = json.dumps(items, ensure_ascii=False)

    body = f"""
    <style>
      .card.rejected {{
        display: none;
        opacity: 0.72;
        border-style: dashed;
      }}

      body.show-rejected .card.rejected {{
        display: block;
      }}

      .rejected-label {{
        color: #8a3a2b;
        font-weight: 700;
      }}

      button.danger {{
        border-color: #9b3b30;
        color: #7a2c24;
      }}
    </style>

    <h1>Voila! Crop Editor</h1>
    <div class="meta">
      PDF: <code>{html.escape(pdf_path.name)}</code><br>
      Accepted figures: {accepted_count} · Rejected false figures: {rejected_count} · Total: {len(items)}
    </div>
    <div class="toolbar">
      <a class="btn primary" href="{gallery_url}">Open hybrid gallery</a>
      <a class="btn" href="http://127.0.0.1:8787">Back to Voila!</a>
      <label class="btn"><input id="showRejectedToggle" type="checkbox" onchange="toggleRejected()"> Show rejected</label>
    </div>

    <div class="grid">
      {''.join(cards)}
    </div>

    <div class="modal" id="cropModal" onclick="overlayClose(event)">
      <div class="modal-panel">
        <div class="modal-image-wrap">
          <img id="modalImage" src="" alt="">
        </div>

        <aside class="modal-side">
          <h2 id="modalTitle">Figure</h2>
          <p id="modalCaption"></p>
          <p class="meta" id="modalMeta"></p>

          <div class="amount-box">
            <label for="amountInput">Adjustment amount in PDF units</label>
            <input id="amountInput" type="number" min="1" step="1" value="16">
            <button type="button" onclick="setAmount(8)">Fine 8</button>
            <button type="button" onclick="setAmount(24)">Coarse 24</button>
          </div>

          <div class="modal-controls">
            <button type="button" onclick="adjustCrop('left', 'expand')">← Expand left</button>
            <button type="button" onclick="adjustCrop('left', 'shrink')">Shrink left →</button>
            <button type="button" onclick="adjustCrop('right', 'shrink')">← Shrink right</button>
            <button type="button" onclick="adjustCrop('right', 'expand')">Expand right →</button>
            <button type="button" onclick="adjustCrop('top', 'expand')">↑ Expand top</button>
            <button type="button" onclick="adjustCrop('top', 'shrink')">Shrink top ↓</button>
            <button type="button" onclick="adjustCrop('bottom', 'shrink')">↑ Shrink bottom</button>
            <button type="button" onclick="adjustCrop('bottom', 'expand')">Expand bottom ↓</button>
          </div>

          <div class="fine">
            crop_rect: <code id="modalRect"></code>
          </div>

          <div class="status" id="modalStatus"></div>

          <div class="modal-footer">
            <button id="modalRejectButton" class="danger" type="button" onclick="toggleCurrentRejected()">Mark as false figure</button>
            <button type="button" onclick="previousFigure()">← Previous</button>
            <button type="button" onclick="nextFigure()">Next →</button>
            <button class="primary" type="button" onclick="closeEditor()">Close</button>
          </div>
        </aside>
      </div>
    </div>

    <script>
      const pdfName = {json.dumps(pdf_path.name)};
      const pdfStem = {json.dumps(pdf_path.stem)};
      let items = {items_json};
      let currentIndex = 0;

      function imageUrl(item) {{
        const rel = item.relative_path.replaceAll("\\\\", "/");
        const base = "/output/" + encodeURIComponent(pdfStem) + "/figures_hybrid/" + rel;
        return base + "?v=" + Date.now();
      }}

      function rectText(item) {{
        return (item.crop_rect || []).map(v => Number(v).toFixed(1)).join(", ");
      }}

      function isRejected(item) {{
        return String(item.status || "accepted").toLowerCase() === "rejected";
      }}

      function openEditor(index) {{
        currentIndex = index;
        const modal = document.getElementById("cropModal");
        document.body.classList.add("modal-open");
        modal.classList.add("open");
        renderModal();
      }}

      function closeEditor() {{
        document.getElementById("cropModal").classList.remove("open");
        document.body.classList.remove("modal-open");
      }}

      function overlayClose(event) {{
        if (event.target.id === "cropModal") {{
          closeEditor();
        }}
      }}

      function renderModal() {{
        const item = items[currentIndex];

        document.getElementById("modalTitle").textContent = "Figure " + item.number;
        document.getElementById("modalCaption").textContent = item.caption || "";
        document.getElementById("modalMeta").textContent = "PDF page " + item.pdf_page + " · " + item.crop_method;
        document.getElementById("modalRect").textContent = rectText(item);
        document.getElementById("modalImage").src = imageUrl(item);

        const rejected = isRejected(item);
        document.getElementById("modalStatus").textContent = rejected ? "Rejected as false figure." : "";
        document.getElementById("modalRejectButton").textContent = rejected ? "Restore" : "Mark as false figure";
      }}

      function setAmount(value) {{
        document.getElementById("amountInput").value = value;
      }}

      async function adjustCrop(side, direction) {{
        const amount = document.getElementById("amountInput").value || "16";
        const status = document.getElementById("modalStatus");
        status.textContent = "Updating...";

        const formData = new FormData();
        formData.append("pdf_name", pdfName);
        formData.append("index", String(currentIndex));
        formData.append("side", side);
        formData.append("direction", direction);
        formData.append("amount", amount);

        const response = await fetch("/adjust-json", {{
          method: "POST",
          body: formData
        }});

        if (!response.ok) {{
          status.textContent = "Update failed.";
          return;
        }}

        const data = await response.json();
        items[currentIndex] = data.item;

        const item = items[currentIndex];
        const newUrl = imageUrl(item);

        document.getElementById("modalImage").src = newUrl;
        document.getElementById("modalRect").textContent = rectText(item);

        const cardImg = document.getElementById("card-img-" + currentIndex);
        const cardRect = document.getElementById("card-rect-" + currentIndex);

        if (cardImg) {{
          cardImg.src = newUrl;
        }}

        if (cardRect) {{
          cardRect.textContent = rectText(item);
        }}

        status.textContent = "Updated.";
      }}

      async function markFalseFigure(index, rejected) {{
        const formData = new FormData();
        formData.append("pdf_name", pdfName);
        formData.append("index", String(index));
        formData.append("rejected", rejected ? "true" : "false");

        const response = await fetch("/figure-status-json", {{
          method: "POST",
          body: formData
        }});

        if (!response.ok) {{
          alert("Could not update figure status.");
          return;
        }}

        window.location.reload();
      }}

      function toggleCurrentRejected() {{
        const item = items[currentIndex];
        markFalseFigure(currentIndex, !isRejected(item));
      }}

      function toggleRejected() {{
        const checked = document.getElementById("showRejectedToggle").checked;
        document.body.classList.toggle("show-rejected", checked);
      }}

      function previousFigure() {{
        if (currentIndex > 0) {{
          currentIndex -= 1;
          renderModal();
        }}
      }}

      function nextFigure() {{
        if (currentIndex < items.length - 1) {{
          currentIndex += 1;
          renderModal();
        }}
      }}

      document.addEventListener("keydown", function(event) {{
        const modalOpen = document.getElementById("cropModal").classList.contains("open");

        if (!modalOpen) return;

        if (event.key === "Escape") {{
          closeEditor();
        }}

        if (event.key === "ArrowLeft") {{
          previousFigure();
        }}

        if (event.key === "ArrowRight") {{
          nextFigure();
        }}
      }});
    </script>
    """

    return page("Voila! Crop Editor", body)


@app.post("/figure-status-json")
def figure_status_json(
    pdf_name: str = Form(...),
    index: int = Form(...),
    rejected: bool = Form(...),
) -> JSONResponse:
    pdf_path = validate_pdf_name(pdf_name)
    item = set_item_rejection(pdf_path, index, rejected)

    return JSONResponse(
        {
            "ok": True,
            "item": item,
        }
    )


@app.post("/adjust-json")
def adjust_json(
    pdf_name: str = Form(...),
    index: int = Form(...),
    side: str = Form(...),
    direction: str = Form(...),
    amount: float = Form(...),
) -> JSONResponse:
    pdf_path = validate_pdf_name(pdf_name)
    item = adjust_item(pdf_path, index, side, direction, amount)

    return JSONResponse(
        {
            "ok": True,
            "item": item,
        }
    )


@app.post("/adjust")
def adjust(
    pdf_name: str = Form(...),
    index: int = Form(...),
    side: str = Form(...),
    direction: str = Form(...),
    amount: float = Form(...),
) -> RedirectResponse:
    pdf_path = validate_pdf_name(pdf_name)
    adjust_item(pdf_path, index, side, direction, amount)

    return RedirectResponse(
        url="/?pdf=" + quote(pdf_path.name),
        status_code=303,
    )
