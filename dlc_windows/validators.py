# course_framework/validators.py
import re

def validate(step: dict, code: str) -> tuple[bool, str]:
    checks = step.get("validation_checks", [])

    for c in checks:
        t = c.get("type")

        if t == "element_exists":
            tag = c.get("target", "")
            if f"<{tag}" not in code.lower():
                return False, f"<{tag}> fehlt"

        elif t == "attribute_exists_or_matches_pattern":
            pattern = c.get("pattern", "")
            if pattern and not re.search(pattern, code, re.IGNORECASE):
                return False, "Attribut/Pattern stimmt nicht"

        elif t == "regex":
            if not re.search(c.get("pattern", ""), code):
                return False, c.get("fail_msg", "Regex passt nicht")

    return True, "OK"
