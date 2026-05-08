from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# 1. Remove broken JS block if it was inserted directly into Python code.
text = re.sub(
    r'\n\s*function getCurrentWordInfo\(textarea\).*?\n(?=\s*function enableScanPan\(\))',
    '\n',
    text,
    flags=re.DOTALL,
)

text = re.sub(
    r'\n\s*function getCurrentOcrWord\(textarea\).*?\n(?=\s*function enableScanPan\(\))',
    '\n',
    text,
    flags=re.DOTALL,
)

# 2. Add backend suggestions endpoint if missing.
if '@app.get("/review-ocr-text/suggestions")' not in text:
    endpoint = r'''

@app.get("/review-ocr-text/suggestions")
def review_ocr_text_suggestions(pdf: str = "", q: str = "", limit: int = 12):
    from collections import Counter
    from fastapi.responses import JSONResponse
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
        "documentație", "obiective", "investiții", "publice", "tehnicoeconomică",
        "proiectare", "execuție", "verificare",
    ]

    counter = Counter()

    for word in technical_words:
        if word.lower().startswith(query):
            counter[word] += 10000

    for page in pages:
        page_text = str(page.get("text") or "")

        for word in re.findall(r"[A-Za-zĂÂÎȘȚăâîșț0-9][A-Za-zĂÂÎȘȚăâîșț0-9\\-]{2,}", page_text):
            clean = word.strip(".,:;()[]{}!?").lower()

            if len(clean) >= 3 and clean.startswith(query):
                counter[clean] += 1

    suggestions = [word for word, _count in counter.most_common(max(1, min(limit, 30)))]

    return JSONResponse({"suggestions": suggestions})
'''
    text += "\n\n" + endpoint

# 3. Patch Review OCR Text page safely.
start = text.find('@app.get("/review-ocr-text")')
end = text.find('@app.post("/review-ocr-text/save")', start)

if start == -1 or end == -1:
    raise SystemExit("Could not find Review OCR Text route.")

segment = text[start:end]

# Remove older autocomplete block if partially inserted inside the HTML script.
segment = re.sub(
    r'\n\s*// OCR autocomplete start.*?// OCR autocomplete end\s*\n',
    '\n',
    segment,
    flags=re.DOTALL,
)

# Add body data attribute.
if '<body data-pdf-name=' not in segment:
    segment = segment.replace(
        '<body>',
        '<body data-pdf-name="{_html_escape(pdf_name)}">'
    )

# Add textarea id and suggestions box.
if 'id="ocrTextArea"' not in segment:
    segment = segment.replace(
        '<textarea name="text">',
        '<textarea id="ocrTextArea" name="text" autocomplete="off" spellcheck="false">'
    )

