from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# 1. Hide/remove floating zoom visually.
if ".scan-floating-zoom {{" in text and "display: none !important;" not in text:
    text = text.replace(
'''    .scan-floating-zoom {{
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
''',
'''    .scan-floating-zoom {{
      display: none !important;
    }}
'''
    )

# 2. Add hand/pan cursor to scan viewport.
if "cursor: grab;" not in text:
    text = text.replace(
'''    .scan-viewport {{
      width: 100%;
      height: 78vh;
      overflow: auto;
      background: #f2ead8;
      border-radius: 18px;
      border: 1px solid var(--line);
      overscroll-behavior: contain;
    }}
''',
'''    .scan-viewport {{
      width: 100%;
      height: 78vh;
      overflow: auto;
      background: #f2ead8;
      border-radius: 18px;
      border: 1px solid var(--line);
      overscroll-behavior: contain;
      cursor: grab;
      touch-action: none;
    }}

    .scan-viewport.dragging {{
      cursor: grabbing;
    }}
'''
    )

# 3. Prevent browser image dragging.
if "-webkit-user-drag: none;" not in text:
    text = text.replace(
'''    .scan-img {{
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
''',
'''    .scan-img {{
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
      -webkit-user-drag: none;
      pointer-events: none;
    }}
'''
    )

# 4. Add drag-to-pan JS.
marker = '''    document.addEventListener("wheel", (event) => {{
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
'''

pan_js = '''    function enableScanPan() {{
      const viewport = document.getElementById("scanViewport");

      if (!viewport || viewport.dataset.panEnabled === "1") {{
        return;
      }}

      viewport.dataset.panEnabled = "1";

      let isDragging = false;
      let startX = 0;
      let startY = 0;
      let startScrollLeft = 0;
      let startScrollTop = 0;

      viewport.addEventListener("pointerdown", (event) => {{
        isDragging = true;
        startX = event.clientX;
        startY = event.clientY;
        startScrollLeft = viewport.scrollLeft;
        startScrollTop = viewport.scrollTop;
        viewport.classList.add("dragging");
        viewport.setPointerCapture(event.pointerId);
        event.preventDefault();
      }});

      viewport.addEventListener("pointermove", (event) => {{
        if (!isDragging) {{
          return;
        }}

        const dx = event.clientX - startX;
        const dy = event.clientY - startY;

        viewport.scrollLeft = startScrollLeft - dx;
        viewport.scrollTop = startScrollTop - dy;
        event.preventDefault();
      }});

      function stopDragging(event) {{
        if (!isDragging) {{
          return;
        }}

        isDragging = false;
        viewport.classList.remove("dragging");

        try {{
          viewport.releasePointerCapture(event.pointerId);
        }} catch (_) {{}}
      }}

      viewport.addEventListener("pointerup", stopDragging);
      viewport.addEventListener("pointercancel", stopDragging);
      viewport.addEventListener("pointerleave", stopDragging);
    }}

'''

if "function enableScanPan()" not in text:
    text = text.replace(marker, pan_js + marker)

# 5. Call pan setup on load.
text = text.replace(
'''    window.addEventListener("load", () => {{
      applyScanZoom();
    }});
''',
'''    window.addEventListener("load", () => {{
      applyScanZoom();
      enableScanPan();
    }});
'''
)

path.write_text(text, encoding="utf-8")
print("OK: removed floating zoom and added hand drag/pan for scanned pages.")
