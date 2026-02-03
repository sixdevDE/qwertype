# course_framework/progress.py

def chapter_progress(chapter_steps: list, completed: dict) -> float:
    done = sum(1 for s in chapter_steps if completed.get(s.get("id")))
    return done / max(1, len(chapter_steps))


def award_badge(progress: float) -> str | None:
    if progress >= 1.0:
        return "gold"
    if progress >= 0.66:
        return "silver"
    if progress >= 0.33:
        return "bronze"
    return None
