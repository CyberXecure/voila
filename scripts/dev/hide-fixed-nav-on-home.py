from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

script = '''
    <script id="hide-fixed-nav-on-home">
      (function () {{
        const nav = document.getElementById("appFixedNav");

        if (!nav) {{
          return;
        }}

        const path = window.location.pathname;

        if (path === "/" || path === "") {{
          nav.hidden = true;
          document.body.style.paddingBottom = "0";
        }}
      }})();
    </script>
'''

if "hide-fixed-nav-on-home" not in text:
    text = text.replace("</body>", script + "\n</body>", 1)

path.write_text(text, encoding="utf-8")

print("OK: fixed navigation hidden on home page.")
