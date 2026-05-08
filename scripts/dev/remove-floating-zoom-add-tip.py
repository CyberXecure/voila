from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

start = text.find('@app.get("/review-ocr-text")')
end = text.find('@app.post("/review-ocr-text/save")', start)

if start == -1 or end == -1:
    raise SystemExit("Could not find Review OCR Text route.")

segment = text[start:end]

# 1. Remove the floating zoom HTML block completely.
segment = re.sub(
    r'\s*<div class="scan-floating-zoom">\s*.*?\s*</div>\s*',
    "\n",
    segment,
    flags=re.DOTALL,
)

# 2. Remove or neutralize floating zoom CSS.
segment = re.sub(
    r'\s*\.scan-floating-zoom\s*\{\{.*?\n\s*\}\}\s*',
    '''
    .scan-floating-zoom {{
      display: none !important;
      visibility: hidden !important;
      pointer-events: none !important;
    }}
''',
    segment,
    flags=re.DOTALL,
)

# 3. Add user tip in the scan toolbar.
if "scan-tip" not in segment:
    segment = segment.replace(
'''            <span class="zoom-pill" data-zoom-label>100%</span>
''',
'''            <span class="zoom-pill" data-zoom-label>100%</span>
            <span class="scan-tip">Tip: Ctrl + mouse wheel = zoom · click + drag = move page</span>
'''
    )

# 4. Add scan tip CSS.
if ".scan-tip {{" not in segment:
    segment = segment.replace(
'''    .zoom-pill {{
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
''',
'''    .zoom-pill {{
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

    .scan-tip {{
      color: var(--muted);
      font-weight: 800;
      font-size: 14px;
      padding: 8px 10px;
    }}
'''
    )

# 5. Safety cleanup on page load in case cached HTML still contains old block.
if 'document.querySelectorAll(".scan-floating-zoom")' not in segment:
    segment = segment.replace(
'''    window.addEventListener("load", () => {{
      applyScanZoom();
      enableScanPan();
    }});
''',
'''    window.addEventListener("load", () => {{
      document.querySelectorAll(".scan-floating-zoom").forEach((el) => el.remove());
      applyScanZoom();
      enableScanPan();
    }});
'''
    )

text = text[:start] + segment + text[end:]

path.write_text(text, encoding="utf-8")
print("OK: floating zoom removed from HTML/CSS and scan usage tip added.")
