
(function () {
  window.VOILA_MONACO_JS_LOADED = true;
  console.log("Voila Monaco OCR JS loaded - multilingual");

  const LANGUAGE_LABELS = {
    auto: "Auto",
    ro: "Română",
    en: "English",
    fr: "Français",
    de: "Deutsch",
    ru: "Русский",
    it: "Italiano",
    es: "Español",
    pt: "Português"
  };

  const LT_LANG = {
    ro: "ro-RO",
    en: "en-US",
    fr: "fr",
    de: "de-DE",
    ru: "ru-RU",
    it: "it",
    es: "es",
    pt: "pt"
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

    const scores = { ro: 0, en: 0, fr: 0, de: 0, it: 0, es: 0, pt: 0 };

    if (/[ăâîșşțţ]/i.test(text)) scores.ro += 5;
    if (/[éèêëàâîïôùûçœ]/i.test(text)) scores.fr += 4;
    if (/[äöüß]/i.test(text)) scores.de += 4;
    if (/[àèéìíîòóùú]/i.test(text)) scores.it += 3;
    if (/[áéíóúñü¿¡]/i.test(text)) scores.es += 3;
    if (/[ãõçáàâéêíóôú]/i.test(text)) scores.pt += 3;

    const markers = {
      ro: ["pentru", "este", "sunt", "care", "prin", "din", "funcție", "capitolul", "figura"],
      en: ["the", "and", "with", "from", "figure", "chapter", "system", "pressure", "temperature"],
      fr: ["pour", "avec", "dans", "figure", "chapitre", "pression", "température", "système"],
      de: ["und", "mit", "der", "die", "das", "abbildung", "kapitel", "druck", "temperatur", "system"],
      it: ["per", "con", "della", "delle", "figura", "capitolo", "pressione", "temperatura", "sistema"],
      es: ["para", "con", "del", "de la", "figura", "capítulo", "presión", "temperatura", "sistema"],
      pt: ["para", "com", "do", "da", "figura", "capítulo", "pressão", "temperatura", "sistema"]
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
      "rus": "ru",
      "it-it": "it",
      "ita": "it",
      "es-es": "es",
      "spa": "es",
      "pt-pt": "pt",
      "pt-br": "pt",
      "por": "pt"
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
    toolbar.appendChild(ocrColumnsSelect);
    toolbar.appendChild(runOcrPageButton);
    toolbar.appendChild(checkButton);
    toolbar.appendChild(saveButton);
    toolbar.appendChild(prevButton);
    toolbar.appendChild(nextButton);

    const host = document.createElement("div");
    host.id = "voilaMonacoEditor";

    const status = document.createElement("div");
    status.id = "voilaMonacoStatus";
    status.innerHTML = "<strong>Editor:</strong> se încarcă Monaco...";

    const ltPanel = document.createElement("div");
    ltPanel.id = "voilaLtPanel";
    ltPanel.hidden = true;

    textarea.classList.add("voila-monaco-hidden");
    textarea.insertAdjacentElement("afterend", status);
    textarea.insertAdjacentElement("afterend", host);
    textarea.insertAdjacentElement("afterend", ltPanel);
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
        lightbulb: { enabled: false },
        fixedOverflowWidgets: true
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
                title: replacement + " — LanguageTool",
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
          ltPanel.hidden = true;
          setStatus("<strong>LanguageTool:</strong> 0 probleme evidente.");
        } else {
          setStatus(
            "<strong>LanguageTool:</strong> " + markers.length +
            " sugestii. Folosește panoul de sugestii de sub toolbar."
          );
          renderLtIssuePanel();
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
          (window.voilaLtIndex + 1) + " / " + matches.length
        );
        renderLtIssuePanel();
      };


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

      prevButton.addEventListener("click", function () {
        window.voilaGoToLanguageToolIssue(-1);
      });

      nextButton.addEventListener("click", function () {
        window.voilaGoToLanguageToolIssue(1);
      });

      runOcrPageButton.addEventListener("click", async function () {
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
              zoom: 3.0,
              columns: Number(ocrColumnsSelect.value || "0")
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
