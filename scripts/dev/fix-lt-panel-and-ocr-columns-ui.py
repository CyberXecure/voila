from pathlib import Path

js_path = Path("services/api/static/ocr_review_monaco.js")
js = js_path.read_text(encoding="utf-8")

# Monaco lightbulb off: folosim panoul nostru, nu popup-ul îngust.
js = js.replace(
'''        lightbulb: { enabled: true },''',
'''        lightbulb: { enabled: false },'''
)

js = js.replace(
'''        lightbulb: { enabled: true }''',
'''        lightbulb: { enabled: false }'''
)

# Add OCR layout selector after language selector creation.
if 'voilaOcrColumns' not in js:
    js = js.replace(
'''    langSelect.value = selectedDocumentLanguage;

    const runOcrPageButton = document.createElement("button");
''',
'''    langSelect.value = selectedDocumentLanguage;

    const ocrColumnsSelect = document.createElement("select");
    ocrColumnsSelect.id = "voilaOcrColumns";
    ocrColumnsSelect.title = "Mod OCR pentru pagina curentă";

    [
      ["0", "OCR normal"],
      ["2", "OCR 2 coloane"],
      ["3", "OCR 3 coloane"]
    ].forEach(function (item) {
      const option = document.createElement("option");
      option.value = item[0];
      option.textContent = item[1];
      ocrColumnsSelect.appendChild(option);
    });

    ocrColumnsSelect.value = "3";

    const runOcrPageButton = document.createElement("button");
'''
    )

    js = js.replace(
'''    toolbar.appendChild(langSelect);
    toolbar.appendChild(runOcrPageButton);
''',
'''    toolbar.appendChild(langSelect);
    toolbar.appendChild(ocrColumnsSelect);
    toolbar.appendChild(runOcrPageButton);
'''
    )

    js = js.replace(
'''              zoom: 3.0
''',
'''              zoom: 3.0,
              columns: Number(ocrColumnsSelect.value || "0")
'''
    )

# Add LanguageTool panel after status creation.
if 'voilaLtPanel' not in js:
    js = js.replace(
'''    const status = document.createElement("div");
    status.id = "voilaMonacoStatus";
    status.innerHTML = "<strong>Editor:</strong> se încarcă Monaco...";

    textarea.classList.add("voila-monaco-hidden");
''',
'''    const status = document.createElement("div");
    status.id = "voilaMonacoStatus";
    status.innerHTML = "<strong>Editor:</strong> se încarcă Monaco...";

    const ltPanel = document.createElement("div");
    ltPanel.id = "voilaLtPanel";
    ltPanel.hidden = true;

    textarea.classList.add("voila-monaco-hidden");
'''
    )

    js = js.replace(
'''    textarea.insertAdjacentElement("afterend", status);
    textarea.insertAdjacentElement("afterend", host);
    textarea.insertAdjacentElement("afterend", toolbar);
''',
'''    textarea.insertAdjacentElement("afterend", status);
    textarea.insertAdjacentElement("afterend", host);
    textarea.insertAdjacentElement("afterend", ltPanel);
    textarea.insertAdjacentElement("afterend", toolbar);
'''
    )

# Add custom LT renderer before prev/next handlers.
if 'function renderLtIssuePanel' not in js:
    marker = '''      prevButton.addEventListener("click", function () {
'''
    insert = r'''
      function escapeHtml(value) {
        return String(value || "")
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;");
      }

      function renderLtIssuePanel() {
        const matches = window.voilaLtMatches || [];

        if (!matches.length) {
          ltPanel.hidden = true;
          return;
        }

        if (window.voilaLtIndex < 0) window.voilaLtIndex = 0;
        if (window.voilaLtIndex >= matches.length) window.voilaLtIndex = matches.length - 1;

        const match = matches[window.voilaLtIndex];
        const replacements = match.replacements || [];
        const range = rangeFromMatch(match);

        const currentText = model.getValueInRange(range);

        const buttons = replacements.slice(0, 8).map(function (replacement, index) {
          return '<button type="button" class="lt-replace" data-index="' + index + '">' +
            escapeHtml(replacement) +
            '</button>';
        }).join("");

        ltPanel.hidden = false;
        ltPanel.innerHTML =
          '<div class="lt-head">' +
            '<strong>LanguageTool</strong>' +
            '<span>' + (window.voilaLtIndex + 1) + ' / ' + matches.length + '</span>' +
          '</div>' +
          '<div class="lt-message">' + escapeHtml(match.message || "Sugestie") + '</div>' +
          '<div class="lt-current">Text: <code>' + escapeHtml(currentText) + '</code></div>' +
          '<div class="lt-actions">' + buttons + '</div>';

        Array.from(ltPanel.querySelectorAll(".lt-replace")).forEach(function (button) {
          button.addEventListener("click", function () {
            const replacement = replacements[Number(button.dataset.index || "0")] || "";

            editor.executeEdits("LanguageTool", [{
              range: range,
              text: replacement,
              forceMoveMarkers: true
            }]);

            syncToTextarea();

            setStatus("<strong>LanguageTool:</strong> sugestie aplicată. Rulează din nou „Verifică text” pentru lista actualizată.");

            matches.splice(window.voilaLtIndex, 1);
            window.voilaSetLanguageToolMarkers(matches);
          });
        });
      }

'''
    if marker not in js:
        raise SystemExit("Nu găsesc markerul prevButton pentru inserare panel LT.")

    js = js.replace(marker, insert + marker)

