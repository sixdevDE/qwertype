# course_framework/course_engine.py

class CourseEngine:
    def __init__(self, steps: list):
        self.steps = steps
        self.index = 0
        self.completed = {}

    def current_step(self) -> dict:
        return self.steps[self.index]

    def is_completed(self) -> bool:
        step_id = self.current_step().get("id", self.index)
        return self.completed.get(step_id, False)

    def mark_completed(self):
        step_id = self.current_step().get("id", self.index)
        self.completed[step_id] = True

    def can_continue(self) -> bool:
        step = self.current_step()
        if step.get("type") in ("now_you", "quiz", "fix_the_code"):
            return self.is_completed()
        return True

    def next(self):
        if not self.can_continue():
            return False
        if self.index < len(self.steps) - 1:
            self.index += 1
            return True
        return False

    def back(self):
        if self.index > 0:
            self.index -= 1
            return True
        return False
