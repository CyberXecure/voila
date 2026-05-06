from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# 1. Ensure hidden nav really stays hidden.
css_fix = '''
    .app-fixed-nav[hidden] {{
      display: none !important;
    }}
'''

if ".app-fixed-nav[hidden]" not in text:
    text = text.replace("    .app-fixed-nav [hidden] {{", css_fix + "\n    .app-fixed-nav [hidden] {{", 1)

# 2. Replace previous home-hide script with stronger script.
old_start = text.find('<script id="hide-fixed-nav-on-home">')
if old_start != -1:
    old_end = text.find("</script>", old_start)
    if old_end != -1:
        old_end += len("</script>")
        text = text[:old_start] + text[old_end:]

script = '''
    <script id="hide-fixed-nav-on-home">
      (function () {{
        function hideHomeNav() {{
          const path = window.location.pathname;
          const nav = document.getElementById("appFixedNav");

          if ((path === "/" || path === "") && nav) {{
            nav.remove();
            document.body.style.paddingBottom = "0";
          }}
        }}

        hideHomeNav();

        if (document.readyState === "loading") {{
          document.addEventListener("DOMContentLoaded", hideHomeNav);
        }} else {{
          hideHomeNav();
        }}
      }})();
    </script>
'''

text = text.replace("</body>", script + "\n</body>", 1)

path.write_text(text, encoding="utf-8")

print("OK: fixed nav is now fully removed on Home page.")
