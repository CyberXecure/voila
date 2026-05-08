from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

page_start = text.find("def page(")
page_end = text.find("\n\ndef ", page_start + 1)

if page_start == -1:
    raise SystemExit("Could not find page() function.")

if page_end == -1:
    page_end = len(text)

segment = text[page_start:page_end]

safe_css = r'''
<style>
  .primary-tool {{
    background: #e0ad68 !important;
    color: #fff !important;
    border-color: transparent !important;
    font-weight: 900 !important;
  }}

  .tool-link {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    padding: 10px 14px;
    margin: 4px;
    text-decoration: none;
  }}
</style>
'''

# Replace bad CSS block inside page() only.
segment, count = re.subn(
    r'''
<style>\s*
\s*\.primary-tool\s*\{.*?
\s*\.tool-link\s*\{.*?
</style>
''',
    safe_css,
    segment,
    flags=re.DOTALL | re.VERBOSE,
)

if count == 0:
    print("No bad primary-tool CSS block found inside page(). Nothing replaced.")
else:
    print(f"Replaced bad primary-tool CSS block: {count}")

text = text[:page_start] + segment + text[page_end:]

path.write_text(text, encoding="utf-8")
print("OK: homepage CSS braces fixed.")
