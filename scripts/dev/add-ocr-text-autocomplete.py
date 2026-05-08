from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# 1. Add backend suggestions endpoint if missing.
if '@app.get("/review-ocr-text/suggestions")' not in text:
    endpoint = r'''

@app.get("/review-ocr-text/suggestions")
def review_ocr_text_suggestions(pdf: str = "", q: str = "", limit: int = 12):
    from fastapi.responses import JSONResponse
    from collections import Counter
    import re

    pdf_name = _safe_pdf_name(pdf)

    if not pdf_name:
        return JSONResponse({"suggestions": []})

    output_dir = _output_dir_for_pdf_name(pdf_name)
    pages = _load_ocr_review_pages(output_dir)

    query = str(q or "").strip().lower()

    if len(query) < 2:
        return JSONResponse({"suggestions": []})

    technical_words = [
        "instalații", "electrice", "automatizare", "iluminat", "tensiune",
        "curent", "putere", "energie", "circuit", "circuite", "protecție",
        "alimentare", "distribuție", "comandă", "măsurare", "reglare",
        "control", "siguranță", "conductoare", "conductor", "echipamente",
        "tablouri", "aparate", "relee", "contactoare", "senzori",
        "rezistență", "impedanță", "frecvență", "factor", "defazaj",
        "luminos", "luminanță", "iluminare", "randament", "transformator",
        "motor", "monofazat", "trifazat", "împământare", "legare",
        "scurtcircuit", "suprasarcină", "declanșare", "automat",
        "automată", "sisteme", "scheme", "tehnologice", "principiu",
        "regulatoare", "traductoare", "ventilare", "climatizare",
        "temperatură", "presiune", "umiditate", "debit", "mărimi",
        "documentație", "obiective", "investiții", "publice", "tehnico",
        "economică", "proiectare", "execuție", "verificare",
    ]

    counter = Counter()

    for word in technical_words:
        normalized = word.lower()

        if normalized.startswith(query):
            counter[word] += 10000

    for page in pages:
        page_text = str(page.get("text") or "")

        for word in re.findall(r"[A-Za-zĂÂÎȘȚăâîșț0-9][A-Za-zĂÂÎȘȚăâîșț0-9\-]{2,}", page_text):
            clean = word.strip(".,:;()[]{}!?").lower()

            if len(clean) < 3:
                continue

            if clean.startswith(query):
                counter[clean] += 1

    suggestions = [
        word
        for word, _count in counter.most_common(max(1, min(limit, 30)))
    ]

    return JSONResponse({"suggestions": suggestions})
'''
    text += "\n\n" + endpoint


# 2. Patch Review OCR Text page.
start = text.find('@app.get("/review-ocr-text")')
end = text.find('@app.post("/review-ocr-text/save")', start)

if start == -1 or end == -1:
    raise SystemExit("Could not find Review OCR Text route.")

segment = text[start:end]

# Add data-pdf-name to body.
if '<body data-pdf-name=' not in segment:
    segment = segment.replace(
        '<body>',
        '<body data-pdf-name="{_html_escape(pdf_name)}">'
    )

# Add suggestions box after textarea.
if 'id="ocrSuggestions"' not in segment:
    segment = segment.replace(
'''          <textarea name="text">{_html_escape(current_text)}</textarea>
''',
'''          <textarea id="ocrTextArea" name="text" autocomplete="off" spellcheck="false">{_html_escape(current_text)}</textarea>
          <div id="ocrSuggestions" class="ocr-suggestions" hidden></div>
          <p class="meta small-tip">Tip: scrie minimum 2 litere. Click pe sugestie sau apasă Tab pentru prima sugestie.</p>
'''
    )

# Add CSS.
if ".ocr-suggestions {{" not in segment:
    segment = segment.replace(
'''    .actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin: 14px 0;
    }}
''',
'''    .ocr-suggestions {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
      padding: 10px;
      background: #142022;
      border: 1px solid var(--line);
      border-radius: 16px;
    }}

    .ocr-suggestions[hidden] {{
      display: none;
    }}

    .ocr-suggestion {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 12px;
      background: var(--panel2);
      color: var(--text);
      font-weight: 850;
      cursor: pointer;
    }}

    .ocr-suggestion.primary {{
      background: var(--accent);
      color: white;
      border-color: transparent;
    }}

    .small-tip {{
      font-size: 14px;
      margin-top: 8px;
    }}

    .actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin: 14px 0;
    }}
'''
    )

