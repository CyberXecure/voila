
(function () {
  window.VOILA_MONACO_JS_LOADED = true;
  console.log("Voila Monaco OCR JS loaded");

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

  function detectVoilaOcrLanguage(value) {
    const text = String(value || "").toLowerCase();

    const roChars = /[ăâîșşțţ]/i.test(text) ? 4 : 0;

    const roWords = [
      "pentru", "este", "sunt", "care", "prin", "în", "din", "funcție",
      "tensiune", "curent", "lămpii", "instalații", "capitolul", "figura"
    ];

    const enWords = [
      "the", "and", "with", "from", "figure", "chapter", "valve",
      "engine", "fuel", "injection", "pressure", "temperature", "system"
    ];

    let roScore = roChars;
    let enScore = 0;

    roWords.forEach(function (word) {
      if (text.includes(word)) roScore += 1;
    });

    enWords.forEach(function (word) {
      if (text.includes(word)) enScore += 1;
    });

    if (enScore > roScore) return "en-US";
    return "ro-RO";
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

    const form = textarea.closest("form");

    const toolbar = document.createElement("div");
    toolbar.id = "voilaMonacoToolbar";

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

        checkButton.disabled = true;
        const oldLabel = checkButton.textContent;
        checkButton.textContent = "Verific...";

        const detectedLanguage = detectVoilaOcrLanguage(textarea.value || "");
        setStatus("<strong>LanguageTool:</strong> verific textul cu limba " + detectedLanguage + "...");

        try {
          const response = await fetch("/check-ocr-languagetool", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text: textarea.value || "",
              language: detectedLanguage
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

      setStatus("<strong>Editor:</strong> Monaco activ. Ctrl+. = quick fix; Alt+N / Alt+P = navigare LanguageTool.");
    }, function () {
      fallback("<strong>Editor:</strong> Monaco nu a putut fi inițializat.");
    });
  });
})();
