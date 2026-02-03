"""QwerType Course Framework (internal module)

UI-independent engine + validators for DLC courses.
"""

from .engine import CourseEngine, flatten_course_steps
from .validators import validate_step
from .ghost import GhostTyper
