from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# 1. Replace direct static course links with dynamic /view-course where possible.
text = re.sub(
    r'href="([^"]*?/output/([^"/]+?)/course\.cleaned\.html)"',
    lambda m: f'href="/view-course?pdf={m.group(2)}.pdf"',
    text,
)

text = re.sub(
    r"href='([^']*?/output/([^'/]+?)/course\.cleaned\.html)'",
    lambda m: f"href='/view-course?pdf={m.group(2)}.pdf'",
    text,
)

# 2. Replace direct static figures links with dynamic /view-figures where possible.
text = re.sub(
    r'href="([^"]*?/output/([^"/]+?)/figures_hybrid/figures_hybrid\.html)"',
    lambda m: f'href="/view-figures?pdf={m.group(2)}.pdf"',
    text,
)

text = re.sub(
    r"href='([^']*?/output/([^'/]+?)/figures_hybrid/figures_hybrid\.html)'",
    lambda m: f"href='/view-figures?pdf={m.group(2)}.pdf'",
    text,
)

# 3. Make sure the Course Tools route exists before patching UI references.
if "_voila_tools_bar" not in text:
    raise SystemExit("Course Tools helpers are missing. Add /course-tools first.")

# 4. Add a small helper for course-card actions if missing.
if "def _course_tools_button_html(" not in text:
    helper = r'''

def _course_tools_button_html(pdf_name: str) -> str:
    from urllib.parse import quote
    safe = Path(str(pdf_name or "")).name
    q = quote(safe)
    return f'<a class="tool-link primary-tool" href="/course-tools?pdf={q}">Course Tools</a>'
'''
    marker = "def _voila_tools_bar("
    pos = text.find(marker)
    text = text[:pos] + helper + "\n\n" + text[pos:]

# 5. Add CSS for Course Tools buttons if library CSS has buttons/cards.
if ".primary-tool" not in text:
    css = r'''
<style>
  .primary-tool {
    background: #e0ad68 !important;
    color: #fff !important;
    border-color: transparent !important;
    font-weight: 900 !important;
  }

  .tool-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    padding: 10px 14px;
    margin: 4px;
    text-decoration: none;
  }
</style>
'''
    # Insert globally before the first </head> occurrence in generated home HTML, if any.
    text = text.replace("</head>", css + "\n</head>", 1)

path.write_text(text, encoding="utf-8")
print("OK: static course/figure links patched toward dynamic Course Tools-compatible routes.")
