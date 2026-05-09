
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request


DEFAULT_LT_URL = "http://127.0.0.1:8081/v2/check"


def check_text(
    text: str,
    language: str = "ro-RO",
    lt_url: str | None = None,
    timeout: int = 20,
) -> dict:
    text = str(text or "")

    if not text.strip():
        return {
            "ok": True,
            "provider": "LanguageTool",
            "matches": [],
            "message": "Text gol.",
        }

    url = (lt_url or os.environ.get("VOILA_LANGUAGETOOL_URL") or DEFAULT_LT_URL).strip()

    payload = urllib.parse.urlencode(
        {
            "text": text,
            "language": language or "ro-RO",
            "enabledOnly": "false",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
    except Exception as exc:
        return {
            "ok": False,
            "provider": "LanguageTool",
            "url": url,
            "matches": [],
            "message": (
                "LanguageTool nu răspunde. Pornește serverul local pe 127.0.0.1:8081 "
                "sau setează VOILA_LANGUAGETOOL_URL."
            ),
            "error": str(exc),
        }

    matches = []

    for item in data.get("matches", []):
        replacements = item.get("replacements", []) or []

        matches.append(
            {
                "message": item.get("message") or "",
                "shortMessage": item.get("shortMessage") or "",
                "offset": int(item.get("offset") or 0),
                "length": int(item.get("length") or 0),
                "context": (item.get("context") or {}).get("text") or "",
                "contextOffset": int((item.get("context") or {}).get("offset") or 0),
                "ruleId": (item.get("rule") or {}).get("id") or "",
                "category": ((item.get("rule") or {}).get("category") or {}).get("name") or "",
                "issueType": (item.get("rule") or {}).get("issueType") or "",
                "replacements": [
                    str(rep.get("value") or "")
                    for rep in replacements[:8]
                    if str(rep.get("value") or "").strip()
                ],
            }
        )

    return {
        "ok": True,
        "provider": "LanguageTool",
        "url": url,
        "language": data.get("language", {}).get("detectedLanguage", {}).get("code") or language,
        "matches": matches,
        "match_count": len(matches),
        "message": f"{len(matches)} sugestii găsite.",
    }
