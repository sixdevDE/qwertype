from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

INTERACTIVE_TYPES = {"now_you", "quiz", "fix_the_code"}

def flatten_course_steps(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten spec.course.chapters[*].steps[*] into a single list of steps.
    Adds: _chapter_title, _chapter_index, _step_index.
    """
    steps: List[Dict[str, Any]] = []
    course = (spec or {}).get("course", {}) or {}
    chapters = course.get("chapters", []) or []
    for ci, ch in enumerate(chapters):
        ch_title = ch.get("title", f"Chapter {ci+1}")
        for si, st in enumerate(ch.get("steps", []) or []):
            step = dict(st)  # copy
            step.setdefault("type", "text")
            step.setdefault("title", "")
            step.setdefault("content", [])
            step["_chapter_title"] = ch_title
            step["_chapter_index"] = ci
            step["_step_index"] = si
            if "id" not in step or not step["id"]:
                step["id"] = f"c{ci}_s{si}_{step.get('type','text')}"
            steps.append(step)
    return steps

@dataclass
class StepState:
    completed: bool = False
    score: Optional[float] = None
    attempts: int = 0

class CourseEngine:
    """UI-independent course engine: navigation + gating + completion state."""
    def __init__(self, steps: List[Dict[str, Any]]):
        if not steps:
            raise ValueError("CourseEngine requires at least one step.")
        self.steps = steps
        self.index = 0
        self.state: Dict[str, StepState] = {}

    def current(self) -> Dict[str, Any]:
        return self.steps[self.index]

    def current_id(self) -> str:
        return str(self.current().get("id", self.index))

    def current_type(self) -> str:
        return str(self.current().get("type", "text"))

    def is_interactive(self, step: Optional[Dict[str, Any]] = None) -> bool:
        st = step or self.current()
        return str(st.get("type", "text")) in INTERACTIVE_TYPES

    def get_state(self, step_id: Optional[str] = None) -> StepState:
        sid = step_id or self.current_id()
        if sid not in self.state:
            self.state[sid] = StepState()
        return self.state[sid]

    def mark_attempt(self, ok: bool, score: Optional[float] = None):
        s = self.get_state()
        s.attempts += 1
        if score is not None:
            s.score = score
        if ok:
            s.completed = True

    def can_continue(self) -> bool:
        step = self.current()
        if not self.is_interactive(step):
            return True
        if step.get("requires_completion", True) is False:
            return True
        return self.get_state().completed

    def next(self) -> bool:
        if not self.can_continue():
            return False
        if self.index < len(self.steps) - 1:
            self.index += 1
            return True
        return False

    def back(self) -> bool:
        if self.index > 0:
            self.index -= 1
            return True
        return False

    def progress_ratio(self) -> float:
        done = 0
        for st in self.steps:
            sid = str(st.get("id"))
            if self.is_interactive(st) and st.get("requires_completion", True) is not False:
                if self.state.get(sid, StepState()).completed:
                    done += 1
            else:
                done += 1
        return done / max(1, len(self.steps))
