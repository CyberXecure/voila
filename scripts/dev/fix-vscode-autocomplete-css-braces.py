from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

start = text.find('@app.get("/review-ocr-text")')
end = text.find('@app.post("/review-ocr-text/save")', start)

if start == -1 or end == -1:
    raise SystemExit("Could not find Review OCR Text route.")

segment = text[start:end]

new_vs_css = r'''
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

pattern = r'''
    /\* VS Code style OCR autocomplete \*/.*?
    \.ocr-suggestion\s+small\s*\{.*?
    \n\s*\}
'''

segment, count = re.subn(
    pattern,
    new_vs_css,
    segment,
    flags=re.DOTALL | re.VERBOSE,
)

if count == 0:
    # Fallback: insert the safe block before </style> if the old block was not found.
    if "VS Code style OCR autocomplete" not in segment:
        segment = segment.replace("</style>", new_vs_css + "\n  </style>")
    else:
        raise SystemExit("Found autocomplete marker but could not replace CSS block safely.")

text = text[:start] + segment + text[end:]

path.write_text(text, encoding="utf-8")
print("OK: fixed VS Code autocomplete CSS braces for Python f-string.")
