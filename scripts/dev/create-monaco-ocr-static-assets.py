from pathlib import Path

root = Path(".")
static_dir = root / "services" / "api" / "static"
static_dir.mkdir(parents=True, exist_ok=True)

(static_dir / "ocr_review_monaco.css").write_text(r'''
/* Voila OCR Review Monaco */

#ocrText.voila-monaco-hidden {
  display: none !important;
}

#voilaMonacoEditor {
  flex: 1 1 auto;
  min-height: 0;
  width: 100%;
  border: 1px solid var(--line, #3b4b50);
  border-radius: 14px;
  overflow: hidden;
  background: #0c1416;
}

#voilaMonacoStatus {
  font-size: 12px;
  color: var(--muted, #c7ad94);
  line-height: 1.25;
  padding: 2px 0;
}

#voilaMonacoStatus strong {
  color: var(--accent, #e0ad68);
}

.voila-monaco-tools {
  display: inline-flex;
  gap: 6px;
  flex-wrap: wrap;
}

.voila-monaco-tools button {
  padding: 7px 10px !important;
  font-size: 13px !important;
  line-height: 1.1 !important;
  border-radius: 999px !important;
}
''', encoding="utf-8")

(static_dir / "ocr_review_monaco.js").write_text(r'''
(function () {
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

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(async function () {
    const textarea = document.getElementById("ocrText");
    if (!textarea) return;

    const form = textarea.closest("form");
    const actions = form ? form.querySelector(".actions") : null;

    const host = document.createElement("div");
    host.id = "voilaMonacoEditor";

    const status = document.createElement("div");
    status.id = "voilaMonacoStatus";
    status.innerHTML = "<strong>Editor:</strong> se încarcă Monaco...";

    textarea.classList.add("voila-monaco-hidden");
    textarea.insertAdjacentElement("afterend", host);
    host.insertAdjacentElement("afterend", status);

    function setStatus(message) {
      status.innerHTML = message || "";
    }

    function fallback(message) {
      textarea.classList.remove("voila-monaco-hidden");
      host.style.display = "none";
      setStatus(message || "<strong>Editor:</strong> Monaco nu a putut fi încărcat.");
    }

    let checkButton = document.getElementById("checkOcrButton");

    if (!checkButton && actions) {
      checkButton = document.createElement("button");
      checkButton.type = "button";
      checkButton.id = "checkOcrButton";
      checkButton.textContent = "Verifică text";
      checkButton.title = "Verifică textul cu LanguageTool și marchează problemele în editor.";

      const firstSubmit = actions.querySelector('button[type="submit"]');
      actions.insertBefore(checkButton, firstSubmit || actions.firstChild);
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

      editor.addAction({
        id: "voila-next-lt-issue",
        label: "LanguageTool: Next issue",
        keybindings: [monaco.KeyMod.Alt | monaco.KeyCode.KeyN],
        run: function () {
          window.voilaGoToLanguageToolIssue(1);
        }
      });

      editor.addAction({
        id: "voila-prev-lt-issue",
        label: "LanguageTool: Previous issue",
        keybindings: [monaco.KeyMod.Alt | monaco.KeyCode.KeyP],
        run: function () {
          window.voilaGoToLanguageToolIssue(-1);
        }
      });

      if (checkButton) {
        checkButton.addEventListener("click", async function () {
          syncToTextarea();

          checkButton.disabled = true;
          const oldLabel = checkButton.textContent;
          checkButton.textContent = "Verific...";

          setStatus("<strong>LanguageTool:</strong> verific textul...");

          try {
            const response = await fetch("/check-ocr-languagetool", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                text: textarea.value || "",
                language: "ro-RO"
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
      }

      editor.setPosition({ lineNumber: 1, column: 1 });
      editor.revealLine(1);
      editor.focus();

      setStatus("<strong>Editor:</strong> Monaco activ. Ctrl+. = quick fix; Alt+N / Alt+P = navigare LanguageTool.");
    }, function () {
      fallback("<strong>Editor:</strong> Monaco nu a putut fi inițializat.");
    });
  });
})();
''', encoding="utf-8")

print("OK: static Monaco OCR Review assets created.")
