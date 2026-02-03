from __future__ import annotations
from typing import Any, Dict, List, Tuple
import re

def _has_tag(code_lower: str, tag: str) -> bool:
    tag = (tag or "").strip().lower()
    if not tag:
        return True
    return f"<{tag}" in code_lower and f"</{tag}>" in code_lower

def validate_step(step: Dict[str, Any], code: str) -> Tuple[bool, str]:
    """Validate user input for a step. Returns (ok, message)."""
    checks: List[Dict[str, Any]] = (step or {}).get("validation_checks", []) or []
    if not checks:
        return True, step.get("success_msg", "OK")

    code = code or ""
    low = code.lower()

    for chk in checks:
        ctype = chk.get("type")
        if ctype == "element_exists":
            target = chk.get("target", "")
            if not _has_tag(low, target):
                return False, chk.get("fail_msg", f"<{target}> fehlt oder ist nicht geschlossen.")
        elif ctype == "contains":
            val = chk.get("value", "")
            if val and val not in code:
                return False, chk.get("fail_msg", f"Fehlt: {val}")
        elif ctype == "regex":
            pat = chk.get("pattern", "")
            flags = re.IGNORECASE | re.MULTILINE
            try:
                if not re.search(pat, code, flags):
                    return False, chk.get("fail_msg", "Pattern passt nicht.")
            except re.error:
                return False, chk.get("fail_msg", "Ungültiges Regex im Kurs-Check.")
        elif ctype == "attribute_exists_or_matches_pattern":
            pat = chk.get("pattern", "")
            if pat:
                try:
                    if not re.search(pat, code, re.IGNORECASE | re.MULTILINE):
                        return False, chk.get("fail_msg", "Attribut/Pattern stimmt nicht.")
                except re.error:
                    return False, chk.get("fail_msg", "Ungültiges Regex im Kurs-Check.")
            else:
                target = chk.get("target", "")
                if target and target.lower() not in low:
                    return False, chk.get("fail_msg", "Attribut fehlt.")
        else:
            continue

    return True, step.get("success_msg", "✅ Korrekt!")
