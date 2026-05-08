from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

start = text.find('@app.get("/review-ocr-text")')
end = text.find('@app.post("/review-ocr-text/save")', start)

if start == -1 or end == -1:
    raise SystemExit("Could not find review OCR text route.")

segment = text[start:end]

old_image = '''    image_html = (
        f'<img class="scan-img" src="{_html_escape(image_url)}" alt="OCR source page {page}">'
        if image_url
        else '<div class="no-img">No rendered page image found for this page.</div>'
    )
'''

new_image = '''    image_html = (
        f"""
        <div class="scan-shell">
          <div class="scan-toolbar">
            <button type="button" onclick="zoomScan(-0.15)">−</button>
            <button type="button" onclick="resetScanZoom()">100%</button>
            <button type="button" onclick="fitScanWidth()">Fit width</button>
            <button type="button" onclick="zoomScan(0.15)">+</button>
            <span class="zoom-pill" data-zoom-label>100%</span>
          </div>

          <div class="scan-viewport" id="scanViewport">
            <img id="scanImage" class="scan-img" src="{_html_escape(image_url)}" alt="OCR source page {page}">
          </div>

          <div class="scan-floating-zoom">
            <button type="button" onclick="zoomScan(-0.15)">−</button>
            <button type="button" onclick="resetScanZoom()">100%</button>
            <button type="button" onclick="fitScanWidth()">Fit</button>
            <button type="button" onclick="zoomScan(0.15)">+</button>
            <span class="zoom-pill" data-zoom-label>100%</span>
          </div>
        </div>
        """
        if image_url
        else '<div class="no-img">No rendered page image found for this page.</div>'
    )
'''

if old_image not in segment:
    raise SystemExit("Could not find image_html block to replace.")

segment = segment.replace(old_image, new_image)

old_css = '''    .scan-img {{
      width: 100%;
      max-height: 82vh;
      object-fit: contain;
      background: #f2ead8;
      border-radius: 18px;
      border: 1px solid var(--line);
    }}
'''

new_css = '''    .scan-shell {{
      position: relative;
    }}

    .scan-toolbar {{
      position: sticky;
      top: 10px;
      z-index: 20;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
      margin-bottom: 12px;
      padding: 10px;
      background: rgba(32, 45, 49, 0.96);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 10px 28px rgba(0,0,0,0.22);
    }}

    .scan-toolbar button,
    .scan-floating-zoom button {{
      padding: 9px 13px;
      min-width: 44px;
      border-radius: 999px;
      font-size: 15px;
      line-height: 1;
    }}

    .zoom-pill {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 8px 12px;
      border-radius: 999px;
      background: #142022;
      border: 1px solid var(--line);
      color: var(--muted);
      font-weight: 900;
      min-width: 68px;
    }}

    .scan-viewport {{
      width: 100%;
      height: 78vh;
      overflow: auto;
      background: #f2ead8;
      border-radius: 18px;
      border: 1px solid var(--line);
      overscroll-behavior: contain;
    }}

    .scan-img {{
      display: block;
      width: auto;
      max-width: none;
      height: auto;
      max-height: none;
      background: #f2ead8;
      border: 0;
      border-radius: 0;
      transform-origin: top left;
      user-select: none;
    }}

    .scan-floating-zoom {{
      position: fixed;
      right: 18px;
      bottom: 92px;
      z-index: 1000;
      display: flex;
      gap: 8px;
      align-items: center;
      padding: 10px;
      background: rgba(32, 45, 49, 0.96);
      border: 1px solid var(--line);
      border-radius: 999px;
      box-shadow: 0 18px 48px rgba(0,0,0,0.35);
    }}
'''

if old_css not in segment:
    raise SystemExit("Could not find .scan-img CSS block to replace.")

segment = segment.replace(old_css, new_css)

js = '''
  <script>
    let scanZoom = 1.0;

    function getScanElements() {{
      return {{
        img: document.getElementById("scanImage"),
        viewport: document.getElementById("scanViewport")
      }};
    }}

    function updateZoomLabels() {{
      const label = Math.round(scanZoom * 100) + "%";
      document.querySelectorAll("[data-zoom-label]").forEach((el) => {{
        el.textContent = label;
      }});
    }}

    function applyScanZoom() {{
      const {{ img }} = getScanElements();

      if (!img) {{
        return;
      }}

      const naturalWidth = img.naturalWidth || img.width || 1000;
      img.style.width = Math.max(120, naturalWidth * scanZoom) + "px";
      updateZoomLabels();
    }}

    function zoomScan(delta) {{
      scanZoom = Math.min(4.0, Math.max(0.25, scanZoom + delta));
      applyScanZoom();
    }}

    function resetScanZoom() {{
      scanZoom = 1.0;
      applyScanZoom();
    }}

    function fitScanWidth() {{
      const {{ img, viewport }} = getScanElements();

      if (!img || !viewport) {{
        return;
      }}

      const naturalWidth = img.naturalWidth || img.width || 1000;
      const availableWidth = Math.max(240, viewport.clientWidth - 24);

      scanZoom = Math.min(4.0, Math.max(0.25, availableWidth / naturalWidth));
      applyScanZoom();
      viewport.scrollLeft = 0;
    }}

    window.addEventListener("load", () => {{
      applyScanZoom();
    }});

    document.addEventListener("wheel", (event) => {{
      const viewport = document.getElementById("scanViewport");

      if (!viewport || !event.ctrlKey) {{
        return;
      }}

      if (!viewport.contains(event.target)) {{
        return;
      }}

      event.preventDefault();
      zoomScan(event.deltaY < 0 ? 0.12 : -0.12);
    }}, {{ passive: false }});
  </script>
'''

if "function fitScanWidth()" not in segment:
    segment = segment.replace("</body>", js + "\n</body>")

text = text[:start] + segment + text[end:]

path.write_text(text, encoding="utf-8")
print("OK: floating zoom added to Review OCR Text.")
