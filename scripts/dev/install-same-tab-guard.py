from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

script = '''
    <script>
      (function () {{
        document.addEventListener("click", function (event) {{
          const link = event.target.closest("a");

          if (!link) {{
            return;
          }}

          const href = link.getAttribute("href") || "";

          if (
            href.startsWith("/") ||
            href.startsWith("http://127.0.0.1") ||
            href.startsWith("http://localhost")
          ) {{
            link.removeAttribute("target");
          }}
        }});
      }})();
    </script>
'''

if "same-tab-navigation" not in text:
    script = script.replace("<script>", '<script id="same-tab-navigation">')
    text = text.replace("</body>", script + "\n</body>", 1)

path.write_text(text, encoding="utf-8")
print("OK: same-tab navigation guard added to web_app.py.")
