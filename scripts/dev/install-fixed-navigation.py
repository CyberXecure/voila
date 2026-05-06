from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# Remove old floating nav CSS blocks.
text = re.sub(
    r"\n\s*\.floating-nav\s*\{\{.*?@media\s*\(max-width:\s*760px\)\s*\{\{.*?\n\s*\}\}\s*\n",
    "\n",
    text,
    flags=re.DOTALL,
)

# Remove old floating nav HTML blocks.
text = re.sub(
    r"\n\s*<div class=\"floating-nav\".*?</div>\s*\n",
    "\n",
    text,
    flags=re.DOTALL,
)

# Remove any previous app fixed nav, if rerun.
text = re.sub(
    r"\n\s*/\*\s*Voila fixed navigation\s*\*/.*?/\*\s*End Voila fixed navigation\s*\*/\s*\n",
    "\n",
    text,
    flags=re.DOTALL,
)

text = re.sub(
    r"\n\s*<nav id=\"appFixedNav\".*?</script>\s*\n",
    "\n",
    text,
    flags=re.DOTALL,
)

css = '''
    /* Voila fixed navigation */
    body {{
      padding-bottom: 108px;
    }}

    .app-fixed-nav {{
      position: fixed;
      left: 50%;
      bottom: calc(18px + env(safe-area-inset-bottom));
      transform: translateX(-50%);
      z-index: 2147483000;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      max-width: calc(100vw - 32px);
      padding: 10px;
      background: rgba(24, 33, 35, 0.88);
      border: 1px solid var(--border);
      border-radius: 999px;
      box-shadow: 0 18px 48px rgba(0,0,0,0.36);
      backdrop-filter: blur(10px);
    }}

    .app-fixed-nav a,
    .app-fixed-nav button {{
      border: 1px solid var(--border);
      background: var(--paper-soft);
      color: var(--text);
      border-radius: 999px;
      padding: 9px 14px;
      font-weight: 800;
      cursor: pointer;
      text-decoration: none;
      font-size: 14px;
      white-space: nowrap;
      line-height: 1;
    }}

    .app-fixed-nav a.primary,
    .app-fixed-nav button.primary {{
      background: var(--accent);
      color: #fffaf0;
      border-color: var(--accent);
    }}

    .app-fixed-nav button.danger {{
      background: rgba(151, 75, 58, 0.92);
      color: #fffaf0;
      border-color: rgba(151, 75, 58, 0.92);
    }}

    .app-fixed-nav a:hover,
    .app-fixed-nav button:hover {{
      transform: translateY(-1px);
      filter: brightness(1.04);
    }}

    .app-fixed-nav [hidden] {{
      display: none !important;
    }}

    @media (max-width: 760px) {{
      body {{
        padding-bottom: 142px;
      }}

      .app-fixed-nav {{
        left: 10px;
        right: 10px;
        bottom: calc(10px + env(safe-area-inset-bottom));
        transform: none;
        max-width: none;
        flex-wrap: wrap;
        justify-content: center;
        border-radius: 22px;
        padding: 10px;
      }}

      .app-fixed-nav a,
      .app-fixed-nav button {{
        flex: 1 1 30%;
        min-width: 92px;
        padding: 10px 8px;
        font-size: 13px;
        text-align: center;
      }}
    }}
    /* End Voila fixed navigation */
'''

html_block = '''
    <nav id="appFixedNav" class="app-fixed-nav" aria-label="Voila quick navigation">
      <a class="primary" href="/">Back</a>
      <a id="fixedStudyLink" href="/" hidden>Study</a>
      <a id="fixedProgressLink" href="/" hidden>Progress</a>
      <button type="button" onclick="window.scrollTo({{ top: 0, behavior: 'smooth' }})">↑ Top</button>
      <button type="button" onclick="window.scrollTo({{ top: document.documentElement.scrollHeight, behavior: 'smooth' }})">↓ Bottom</button>
      <button id="fixedResetButton" class="danger" type="button" hidden>Reset</button>
    </nav>

    <script>
      (function () {{
        const params = new URLSearchParams(window.location.search);
        const pdf = params.get("pdf");
        const path = window.location.pathname;

        const studyLink = document.getElementById("fixedStudyLink");
        const progressLink = document.getElementById("fixedProgressLink");
        const resetButton = document.getElementById("fixedResetButton");

        if (pdf) {{
          const encodedPdf = encodeURIComponent(pdf);

          if (studyLink && path !== "/study") {{
            studyLink.href = "/study?pdf=" + encodedPdf;
            studyLink.hidden = false;
          }}

          if (progressLink && path !== "/progress") {{
            progressLink.href = "/progress?pdf=" + encodedPdf;
            progressLink.hidden = false;
          }}

          if (resetButton && (path === "/study" || path === "/progress")) {{
            resetButton.hidden = false;

            resetButton.addEventListener("click", function () {{
              const ok = window.confirm("Reset study progress for this PDF?");

              if (!ok) {{
                return;
              }}

              const form = document.createElement("form");
              form.method = "POST";
              form.action = "/study-reset";

              const input = document.createElement("input");
              input.type = "hidden";
              input.name = "pdf_name";
              input.value = pdf;

              form.appendChild(input);
              document.body.appendChild(form);
              form.submit();
            }});
          }}
        }}
      }})();
    </script>
'''

if "</style>" not in text:
    raise SystemExit("Could not find </style>.")

text = text.replace("</style>", css + "\n  </style>", 1)

if "</body>" not in text:
    raise SystemExit("Could not find </body>.")

text = text.replace("</body>", html_block + "\n</body>", 1)

path.write_text(text, encoding="utf-8")

print("OK: global fixed navigation bar installed.")
