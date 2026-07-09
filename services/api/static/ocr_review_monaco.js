/* VOILA_V0_7_40_NATIVE_OCR_REVIEW_TOOLS_NO_MONACO */
(function () {
  if (window.voilaNativeOcrReviewToolsNoMonaco) return;
  window.voilaNativeOcrReviewToolsNoMonaco = true;

  const LT_LANG = {
    auto: "ro-RO",
    ro: "ro-RO",
    en: "en-US",
    fr: "fr-FR",
    de: "de-DE",
    it: "it-IT",
    es: "es-ES",
    pt: "pt-PT",
    ru: "ru-RU"
  };

  const LANGUAGE_LABELS = {
    auto: "Auto",
    ro: "Română",
    en: "English",
    fr: "Français",
    de: "Deutsch",
    it: "Italiano",
    es: "Español",
    pt: "Português",
    ru: "Русский"
  };

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  function enc(value) {
    return encodeURIComponent(value || "");
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

  function getPageNumber() {
    const url = new URL(window.location.href);
    return Number(url.searchParams.get("page") || "1");
  }

  function detectLanguageFromText(value) {
    const text = String(value || "").toLowerCase();
    if (/[а-яё]/i.test(text)) return "ru";

    const scores = { ro: 0, en: 0, fr: 0, de: 0, it: 0, es: 0, pt: 0 };
    ["ă","â","î","ș","ţ","ț"].forEach(function (ch) { if (text.includes(ch)) scores.ro += 3; });
    [" the "," and "," of "," to "," is "].forEach(function (w) { if (text.includes(w)) scores.en += 1; });
    [" le "," la "," les "," des "," une "].forEach(function (w) { if (text.includes(w)) scores.fr += 1; });
    [" der "," die "," und "," ist "," nicht "].forEach(function (w) { if (text.includes(w)) scores.de += 1; });
    [" il "," che "," una "," con "," per "].forEach(function (w) { if (text.includes(w)) scores.it += 1; });
    [" el "," que "," una "," con "," para "].forEach(function (w) { if (text.includes(w)) scores.es += 1; });
    [" que "," uma "," com "," para "," não "].forEach(function (w) { if (text.includes(w)) scores.pt += 1; });

    return Object.keys(scores).sort(function (a, b) { return scores[b] - scores[a]; })[0] || "ro";
  }

  function effectiveLanguage(selected, text) {
    return selected === "auto" ? detectLanguageFromText(text) : selected;
  }

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function installStyle() {
    if (document.getElementById("voila-native-ocr-review-tools-css")) return;

    const style = document.createElement("style");
    style.id = "voila-native-ocr-review-tools-css";
    style.textContent = [
      "#voilaOcrReviewToolbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:10px 0 12px}",
      "#voilaOcrReviewToolbar button,#voilaOcrReviewToolbar select{border-radius:999px;padding:8px 12px;font-weight:800}",
      "#voilaOcrReviewToolbar button.primary{background:#e6ad62;color:#101819;border-color:transparent}",
      "#voilaOcrReviewStatus{font-size:13px;line-height:1.2;margin:6px 0 6px;color:#e9c39b}",
      "#voilaOcrReviewStatus strong{color:#f3b765}",
      "#voilaLtPanel{border:1px solid rgba(230,173,98,.25);border-radius:12px;padding:7px 9px;margin:6px 0;background:rgba(255,255,255,.035)}",
      "#voilaLtPanel[hidden]{display:none!important}",
      "#voilaLtPanel .lt-compact{display:flex;gap:6px;align-items:center;flex-wrap:wrap}",
      "#voilaLtPanel .lt-actions-only{padding:0;margin:0}",
      "#voilaLtPanel button{border-radius:999px;padding:5px 8px;font-size:12px;font-weight:800}",
      "[data-voila-hidden-native-ocr-submit='1']{display:none!important;visibility:hidden!important;pointer-events:none!important}",
      "textarea#ocrText, textarea[name='text'], textarea[name='corrected_text']{display:block!important;width:100%;min-height:260px;font-family:Consolas,'Cascadia Mono','Courier New',monospace;font-size:18px;line-height:1.55}"
    ].join("\\n");

    document.head.appendChild(style);
  }

  ready(function () {
    installStyle();

    const textarea = findOcrTextarea();
    if (!textarea) {
      console.warn("Voila OCR Review: no textarea found.");
      return;
    }

    if (!textarea.id) textarea.id = "ocrText";

    const form = textarea.closest("form");
    const pdfName = getPdfName();

    let ltMatches = [];
    let ltIndex = 0;

    const toolbar = document.createElement("div");
    toolbar.id = "voilaOcrReviewToolbar";

    const uiLangSelect = document.createElement("select");
    uiLangSelect.innerHTML = '<option value="ro">Română</option><option value="en">English</option>';
    uiLangSelect.value = "ro";
    uiLangSelect.title = "Limba interfeței";

    const langSelect = document.createElement("select");
    ["ro","en","fr","de","it","es","pt","ru"].forEach(function (lang) {
      const option = document.createElement("option");
      option.value = lang;
      option.textContent = LANGUAGE_LABELS[lang] || lang;
      langSelect.appendChild(option);
    });
    langSelect.value = "ro";
    langSelect.title = "Limba documentului";

    const columnsSelect = document.createElement("select");
    columnsSelect.innerHTML =
      '<option value="0">OCR normal</option>' +
      '<option value="2">OCR 2 coloane</option>' +
      '<option value="3">OCR 3 coloane</option>';
    columnsSelect.value = "3";

    function button(label, className) {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = label;
      if (className) b.className = className;
      return b;
    }

    const runOcrButton = button("Rulează OCR pagină", "primary");
    const checkButton = button("Verifică text");
    const saveButton = button("Salvează", "primary");
    const prevIssueButton = button("← problemă");
    const nextIssueButton = button("problemă →");

    [uiLangSelect, langSelect, columnsSelect, runOcrButton, checkButton, saveButton, prevIssueButton, nextIssueButton]
      .forEach(function (el) { toolbar.appendChild(el); });

    const status = document.createElement("div");
    status.id = "voilaOcrReviewStatus";
    status.innerHTML = "";

    const ltPanel = document.createElement("div");
    ltPanel.id = "voilaLtPanel";
    ltPanel.hidden = true;

    textarea.insertAdjacentElement("beforebegin", toolbar);
    toolbar.insertAdjacentElement("afterend", status);
    status.insertAdjacentElement("afterend", ltPanel);

    function setStatus(message) {
      status.innerHTML = message || "";
    }

    function flashStatus() {
      status.style.outline = "2px solid rgba(230,173,98,.85)";
      status.style.borderRadius = "10px";
      status.style.padding = "8px 10px";
      window.setTimeout(function () {
        status.style.outline = "";
      }, 1200);
    }

    function hideNativeOcrReviewSubmitButtons() {
      const selector = 'button, a, input[type="submit"], input[type="button"]';
      Array.from(document.querySelectorAll(selector)).forEach(function (el) {
        const label = labelOf(el);
        if (
          label.includes("apply corrected ocr") ||
          label.includes("pages.json") ||
          label.includes("save reviewed page") ||
          label.includes("save as needs review")
        ) {
          el.dataset.voilaHiddenNativeOcrSubmit = "1";
          el.style.setProperty("display", "none", "important");
          el.style.setProperty("visibility", "hidden", "important");
          el.style.setProperty("pointer-events", "none", "important");
        }
      });
    }

    hideNativeOcrReviewSubmitButtons();
    window.setTimeout(hideNativeOcrReviewSubmitButtons, 250);
    window.setTimeout(hideNativeOcrReviewSubmitButtons, 1000);

    function scrollTextareaToOffset(offset) {
      const safeOffset = Math.max(0, Number(offset || 0));
      const before = textarea.value.slice(0, safeOffset);
      const lineIndex = before.split(/\r\n|\r|\n/).length - 1;
      const computed = window.getComputedStyle(textarea);
      const lineHeight = parseFloat(computed.lineHeight) || 26;
      const targetTop = Math.max(0, (lineIndex * lineHeight) - (textarea.clientHeight * 0.35));
      textarea.scrollTop = targetTop;
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

    function renderLtPanel() {
      if (!ltMatches.length) {
        ltPanel.hidden = true;
        return;
      }

      if (ltIndex < 0) ltIndex = 0;
      if (ltIndex >= ltMatches.length) ltIndex = ltMatches.length - 1;

      const match = ltMatches[ltIndex] || {};
      const replacements = match.replacements || [];

      const buttons = replacements.slice(0, 6).map(function (replacement, index) {
        const text = String(replacement.value || replacement || "");
        return '<button type="button" class="lt-replace" data-index="' + index + '">' +
          escapeHtml(text) +
          '</button>';
      }).join("");

      ltPanel.hidden = false;
      ltPanel.innerHTML =
        '<div class="lt-compact lt-actions-only">' +
          buttons +
        '</div>';

      Array.from(ltPanel.querySelectorAll(".lt-replace")).forEach(function (btn) {
        btn.addEventListener("click", function () {
          const replacement = replacements[Number(btn.dataset.index || "0")] || "";
          const replacementText = String(replacement.value || replacement || "");
          const start = Math.max(0, Number(match.offset || 0));
          const len = Math.max(1, Number(match.length || 1));
          const before = textarea.value.slice(0, start);
          const after = textarea.value.slice(start + len);
          textarea.value = before + replacementText + after;
          ltMatches.splice(ltIndex, 1);
          setStatus("");
          renderLtPanel();
        });
      });
    }

    function goToIssue(direction, sourceButton) {
      const oldLabel = sourceButton ? sourceButton.textContent : "";

      if (sourceButton) sourceButton.textContent = "Click primit";

      if (!ltMatches.length) {
        ltPanel.hidden = true;
        setStatus("<strong>LanguageTool:</strong> nu există o problemă selectabilă. Rulează „Verifică text”; dacă rezultatul este 0 probleme, aceste butoane nu au unde naviga.");
        flashStatus();
        textarea.focus({ preventScroll: true });
        if (sourceButton) {
          window.setTimeout(function () { sourceButton.textContent = oldLabel; }, 900);
        }
        return;
      }

      ltIndex += direction;
      if (ltIndex < 0) ltIndex = ltMatches.length - 1;
      if (ltIndex >= ltMatches.length) ltIndex = 0;

      const match = ltMatches[ltIndex] || {};
      const start = Math.max(0, Number(match.offset || 0));
      const end = start + Math.max(1, Number(match.length || 1));

      try {
        textarea.focus({ preventScroll: true });
        textarea.setSelectionRange(start, end);
        scrollTextareaToOffset(start);
      } catch (_) {}

      const label = "Problema " + (ltIndex + 1) + "/" + ltMatches.length;
      setStatus("");
      flashStatus();
      renderLtPanel();

      try {
        textarea.focus({ preventScroll: true });
        textarea.setSelectionRange(start, end);
        scrollTextareaToOffset(start);
      } catch (_) {}

      if (sourceButton) {
        sourceButton.textContent = label;
        window.setTimeout(function () { sourceButton.textContent = oldLabel; }, 900);
      }
    }

    saveButton.addEventListener("click", function () {
      const submit = findReviewedSubmitButton();
      if (form && submit && form.requestSubmit) {
        form.requestSubmit(submit);
      } else if (submit) {
        submit.click();
      } else if (form) {
        form.submit();
      }
    });

    prevIssueButton.addEventListener("click", function () {
      goToIssue(-1, prevIssueButton);
    });

    nextIssueButton.addEventListener("click", function () {
      goToIssue(1, nextIssueButton);
    });

    checkButton.addEventListener("click", async function () {
      const selected = langSelect.value || "auto";
      const effective = effectiveLanguage(selected, textarea.value || "");
      const ltLanguage = LT_LANG[effective] || "ro-RO";

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
          ltMatches = [];
          ltIndex = 0;
          ltPanel.hidden = true;
          setStatus("<strong>LanguageTool:</strong> " + (data.message || "nu răspunde."));
          flashStatus();
          return;
        }

        ltMatches = data.matches || [];
        ltIndex = 0;

        if (!ltMatches.length) {
          ltPanel.hidden = true;
          setStatus("<strong>LanguageTool:</strong> 0 probleme evidente.");
          flashStatus();
          return;
        }

        setStatus("<strong>LT:</strong> " + ltMatches.length + " sugestii.");
        goToIssue(0, null);
      } catch (err) {
        ltMatches = [];
        ltIndex = 0;
        ltPanel.hidden = true;
        setStatus("<strong>LanguageTool:</strong> eroare: " + (err.message || String(err)));
        flashStatus();
      } finally {
        checkButton.disabled = false;
        checkButton.textContent = oldLabel;
      }
    });

    runOcrButton.addEventListener("click", async function () {
      const pageNumber = getPageNumber();

      if (!pdfName || !pageNumber) {
        setStatus("<strong>OCR:</strong> nu pot determina PDF-ul sau pagina.");
        flashStatus();
        return;
      }

      runOcrButton.disabled = true;
      const oldLabel = runOcrButton.textContent;
      runOcrButton.textContent = "OCR...";

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
            columns: Number(columnsSelect.value || "0")
          })
        });

        const data = await response.json();

        if (!data.ok) {
          setStatus("<strong>OCR:</strong> " + (data.message || "eroare") + "<br><pre>" + String(data.stderr || data.stdout || "").slice(-900) + "</pre>");
          flashStatus();
          return;
        }

        setStatus("<strong>OCR:</strong> gata. Reîncarc pagina...");
        const url = new URL(window.location.href);
        url.searchParams.set("v", Date.now());
        window.location.href = url.toString();
      } catch (err) {
        setStatus("<strong>OCR:</strong> eroare: " + (err.message || String(err)));
        flashStatus();
      } finally {
        runOcrButton.disabled = false;
        runOcrButton.textContent = oldLabel;
      }
    });
  });
})();
