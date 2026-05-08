from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

start = text.find('@app.get("/review-ocr-text")')
end = text.find('@app.post("/review-ocr-text/save")', start)

if start == -1 or end == -1:
    raise SystemExit("Could not find Review OCR Text route.")

segment = text[start:end]

# Add VS-style CSS override before </style>.
vs_css = r'''
    /* VS Code style OCR autocomplete */
    .ocr-suggestions {
      position: fixed !important;
      z-index: 3000 !important;
      display: block !important;
      min-width: 280px;
      max-width: min(520px, calc(100vw - 24px));
      max-height: 280px;
      overflow-y: auto;
      padding: 6px;
      background: #1b2529;
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: 0 18px 48px rgba(0,0,0,0.45);
    }

    .ocr-suggestions[hidden] {
      display: none !important;
    }

    .ocr-suggestion {
      display: block !important;
      width: 100%;
      border: 0;
      border-radius: 8px;
      padding: 9px 12px;
      background: transparent;
      color: var(--text);
      text-align: left;
      font-weight: 800;
      font-size: 15px;
      cursor: pointer;
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
    }

    .ocr-suggestion:hover,
    .ocr-suggestion.active,
    .ocr-suggestion.primary {
      background: var(--accent);
      color: white;
    }

    .ocr-suggestion small {
      display: block;
      color: rgba(255,255,255,0.70);
      font-weight: 700;
      margin-top: 2px;
    }
'''

if "VS Code style OCR autocomplete" not in segment:
    segment = segment.replace("</style>", vs_css + "\n  </style>")

# Update tip text.
segment = segment.replace(
    "Tip: scrie minimum 2 litere. Click pe sugestie sau apasă Tab pentru prima sugestie.",
    "Tip: sugestiile apar lângă cursor. ↑/↓ navighează · Enter/Tab acceptă · Esc închide · Ctrl+Space afișează sugestii."
)

# Determine if route HTML is inside Python f-string with doubled braces.
uses_double_braces = "window.addEventListener(\"load\", () => {{" in segment or "function zoomScan(delta) {{" in segment
OB = "{{" if uses_double_braces else "{"
CB = "}}" if uses_double_braces else "}"