# Call panel renderer when markers are set.
js = js.replace(
'''        if (!markers.length) {
          setStatus("<strong>LanguageTool:</strong> 0 probleme evidente.");
        } else {
          setStatus(
            "<strong>LanguageTool:</strong> " + markers.length +
            " sugestii. Click pe subliniere sau Ctrl+. pentru quick fix."
          );
        }
''',
'''        if (!markers.length) {
          ltPanel.hidden = true;
          setStatus("<strong>LanguageTool:</strong> 0 probleme evidente.");
        } else {
          setStatus(
            "<strong>LanguageTool:</strong> " + markers.length +
            " sugestii. Folosește panoul de sugestii de sub toolbar."
          );
          renderLtIssuePanel();
        }
'''
)

# Call panel renderer after navigation.
js = js.replace(
'''        setStatus(
          "<strong>LanguageTool:</strong> sugestia " +
          (window.voilaLtIndex + 1) + " / " + matches.length +
          ". Ctrl+. pentru quick fix."
        );
''',
'''        setStatus(
          "<strong>LanguageTool:</strong> sugestia " +
          (window.voilaLtIndex + 1) + " / " + matches.length
        );
        renderLtIssuePanel();
'''
)

js_path.write_text(js, encoding="utf-8")


css_path = Path("services/api/static/ocr_review_monaco.css")
css = css_path.read_text(encoding="utf-8")

marker = "/* OCR_LT_PANEL_AND_COLUMNS_V1 */"

if marker not in css:
    css += r'''

/* OCR_LT_PANEL_AND_COLUMNS_V1 */

#voilaOcrColumns {
  padding: 7px 10px;
  font-size: 13px;
  line-height: 1.1;
  border-radius: 999px;
  border: 1px solid var(--line, #3b4b50);
  background: #111b1e;
  color: var(--text, #f4efe7);
}

#voilaLtPanel {
  margin: 8px 0 10px;
  padding: 10px 12px;
  border: 1px solid rgba(224, 173, 104, 0.45);
  border-radius: 14px;
  background: rgba(12, 20, 22, 0.96);
  color: var(--text, #f4efe7);
  position: relative;
  z-index: 30;
}

#voilaLtPanel .lt-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--accent, #e0ad68);
  margin-bottom: 6px;
}

#voilaLtPanel .lt-message {
  font-size: 14px;
  margin-bottom: 6px;
}

#voilaLtPanel .lt-current {
  font-size: 13px;
  color: var(--muted, #c7ad94);
  margin-bottom: 8px;
}

#voilaLtPanel code {
  color: #fff4da;
  background: rgba(255,255,255,0.06);
  padding: 2px 6px;
  border-radius: 6px;
}

#voilaLtPanel .lt-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

#voilaLtPanel .lt-replace {
  padding: 6px 10px !important;
  font-size: 14px !important;
  border-radius: 999px !important;
  background: var(--accent, #e0ad68) !important;
  color: #101819 !important;
  border-color: transparent !important;
  text-shadow: none !important;
  white-space: normal !important;
  max-width: 100% !important;
}
'''

css_path.write_text(css, encoding="utf-8")

print("OK: custom LanguageTool panel + OCR columns selector added.")
