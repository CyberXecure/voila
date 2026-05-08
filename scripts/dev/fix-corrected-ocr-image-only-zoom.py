from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

old = """    main {
      display: grid;
      grid-template-columns: minmax(420px, 1fr) minmax(420px, 1fr);
      gap: 16px;
      padding: 16px;
      height: calc(100vh - 76px);
    }"""

new = """    main {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 16px;
      padding: 16px;
      height: calc(100vh - 76px);
      overflow: hidden;
    }"""

text = text.replace(old, new)

old = """    .pane {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      overflow: hidden;
      min-height: 0;
    }"""

new = """    .pane {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      overflow: hidden;
      min-height: 0;
      min-width: 0;
    }"""

text = text.replace(old, new)

old = """    .scan-wrap img {
      max-width: none;
      width: 100%;
      display: block;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,.35);
    }"""

new = """    .scan-wrap img {
      max-width: none;
      width: var(--scan-zoom, 100%);
      display: block;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,.35);
      user-select: none;
      pointer-events: none;
    }"""

text = text.replace(old, new)

text = text.replace(
    "Tip: Ctrl + mouse wheel zoom, drag with mouse to pan",
    "Tip: Ctrl + mouse wheel = zoom doar pe imagine; click + drag = mută pagina"
)

old = """    const box = document.getElementById('scanWrap');
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
    }});"""

new = """    const box = document.getElementById('scanWrap');
    const img = box.querySelector('img');

    let isDown = false;
    let startX = 0;
    let startY = 0;
    let scrollLeft = 0;
    let scrollTop = 0;
    let scanZoom = 100;

    function setScanZoom(nextZoom) {{
      scanZoom = Math.max(45, Math.min(260, nextZoom));
      img.style.setProperty('--scan-zoom', scanZoom + '%');
    }}

    // Ctrl + mouse wheel zooms ONLY the scanned image.
    // It does not trigger browser zoom and does not resize the OCR editor pane.
    box.addEventListener('wheel', (e) => {{
      if (!e.ctrlKey) return;

      e.preventDefault();
      e.stopPropagation();

      const beforeX = box.scrollLeft + e.offsetX;
      const beforeY = box.scrollTop + e.offsetY;
      const oldZoom = scanZoom;

      const direction = e.deltaY < 0 ? 12 : -12;
      setScanZoom(scanZoom + direction);

      const ratio = scanZoom / oldZoom;
      box.scrollLeft = beforeX * ratio - e.offsetX;
      box.scrollTop = beforeY * ratio - e.offsetY;
    }}, {{ passive: false }});

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
    }});"""

if old not in text:
    raise SystemExit("Could not find scan JS block to replace.")

text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
print("OK: corrected OCR review zoom is now image-only and layout-stable.")