new_js = f'''
    // OCR autocomplete start
    function getCurrentOcrWord(textarea) {OB}
      const cursor = textarea.selectionStart || 0;
      const before = textarea.value.slice(0, cursor);
      const match = before.match(/[A-Za-zĂÂÎȘȚăâîșț0-9-]+$/);

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

    function getTextareaCaretViewportPosition(textarea) {OB}
      const position = textarea.selectionStart || 0;
      const style = window.getComputedStyle(textarea);
      const rect = textarea.getBoundingClientRect();

      const mirror = document.createElement("div");
      mirror.style.position = "absolute";
      mirror.style.visibility = "hidden";
      mirror.style.whiteSpace = "pre-wrap";
      mirror.style.overflowWrap = "break-word";
      mirror.style.wordWrap = "break-word";
      mirror.style.top = "0";
      mirror.style.left = "-9999px";
      mirror.style.width = textarea.clientWidth + "px";
      mirror.style.fontFamily = style.fontFamily;
      mirror.style.fontSize = style.fontSize;
      mirror.style.fontWeight = style.fontWeight;
      mirror.style.letterSpacing = style.letterSpacing;
      mirror.style.lineHeight = style.lineHeight;
      mirror.style.paddingTop = style.paddingTop;
      mirror.style.paddingRight = style.paddingRight;
      mirror.style.paddingBottom = style.paddingBottom;
      mirror.style.paddingLeft = style.paddingLeft;
      mirror.style.borderTopWidth = style.borderTopWidth;
      mirror.style.borderRightWidth = style.borderRightWidth;
      mirror.style.borderBottomWidth = style.borderBottomWidth;
      mirror.style.borderLeftWidth = style.borderLeftWidth;

      const before = textarea.value.slice(0, position);
      const after = textarea.value.slice(position);

      mirror.textContent = before;

      const marker = document.createElement("span");
      marker.textContent = after.length ? after[0] : ".";
      mirror.appendChild(marker);

      document.body.appendChild(mirror);

      const markerRect = marker.getBoundingClientRect();
      const mirrorRect = mirror.getBoundingClientRect();

      const lineHeight = parseFloat(style.lineHeight) || 24;

      const left = rect.left + (markerRect.left - mirrorRect.left) - textarea.scrollLeft;
      const top = rect.top + (markerRect.top - mirrorRect.top) - textarea.scrollTop + lineHeight + 4;

      document.body.removeChild(mirror);

      return {OB}
        left: left,
        top: top
      {CB};
    {CB}

    let ocrSuggestionTimer = null;
    let ocrLastSuggestions = [];
    let ocrActiveSuggestionIndex = 0;

    function getOcrSuggestionBox() {OB}
      return document.getElementById("ocrSuggestions");
    {CB}

    function ocrSuggestionBoxVisible() {OB}
      const box = getOcrSuggestionBox();
      return !!box && !box.hidden && ocrLastSuggestions.length > 0;
    {CB}

    function hideOcrSuggestions() {OB}
      const box = getOcrSuggestionBox();

      if (!box) {OB}
        return;
      {CB}

      box.hidden = true;
      box.innerHTML = "";
      ocrLastSuggestions = [];
      ocrActiveSuggestionIndex = 0;
    {CB}

    function positionOcrSuggestions() {OB}
      const textarea = document.getElementById("ocrTextArea");
      const box = getOcrSuggestionBox();

      if (!textarea || !box || box.hidden) {OB}
        return;
      {CB}

      const pos = getTextareaCaretViewportPosition(textarea);

      const boxWidth = Math.min(520, Math.max(280, box.offsetWidth || 320));
      const boxHeight = Math.min(280, box.offsetHeight || 220);

      let left = pos.left;
      let top = pos.top;

      if (left + boxWidth > window.innerWidth - 12) {OB}
        left = window.innerWidth - boxWidth - 12;
      {CB}

      if (left < 12) {OB}
        left = 12;
      {CB}

      if (top + boxHeight > window.innerHeight - 12) {OB}
        top = pos.top - boxHeight - 30;
      {CB}

      if (top < 12) {OB}
        top = 12;
      {CB}

      box.style.left = left + "px";
      box.style.top = top + "px";
    {CB}

    function renderOcrSuggestions(suggestions) {OB}
      const box = getOcrSuggestionBox();

      if (!box) {OB}
        return;
      {CB}

      ocrLastSuggestions = suggestions || [];
      ocrActiveSuggestionIndex = 0;

      if (!ocrLastSuggestions.length) {OB}
        hideOcrSuggestions();
        return;
      {CB}

      box.innerHTML = "";

      ocrLastSuggestions.forEach(function(word, index) {OB}
        const button = document.createElement("button");
        button.type = "button";
        button.className = index === ocrActiveSuggestionIndex ? "ocr-suggestion active" : "ocr-suggestion";
        button.textContent = word;
        button.dataset.index = String(index);
        button.dataset.word = word;

        button.addEventListener("mousedown", function(event) {OB}
          event.preventDefault();
        {CB});

        button.addEventListener("mouseenter", function() {OB}
          setActiveOcrSuggestion(index);
        {CB});

        button.addEventListener("click", function() {OB}
          insertOcrSuggestion(word);
        {CB});

        box.appendChild(button);
      {CB});

      box.hidden = false;
      positionOcrSuggestions();
    {CB}

    function setActiveOcrSuggestion(index) {OB}
      if (!ocrLastSuggestions.length) {OB}
        return;
      {CB}

      if (index < 0) {OB}
        index = ocrLastSuggestions.length - 1;
      {CB}

      if (index >= ocrLastSuggestions.length) {OB}
        index = 0;
      {CB}

      ocrActiveSuggestionIndex = index;

      const box = getOcrSuggestionBox();

      if (!box) {OB}
        return;
      {CB}

      box.querySelectorAll(".ocr-suggestion").forEach(function(button, i) {OB}
        button.classList.toggle("active", i === ocrActiveSuggestionIndex);

        if (i === ocrActiveSuggestionIndex) {OB}
          button.scrollIntoView({OB} block: "nearest" {CB});
        {CB}
      {CB});
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

      textarea.dispatchEvent(new Event("input", {OB} bubbles: true {CB}));
    {CB}

    function refreshOcrSuggestions(force) {OB}
      const textarea = document.getElementById("ocrTextArea");

      if (!textarea) {OB}
        return;
      {CB}

      const info = getCurrentOcrWord(textarea);

      if (!info || (!force && info.word.length < 2)) {OB}
        hideOcrSuggestions();
        return;
      {CB}

      const pdfName = document.body.dataset.pdfName || "";
      const query = info ? info.word : "";
      const url = "/review-ocr-text/suggestions?pdf=" + encodeURIComponent(pdfName) + "&q=" + encodeURIComponent(query) + "&limit=12";

      fetch(url)
        .then(function(response) {OB}
          return response.json();
        {CB})
        .then(function(data) {OB}
          renderOcrSuggestions(data.suggestions || []);
        {CB})
        .catch(function() {OB}
          hideOcrSuggestions();
        {CB});
    {CB}

    function scheduleOcrSuggestions() {OB}
      clearTimeout(ocrSuggestionTimer);
      ocrSuggestionTimer = setTimeout(function() {OB}
        refreshOcrSuggestions(false);
      {CB}, 90);
    {CB}

    function enableOcrAutocomplete() {OB}
      const textarea = document.getElementById("ocrTextArea");

      if (!textarea || textarea.dataset.autocompleteEnabled === "1") {OB}
        return;
      {CB}

      textarea.dataset.autocompleteEnabled = "1";

      textarea.addEventListener("input", scheduleOcrSuggestions);
      textarea.addEventListener("click", scheduleOcrSuggestions);
      textarea.addEventListener("scroll", positionOcrSuggestions);

      textarea.addEventListener("keydown", function(event) {OB}
        if (event.ctrlKey && event.code === "Space") {OB}
          event.preventDefault();
          refreshOcrSuggestions(true);
          return;
        {CB}

        if (!ocrSuggestionBoxVisible()) {OB}
          return;
        {CB}

        if (event.key === "ArrowDown") {OB}
          event.preventDefault();
          setActiveOcrSuggestion(ocrActiveSuggestionIndex + 1);
          return;
        {CB}

        if (event.key === "ArrowUp") {OB}
          event.preventDefault();
          setActiveOcrSuggestion(ocrActiveSuggestionIndex - 1);
          return;
        {CB}

        if (event.key === "Tab" || event.key === "Enter") {OB}
          event.preventDefault();
          insertOcrSuggestion(ocrLastSuggestions[ocrActiveSuggestionIndex]);
          return;
        {CB}

        if (event.key === "Escape") {OB}
          event.preventDefault();
          hideOcrSuggestions();
          return;
        {CB}
      {CB});

      window.addEventListener("resize", positionOcrSuggestions);
      window.addEventListener("scroll", positionOcrSuggestions, true);
    {CB}

    document.addEventListener("DOMContentLoaded", function() {OB}
      enableOcrAutocomplete();
    {CB});
    // OCR autocomplete end
'''

# Replace existing autocomplete JS block.
if "// OCR autocomplete start" in segment:
    segment = re.sub(
        r'\n\s*// OCR autocomplete start.*?// OCR autocomplete end',
        "\n" + new_js,
        segment,
        flags=re.DOTALL,
    )
else:
    script_end = segment.rfind("</script>")

    if script_end == -1:
        raise SystemExit("Could not find </script> in Review OCR Text route.")

    segment = segment[:script_end] + new_js + "\n" + segment[script_end:]

text = text[:start] + segment + text[end:]

path.write_text(text, encoding="utf-8")
print("OK: OCR suggestions changed to VS Code style popup.")
