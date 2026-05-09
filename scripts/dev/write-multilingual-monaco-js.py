from pathlib import Path

path = Path("services/api/static/ocr_review_monaco.js")

path.write_text(r'''
(function () {
  window.VOILA_MONACO_JS_LOADED = true;
  console.log("Voila Monaco OCR JS loaded - multilingual");

  const LANGUAGE_LABELS = {
    auto: "Auto",
    ro: "Română",
    en: "English",
    fr: "Français",
    de: "Deutsch",
    ru: "Русский"
  };

  const LT_LANG = {
    ro: "ro-RO",
    en: "en-US",
    fr: "fr",
    de: "de-DE",
    ru: "ru-RU"
  };

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (window.require) return resolve();

      const script = document.createElement("script");
      script.src = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  function findOcrTextarea() {
    return (
      document.getElementById("ocrText") ||
      document.querySelector('textarea[name="text"]') ||
      document.querySelector('textarea[name="corrected_text"]') ||
      document.querySelector('textarea[name*="ocr" i]') ||
      document.querySelector("form textarea") ||
      document.querySelector("textarea")
    );
  }

  function labelOf(el) {
    return String((el && (el.textContent || el.value)) || "").trim().toLowerCase();
  }

  function getPdfName() {
    const url = new URL(window.location.href);
    return url.searchParams.get("pdf") || document.body.dataset.pdfName || "";
  }

  function detectLanguageFromText(value) {
    const text = String(value || "").toLowerCase();

    if (/[а-яё]/i.test(text)) return "ru";

    const scores = { ro: 0, en: 0, fr: 0, de: 0 };

    if (/[ăâîșşțţ]/i.test(text)) scores.ro += 5;
    if (/[éèêëàâîïôùûçœ]/i.test(text)) scores.fr += 4;
    if (/[äöüß]/i.test(text)) scores.de += 4;

    const markers = {
      ro: ["pentru", "este", "sunt", "care", "prin", "din", "funcție", "capitolul", "figura"],
      en: ["the", "and", "with", "from", "figure", "chapter", "system", "pressure", "temperature"],
      fr: ["pour", "avec", "dans", "figure", "chapitre", "pression", "température", "système"],
      de: ["und", "mit", "der", "die", "das", "abbildung", "kapitel", "druck", "temperatur", "system"]
    };

    Object.keys(markers).forEach(function (lang) {
      markers[lang].forEach(function (word) {
        if (text.includes(word)) scores[lang] += 1;
      });
    });

    let best = "en";
    Object.keys(scores).forEach(function (lang) {
      if (scores[lang] > scores[best]) best = lang;
    });

    return best;
  }

  function normalizeLanguage(value) {
    value = String(value || "auto").toLowerCase();

    const aliases = {
      "ro-ro": "ro",
      "ron": "ro",
      "romana": "ro",
      "română": "ro",
      "en-us": "en",
      "en-gb": "en",
      "eng": "en",
      "fr-fr": "fr",
      "fra": "fr",
      "de-de": "de",
      "deu": "de",
      "ru-ru": "ru",
      "rus": "ru"
    };

    value = aliases[value] || value;

    if (!LANGUAGE_LABELS[value]) return "auto";

    return value;
  }

  function getEffectiveLanguage(selectedLanguage, text) {
    selectedLanguage = normalizeLanguage(selectedLanguage);

    if (selectedLanguage === "auto") {
      return detectLanguageFromText(text);
    }

    return selectedLanguage;
  }

  async function loadDocumentLanguage(pdfName) {
    try {
      const response = await fetch("/document-language?pdf=" + encodeURIComponent(pdfName));
      const data = await response.json();

      if (data && data.ok) {
        return normalizeLanguage(data.document_language || "auto");
      }
    } catch (_) {}

    return "auto";
  }

  async function saveDocumentLanguage(pdfName, language) {
    try {
      await fetch("/document-language", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pdf: pdfName,
          language: normalizeLanguage(language)
        })
      });
    } catch (_) {}
  }

  ready(async function () {
    const textarea = findOcrTextarea();

    if (!textarea) {
      console.warn("Voila Monaco: no textarea found.");
      return;
    }

    if (!textarea.id) {
      textarea.id = "ocrText";
    }

    const pdfName = getPdfName();
    let selectedDocumentLanguage = await loadDocumentLanguage(pdfName);

    const form = textarea.closest("form");

    const toolbar = document.createElement("div");
    toolbar.id = "voilaMonacoToolbar";

    const langSelect = document.createElement("select");
    langSelect.id = "voilaDocumentLanguage";
    langSelect.title = "Limba documentului PDF";

    Object.keys(LANGUAGE_LABELS).forEach(function (lang) {
      const option = document.createElement("option");
      option.value = lang;
      option.textContent = LANGUAGE_LABELS[lang];
      langSelect.appendChild(option);
    });

    langSelect.value = selectedDocumentLanguage;

    const checkButton = document.createElement("button");
    checkButton.type = "button";
    checkButton.id = "checkOcrButton";
    checkButton.textContent = "Verifică text";
    checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor.";

    const saveButton = document.createElement("button");
    saveButton.type = "button";
    saveButton.className = "voila-primary";
    saveButton.textContent = "Salvează";
    saveButton.title = "Salvează corecția curentă.";

    const prevButton = document.createElement("button");
    prevButton.type = "button";
    prevButton.textContent = "← problemă";

    const nextButton = document.createElement("button");
    nextButton.type = "button";
    nextButton.textContent = "problemă →";

    toolbar.appendChild(langSelect);
    toolbar.appendChild(checkButton);
    toolbar.appendChild(saveButton);
    toolbar.appendChild(prevButton);
    toolbar.appendChild(nextButton);

    const host = document.createElement("div");
    host.id = "voilaMonacoEditor";

    const status = document.createElement("div");
    status.id = "voilaMonacoStatus";
    status.innerHTML = "<strong>Editor:</strong> se încarcă Monaco...";

    textarea.classList.add("voila-monaco-hidden");
    textarea.insertAdjacentElement("afterend", status);
    textarea.insertAdjacentElement("afterend", host);
    textarea.insertAdjacentElement("afterend", toolbar);

    function setStatus(message) {
      status.innerHTML = message || "";
    }

    function fallback(message) {
      textarea.classList.remove("voila-monaco-hidden");
      host.style.display = "none";
      toolbar.style.display = "none";
      setStatus(message || "<strong>Editor:</strong> Monaco nu a putut fi încărcat.");
    }

    langSelect.addEventListener("change", async function () {
      selectedDocumentLanguage = normalizeLanguage(langSelect.value);
      await saveDocumentLanguage(pdfName, selectedDocumentLanguage);

      const effective = getEffectiveLanguage(selectedDocumentLanguage, textarea.value || "");
      setStatus(
        "<strong>Limba documentului:</strong> " +
        LANGUAGE_LABELS[selectedDocumentLanguage] +
        " · LanguageTool: " +
        (LT_LANG[effective] || "en-US")
      );
    });

    try {
      await loadScript("https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs/loader.js");
    } catch (err) {
      fallback("<strong>Editor:</strong> Monaco CDN nu s-a încărcat. Folosesc editorul simplu.");
      return;
    }

    if (!window.require) {
      fallback("<strong>Editor:</strong> Monaco loader indisponibil.");
      return;
    }

    window.require.config({
      paths: {
        vs: "https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs"
      }
    });

    window.require(["vs/editor/editor.main"], function () {
      monaco.languages.register({ id: "voila-ocr" });

      const model = monaco.editor.createModel(textarea.value || "", "voila-ocr");

      const editor = monaco.editor.create(host, {
        model: model,
        theme: "vs-dark",
        automaticLayout: true,
        wordWrap: "on",
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        fontSize: 15,
        lineHeight: 22,
        fontFamily: 'Consolas, "Cascadia Mono", "Courier New", monospace',
        quickSuggestions: false,
        suggestOnTriggerCharacters: false,
        tabSize: 2,
        padding: { top: 10, bottom: 10 },
        lightbulb: { enabled: true }
      });

      window.voilaMonaco = editor;
      window.voilaMonacoModel = model;
      window.voilaLtMatches = [];
      window.voilaLtIndex = 0;

      function syncToTextarea() {
        textarea.value = model.getValue();
      }

      model.onDidChangeContent(syncToTextarea);

      if (form) {
        form.addEventListener("submit", syncToTextarea);
      }

      function findReviewedSubmitButton() {
        if (!form) return null;

        const buttons = Array.from(form.querySelectorAll('button[type="submit"], input[type="submit"]'));

        return (
          buttons.find(function (btn) {
            const label = labelOf(btn);
            return (label.includes("reviewed") || label.includes("salvează")) &&
                   !label.includes("needs") &&
                   !label.includes("mai târziu");
          }) ||
          buttons[0] ||
          null
        );
      }

      saveButton.addEventListener("click", function () {
        syncToTextarea();

        const submit = findReviewedSubmitButton();

        if (form && submit && form.requestSubmit) {
          form.requestSubmit(submit);
        } else if (submit) {
          submit.click();
        } else if (form) {
          form.submit();
        }
      });

      function rangeFromMatch(match) {
        const offset = Number(match.offset || 0);
        const length = Math.max(1, Number(match.length || 1));
        const start = model.getPositionAt(offset);
        const end = model.getPositionAt(offset + length);

        return new monaco.Range(
          start.lineNumber,
          start.column,
          end.lineNumber,
          end.column
        );
      }

      function rangesIntersect(a, b) {
        return !(a.endLineNumber < b.startLineNumber ||
          a.startLineNumber > b.endLineNumber ||
          (a.endLineNumber === b.startLineNumber && a.endColumn < b.startColumn) ||
          (a.startLineNumber === b.endLineNumber && a.startColumn > b.endColumn));
      }

      monaco.languages.registerCodeActionProvider("voila-ocr", {
        provideCodeActions: function (_model, range) {
          const actions = [];

          (window.voilaLtMatches || []).forEach(function (match) {
            const matchRange = rangeFromMatch(match);

            if (!rangesIntersect(matchRange, range)) return;

            (match.replacements || []).slice(0, 5).forEach(function (replacement) {
              actions.push({
                title: "LanguageTool: " + replacement,
                kind: "quickfix",
                edit: {
                  edits: [{
                    resource: model.uri,
                    edit: {
                      range: matchRange,
                      text: replacement
                    }
                  }]
                }
              });
            });
          });

          return {
            actions: actions,
            dispose: function () {}
          };
        }
      });

      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Period, function () {
        editor.getAction("editor.action.quickFix").run();
      });

      window.voilaSetLanguageToolMarkers = function (matches) {
        window.voilaLtMatches = matches || [];
        window.voilaLtIndex = 0;

        const markers = window.voilaLtMatches.map(function (match) {
          const range = rangeFromMatch(match);

          return {
            severity: monaco.MarkerSeverity.Warning,
            startLineNumber: range.startLineNumber,
            startColumn: range.startColumn,
            endLineNumber: range.endLineNumber,
            endColumn: range.endColumn,
            message: match.message || "LanguageTool suggestion",
            source: "LanguageTool",
            code: match.ruleId || ""
          };
        });

        monaco.editor.setModelMarkers(model, "languagetool", markers);

        if (!markers.length) {
          setStatus("<strong>LanguageTool:</strong> 0 probleme evidente.");
        } else {
          setStatus(
            "<strong>LanguageTool:</strong> " + markers.length +
            " sugestii. Click pe subliniere sau Ctrl+. pentru quick fix."
          );
        }
      };

      window.voilaGoToLanguageToolIssue = function (direction) {
        const matches = window.voilaLtMatches || [];
        if (!matches.length) return;

        window.voilaLtIndex += direction;

        if (window.voilaLtIndex < 0) window.voilaLtIndex = matches.length - 1;
        if (window.voilaLtIndex >= matches.length) window.voilaLtIndex = 0;

        const range = rangeFromMatch(matches[window.voilaLtIndex]);
        editor.setSelection(range);
        editor.revealRangeInCenter(range);
        editor.focus();

        setStatus(
          "<strong>LanguageTool:</strong> sugestia " +
          (window.voilaLtIndex + 1) + " / " + matches.length +
          ". Ctrl+. pentru quick fix."
        );
      };

      prevButton.addEventListener("click", function () {
        window.voilaGoToLanguageToolIssue(-1);
      });

      nextButton.addEventListener("click", function () {
        window.voilaGoToLanguageToolIssue(1);
      });

      checkButton.addEventListener("click", async function () {
        syncToTextarea();

        const effectiveLanguage = getEffectiveLanguage(langSelect.value, textarea.value || "");
        const ltLanguage = LT_LANG[effectiveLanguage] || "en-US";

        checkButton.disabled = true;
        const oldLabel = checkButton.textContent;
        checkButton.textContent = "Verific...";

        setStatus("<strong>LanguageTool:</strong> verific textul cu " + ltLanguage + "...");

        try {
          const response = await fetch("/check-ocr-languagetool", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text: textarea.value || "",
              language: ltLanguage
            })
          });

          const data = await response.json();

          if (!data.ok) {
            setStatus("<strong>LanguageTool:</strong> " + (data.message || "nu rulează."));
            return;
          }

          window.voilaSetLanguageToolMarkers(data.matches || []);
        } catch (err) {
          setStatus("<strong>LanguageTool:</strong> eroare: " + (err.message || String(err)));
        } finally {
          checkButton.disabled = false;
          checkButton.textContent = oldLabel;
        }
      });

      editor.setPosition({ lineNumber: 1, column: 1 });
      editor.revealLine(1);
      editor.focus();

      const effectiveInitial = getEffectiveLanguage(langSelect.value, model.getValue());
      setStatus(
        "<strong>Editor:</strong> Monaco activ. Limba: " +
        LANGUAGE_LABELS[langSelect.value] +
        " · LanguageTool: " +
        (LT_LANG[effectiveInitial] || "en-US") +
        ". Ctrl+. = quick fix."
      );
    }, function () {
      fallback("<strong>Editor:</strong> Monaco nu a putut fi inițializat.");
    });
  });
})();
''', encoding="utf-8")

print("OK: multilingual Monaco OCR review JS written.")
