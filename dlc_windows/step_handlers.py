# course_framework/step_handlers.py

def is_interactive(step: dict) -> bool:
    return step.get("type") in ("now_you", "quiz", "fix_the_code")


def needs_editor(step: dict) -> bool:
    return step.get("type") in ("now_you", "ghost_demo", "fix_the_code")


def needs_preview(step: dict) -> bool:
    return step.get("type") in ("ghost_demo", "now_you")


def auto_complete(step: dict) -> bool:
    return step.get("type") in ("intro", "lesson", "text", "ghost_demo")
