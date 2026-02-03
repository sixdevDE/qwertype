from __future__ import annotations
from typing import Optional

def badge_for_ratio(r: float) -> Optional[str]:
    if r >= 1.0:
        return "gold"
    if r >= 0.66:
        return "silver"
    if r >= 0.33:
        return "bronze"
    return None
