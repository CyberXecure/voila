from pathlib import Path
import re
import time

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

route_start = text.find("def voila_review_ocr_corrected(")
if route_start == -1:
    raise SystemExit("Nu găsesc ruta voila_review_ocr_corrected.")

next_route = text.find("\n@app.", route_start + 1)
if next_route == -1:
    next_route = len(text)

route = text[route_start:next_route]

# Remove old Monaco includes from this route only.
route = re.sub(
    r'\s*<link rel="stylesheet" href="/voila-static/ocr_review_monaco\.css[^"]*">\n?',
    "\n",
    route,
)

route = re.sub(
    r'\s*<script defer src="/voila-static/ocr_review_monaco\.js[^"]*"></script>\n?',
    "\n",
    route,
)

route = re.sub(
    r'\s*<script src="/voila-static/ocr_review_monaco\.js[^"]*"></script>\n?',
    "\n",
    route,
)

stamp = str(int(time.time()))

css_include = f'  <link rel="stylesheet" href="/voila-static/ocr_review_monaco.css?v={stamp}">\n'
js_include = f'  <script src="/voila-static/ocr_review_monaco.js?v={stamp}"></script>\n'

if "</head>" not in route:
    raise SystemExit("Nu găsesc </head> în OCR review.")

if "</body>" not in route:
    raise SystemExit("Nu găsesc </body> în OCR review.")

route = route.replace("</head>", css_include + "</head>", 1)
route = route.replace("</body>", js_include + "</body>", 1)

text = text[:route_start] + route + text[next_route:]

path.write_text(text, encoding="utf-8")
print("OK: Monaco static includes moved to stable positions with cache busting.")
