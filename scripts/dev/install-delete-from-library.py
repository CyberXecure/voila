from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# Imports
if "import shutil" not in text:
    text = text.replace("import html\n", "import html\nimport shutil\n")

if "import datetime as dt" not in text:
    text = text.replace("import shutil\n", "import shutil\nimport datetime as dt\n")

# CSS
css = '''
    .btn.danger,
    button.danger {{
      background: rgba(151, 75, 58, 0.92);
      color: #fffaf0;
      border-color: rgba(151, 75, 58, 0.92);
    }}

    .delete-library-form {{
      display: inline-flex;
      margin: 0;
    }}
'''

if ".delete-library-form" not in text:
    text = text.replace("</style>", css + "\n  </style>", 1)

# Route: Delete from library = move PDF + generated output to trash
route = r'''

def move_to_trash(source: Path, trash_subdir: str) -> Path | None:
    if not source.exists():
        return None

    trash_dir = PROJECT_ROOT / "data" / "trash" / trash_subdir
    trash_dir.mkdir(parents=True, exist_ok=True)

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

    if source.is_dir():
        target = trash_dir / f"{source.name}_{stamp}"
    else:
        target = trash_dir / f"{source.stem}_{stamp}{source.suffix}"

    shutil.move(str(source), str(target))

    return target


@app.post("/delete-from-library")
def delete_from_library(pdf_name: str = Form(...)) -> RedirectResponse:
    pdf_path = validate_pdf_name(pdf_name)
    output_dir = OUTPUT_DIR / pdf_path.stem

    move_to_trash(output_dir, "courses")
    move_to_trash(pdf_path, "pdfs")

    return RedirectResponse(
        url="/",
        status_code=303,
    )

'''

if '@app.post("/delete-from-library")' not in text:
    if '\n@app.get("/progress"' in text:
        text = text.replace('\n@app.get("/progress"', route + '\n@app.get("/progress"', 1)
    elif '\n@app.get("/study"' in text:
        text = text.replace('\n@app.get("/study"', route + '\n@app.get("/study"', 1)
    else:
        text += "\n" + route

# Home-page script: inject Delete from library button into every PDF card
script = '''
    <script id="delete-from-library-injector">
      (function () {{
        function injectDeleteButtons() {{
          const path = window.location.pathname;

          if (path !== "/" && path !== "") {{
            return;
          }}

          const cards = document.querySelectorAll(".card");

          cards.forEach(function (card) {{
            if (card.querySelector(".delete-library-form")) {{
              return;
            }}

            const title = card.querySelector("h2, h3");

            if (!title) {{
              return;
            }}

            const pdfName = (title.innerText || "").replace(/\\s+/g, " ").trim();

            if (!pdfName.toLowerCase().endsWith(".pdf")) {{
              return;
            }}

            const form = document.createElement("form");
            form.className = "delete-library-form";
            form.method = "POST";
            form.action = "/delete-from-library";
            form.onsubmit = function () {{
              return window.confirm("Remove this PDF and its generated course from the library? Files will be moved to data/trash, not permanently deleted.");
            }};

            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "pdf_name";
            input.value = pdfName;

            const button = document.createElement("button");
            button.className = "btn danger";
            button.type = "submit";
            button.textContent = "Delete from library";

            form.appendChild(input);
            form.appendChild(button);

            const actions = card.querySelector(".actions");

            if (actions) {{
              actions.appendChild(form);
            }} else {{
              card.appendChild(form);
            }}
          }});
        }}

        injectDeleteButtons();

        if (document.readyState === "loading") {{
          document.addEventListener("DOMContentLoaded", injectDeleteButtons);
        }} else {{
          injectDeleteButtons();
        }}
      }})();
    </script>
'''

if "delete-from-library-injector" not in text:
    text = text.replace("</body>", script + "\n</body>", 1)

path.write_text(text, encoding="utf-8")

print("OK: Delete from library route and UI injector installed.")
