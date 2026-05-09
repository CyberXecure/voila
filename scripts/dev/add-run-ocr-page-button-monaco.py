from pathlib import Path

path = Path("services/api/static/ocr_review_monaco.js")
text = path.read_text(encoding="utf-8")

if 'runOcrPageButton' not in text:
    text = text.replace(
'''    const checkButton = document.createElement("button");
    checkButton.type = "button";
    checkButton.id = "checkOcrButton";
    checkButton.textContent = "Verifică text";
    checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor.";
''',
'''    const runOcrPageButton = document.createElement("button");
    runOcrPageButton.type = "button";
    runOcrPageButton.id = "runOcrPageButton";
    runOcrPageButton.className = "voila-primary";
    runOcrPageButton.textContent = "Rulează OCR pagină";
    runOcrPageButton.title = "Generează OCR pentru pagina curentă, dacă textul este gol sau incomplet.";

    const checkButton = document.createElement("button");
    checkButton.type = "button";
    checkButton.id = "checkOcrButton";
    checkButton.textContent = "Verifică text";
    checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor.";
'''
    )

    text = text.replace(
'''    toolbar.appendChild(langSelect);
    toolbar.appendChild(checkButton);
    toolbar.appendChild(saveButton);
''',
'''    toolbar.appendChild(langSelect);
    toolbar.appendChild(runOcrPageButton);
    toolbar.appendChild(checkButton);
    toolbar.appendChild(saveButton);
'''
    )

    text = text.replace(
'''      checkButton.addEventListener("click", async function () {
        syncToTextarea();
''',
'''      runOcrPageButton.addEventListener("click", async function () {
        syncToTextarea();

        const url = new URL(window.location.href);
        const pdfName = url.searchParams.get("pdf") || getPdfName();
        const pageNumber = Number(url.searchParams.get("page") || "1");

        if (!pdfName || !pageNumber) {
          setStatus("<strong>OCR:</strong> nu pot determina PDF-ul sau pagina.");
          return;
        }

        runOcrPageButton.disabled = true;
        const oldLabel = runOcrPageButton.textContent;
        runOcrPageButton.textContent = "OCR...";

        setStatus("<strong>OCR:</strong> generez text pentru pagina curentă...");

        try {
          const response = await fetch("/run-ocr-page", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              pdf: pdfName,
              page: pageNumber,
              psm: 6,
              zoom: 3.0
            })
          });

          const data = await response.json();

          if (!data.ok) {
            setStatus("<strong>OCR:</strong> " + (data.message || "eroare") + "<br><pre>" + String(data.stderr || data.stdout || "").slice(-900) + "</pre>");
            return;
          }

          setStatus("<strong>OCR:</strong> gata. Reîncarc pagina...");
          window.location.href = window.location.href.replace(/([?&])v=[^&]*/, "$1v=" + Date.now());

          if (!window.location.href.includes("v=")) {
            window.location.href += (window.location.href.includes("?") ? "&" : "?") + "v=" + Date.now();
          }
        } catch (err) {
          setStatus("<strong>OCR:</strong> eroare: " + (err.message || String(err)));
        } finally {
          runOcrPageButton.disabled = false;
          runOcrPageButton.textContent = oldLabel;
        }
      });

      checkButton.addEventListener("click", async function () {
        syncToTextarea();
'''
    )

path.write_text(text, encoding="utf-8")
print("OK: Run OCR page button added to Monaco toolbar.")
