from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

route_start = text.find('@app.get("/review-ocr-text")')
route_end = text.find('@app.post("/review-ocr-text/save")', route_start)

if route_start == -1 or route_end == -1:
    raise SystemExit("Could not find Review OCR Text route.")

segment = text[route_start:route_end]

marker = "    /* VS Code style OCR autocomplete */"
css_start = segment.find(marker)

if css_start == -1:
    raise SystemExit("Could not find VS Code autocomplete CSS marker.")

style_end = segment.find("\n  </style>", css_start)

if style_end == -1:
    style_end = segment.find("</style>", css_start)

if style_end == -1:
    raise SystemExit("Could not find </style> after autocomplete CSS.")

safe_css = r'''
    /* VS Code style OCR autocomplete */
    .ocr-suggestions {{
      position: fixed !important;
      z-index: 3000 !important;
      display: block !important;
      min-width: 280px;
      max-width: min(520px, calc(100vw - 24px));
      max-height: 280px;
      overflow-y: auto;
      padding: 6px;
      background: #1b2529;
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: 0 18px 48px rgba(0,0,0,0.45);
    }}

    .ocr-suggestions[hidden] {{
      display: none !important;
    }}

    .ocr-suggestion {{
      display: block !important;
      width: 100%;
      border: 0;
      border-radius: 8px;
      padding: 9px 12px;
      background: transparent;
      color: var(--text);
      text-align: left;
      font-weight: 800;
      font-size: 15px;
      cursor: pointer;
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
    }}

    .ocr-suggestion:hover,
    .ocr-suggestion.active,
    .ocr-suggestion.primary {{
      background: var(--accent);
      color: white;
    }}

    .ocr-suggestion small {{
      display: block;
      color: rgba(255,255,255,0.70);
      font-weight: 700;
      margin-top: 2px;
    }}
'''

segment = segment[:css_start] + safe_css + segment[style_end:]

text = text[:route_start] + segment + text[route_end:]

path.write_text(text, encoding="utf-8")
print("OK: replaced bad VS Code autocomplete CSS block with f-string-safe CSS.")