# Add JS before </script> of Review OCR Text route.
autocomplete_js = r'''
    function getCurrentWordInfo(textarea) {
      const cursor = textarea.selectionStart || 0;
      const before = textarea.value.slice(0, cursor);
      const match = before.match(/[A-Za-zĂÂÎȘȚăâîșț0-9\-]+$/);

      if (!match) {
        return null;
      }

      const word = match[0];

      return {
        word,
        start: cursor - word.length,
        end: cursor
      };
    }

    let suggestionAbort = null;
    let suggestionTimer = null;
    let lastSuggestions = [];

    function hideOcrSuggestions() {
      const box = document.getElementById("ocrSuggestions");

      if (!box) {
        return;
      }

      box.hidden = true;
      box.innerHTML = "";
      lastSuggestions = [];
    }

    function insertOcrSuggestion(value) {
      const textarea = document.getElementById("ocrTextArea");
      const info = getCurrentWordInfo(textarea);

      if (!textarea || !info) {
        return;
      }

      const before = textarea.value.slice(0, info.start);
      const after = textarea.value.slice(info.end);
      const replacement = value;

      textarea.value = before + replacement + after;

      const nextCursor = before.length + replacement.length;
      textarea.focus();
      textarea.setSelectionRange(nextCursor, nextCursor);

      hideOcrSuggestions();
    }

    async function refreshOcrSuggestions() {
      const textarea = document.getElementById("ocrTextArea");
      const box = document.getElementById("ocrSuggestions");

      if (!textarea || !box) {
        return;
      }

      const info = getCurrentWordInfo(textarea);

      if (!info || info.word.length < 2) {
        hideOcrSuggestions();
        return;
      }

      const pdfName = document.body.dataset.pdfName || "";

      if (suggestionAbort) {
        suggestionAbort.abort();
      }

      suggestionAbort = new AbortController();

      try {
        const url = `/review-ocr-text/suggestions?pdf=${{encodeURIComponent(pdfName)}}&q=${{encodeURIComponent(info.word)}}&limit=12`;
        const response = await fetch(url, { signal: suggestionAbort.signal });
        const data = await response.json();
        const suggestions = data.suggestions || [];

        lastSuggestions = suggestions;

        if (!suggestions.length) {
          hideOcrSuggestions();
          return;
        }

        box.innerHTML = suggestions.map((word, index) => {
          const cls = index === 0 ? "ocr-suggestion primary" : "ocr-suggestion";
          return `<button type="button" class="${{cls}}" data-word="${{word.replaceAll('"', "&quot;")}}">${{word}}</button>`;
        }).join("");

        box.hidden = false;

        box.querySelectorAll("[data-word]").forEach((button) => {
          button.addEventListener("click", () => {
            insertOcrSuggestion(button.dataset.word || "");
          });
        });
      } catch (_error) {
        // Ignore aborted or temporary suggestion errors.
      }
    }

    function enableOcrAutocomplete() {
      const textarea = document.getElementById("ocrTextArea");

      if (!textarea || textarea.dataset.autocompleteEnabled === "1") {
        return;
      }

      textarea.dataset.autocompleteEnabled = "1";

      textarea.addEventListener("input", () => {
        clearTimeout(suggestionTimer);
        suggestionTimer = setTimeout(refreshOcrSuggestions, 120);
      });

      textarea.addEventListener("click", () => {
        clearTimeout(suggestionTimer);
        suggestionTimer = setTimeout(refreshOcrSuggestions, 120);
      });

      textarea.addEventListener("keyup", (event) => {
        if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) {
          clearTimeout(suggestionTimer);
          suggestionTimer = setTimeout(refreshOcrSuggestions, 120);
        }
      });

      textarea.addEventListener("keydown", (event) => {
        if (event.key === "Tab" && lastSuggestions.length > 0) {
          event.preventDefault();
          insertOcrSuggestion(lastSuggestions[0]);
        }

        if (event.key === "Escape") {
          hideOcrSuggestions();
        }
      });
    }

'''

if "function enableOcrAutocomplete()" not in segment:
    marker = '    function enableScanPan() {{'
    if marker not in segment:
        raise SystemExit("Could not find JS marker.")
    segment = segment.replace(marker, autocomplete_js + "\n" + marker)

# Call autocomplete on load.
segment = segment.replace(
'''    window.addEventListener("load", () => {{
      document.querySelectorAll(".scan-floating-zoom").forEach((el) => el.remove());
      applyScanZoom();
      enableScanPan();
    }});
''',
'''    window.addEventListener("load", () => {{
      document.querySelectorAll(".scan-floating-zoom").forEach((el) => el.remove());
      applyScanZoom();
      enableScanPan();
      enableOcrAutocomplete();
    }});
'''
)

text = text[:start] + segment + text[end:]

path.write_text(text, encoding="utf-8")
print("OK: OCR text autocomplete suggestions added.")