if 'id="ocrSuggestions"' not in segment:
    segment = segment.replace(
'''          <textarea id="ocrTextArea" name="text" autocomplete="off" spellcheck="false">{_html_escape(current_text)}</textarea>
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

# Detect whether this HTML is inside an f-string and therefore needs doubled braces.
uses_double_braces = "function zoomScan(delta) {{" in segment or "window.addEventListener(\"load\", () => {{" in segment
OB = "{{" if uses_double_braces else "{"
CB = "}}" if uses_double_braces else "}"

safe_js = f'''
    // OCR autocomplete start
    function getCurrentOcrWord(textarea) {OB}
      const cursor = textarea.selectionStart || 0;
      const before = textarea.value.slice(0, cursor);
      const match = before.match(/[A-Za-zĂÂÎȘȚăâîșț0-9\\-]+$/);

      if (!match) {OB}
        return null;
      {CB}

      const word = match[0];

      return {OB}
        word: word,
        start: cursor - word.length,
        end: cursor
      {CB};
    {CB}

    let ocrSuggestionTimer = null;
    let ocrLastSuggestions = [];

    function hideOcrSuggestions() {OB}
      const box = document.getElementById("ocrSuggestions");

      if (!box) {OB}
        return;
      {CB}

      box.hidden = true;
      box.innerHTML = "";
      ocrLastSuggestions = [];
    {CB}

    function insertOcrSuggestion(value) {OB}
      const textarea = document.getElementById("ocrTextArea");

      if (!textarea) {OB}
        return;
      {CB}

      const info = getCurrentOcrWord(textarea);

      if (!info) {OB}
        return;
      {CB}

      const before = textarea.value.slice(0, info.start);
      const after = textarea.value.slice(info.end);

      textarea.value = before + value + after;

      const nextCursor = before.length + value.length;
      textarea.focus();
      textarea.setSelectionRange(nextCursor, nextCursor);

      hideOcrSuggestions();
    {CB}

    function refreshOcrSuggestions() {OB}
      const textarea = document.getElementById("ocrTextArea");
      const box = document.getElementById("ocrSuggestions");

      if (!textarea || !box) {OB}
        return;
      {CB}

      const info = getCurrentOcrWord(textarea);

      if (!info || info.word.length < 2) {OB}
        hideOcrSuggestions();
        return;
      {CB}

      const pdfName = document.body.dataset.pdfName || "";
      const url = "/review-ocr-text/suggestions?pdf=" + encodeURIComponent(pdfName) + "&q=" + encodeURIComponent(info.word) + "&limit=12";

      fetch(url)
        .then(function(response) {OB}
          return response.json();
        {CB})
        .then(function(data) {OB}
          const suggestions = data.suggestions || [];
          ocrLastSuggestions = suggestions;

          if (!suggestions.length) {OB}
            hideOcrSuggestions();
            return;
          {CB}

          box.innerHTML = "";

          suggestions.forEach(function(word, index) {OB}
            const button = document.createElement("button");
            button.type = "button";
            button.className = index === 0 ? "ocr-suggestion primary" : "ocr-suggestion";
            button.textContent = word;
            button.dataset.word = word;

            button.addEventListener("click", function() {OB}
              insertOcrSuggestion(button.dataset.word || "");
            {CB});

            box.appendChild(button);
          {CB});

          box.hidden = false;
        {CB})
        .catch(function() {OB}
          hideOcrSuggestions();
        {CB});
    {CB}

    function enableOcrAutocomplete() {OB}
      const textarea = document.getElementById("ocrTextArea");

      if (!textarea || textarea.dataset.autocompleteEnabled === "1") {OB}
        return;
      {CB}

      textarea.dataset.autocompleteEnabled = "1";

      textarea.addEventListener("input", function() {OB}
        clearTimeout(ocrSuggestionTimer);
        ocrSuggestionTimer = setTimeout(refreshOcrSuggestions, 120);
      {CB});

      textarea.addEventListener("click", function() {OB}
        clearTimeout(ocrSuggestionTimer);
        ocrSuggestionTimer = setTimeout(refreshOcrSuggestions, 120);
      {CB});

      textarea.addEventListener("keydown", function(event) {OB}
        if (event.key === "Tab" && ocrLastSuggestions.length > 0) {OB}
          event.preventDefault();
          insertOcrSuggestion(ocrLastSuggestions[0]);
        {CB}

        if (event.key === "Escape") {OB}
          hideOcrSuggestions();
        {CB}
      {CB});
    {CB}

    document.addEventListener("DOMContentLoaded", function() {OB}
      enableOcrAutocomplete();
    {CB});
    // OCR autocomplete end
'''

if "// OCR autocomplete start" not in segment:
    script_end = segment.rfind("</script>")

    if script_end == -1:
        body_end = segment.rfind("</body>")
        if body_end == -1:
            raise SystemExit("Could not find </script> or </body> in Review OCR Text route.")

        segment = segment[:body_end] + "\n  <script>\n" + safe_js + "\n  </script>\n" + segment[body_end:]
    else:
        segment = segment[:script_end] + safe_js + "\n" + segment[script_end:]

text = text[:start] + segment + text[end:]

path.write_text(text, encoding="utf-8")
print("OK: fixed OCR autocomplete insertion safely.")
