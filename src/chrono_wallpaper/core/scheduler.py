"""Time-based transition scheduling."""

from datetime import datetime
from typing import Optional


class TransitionScheduler:
    """Calculate blend factors based on time of day."""

    def __init__(self, morning_start: int = 6, morning_end: int = 7,
                 evening_start: int = 22, evening_end: int = 0):
        self.morning_start = morning_start
        self.morning_end = morning_end
        self.evening_start = evening_start
        self.evening_end = evening_end

    def get_blend_factor(self, now: Optional[datetime] = None) -> float:
        """
        Calculate blend factor (0.0 = day, 1.0 = night).

        Returns:
            0.0 during day hours
            1.0 during night hours
            0.0-1.0 during transitions (smooth interpolation)
        """
        if now is None:
            now = datetime.now()

        hour = now.hour
        minute = now.minute

        # Evening transition: 22:00-00:00 (10pm to midnight) day→night
        if hour == 22:
            # 22:00 = 0%, 23:00 = 50%
            return minute / 120.0
        elif hour == 23:
            # 23:00 = 50%, 00:00 = 100%
            return 0.5 + (minute / 120.0)

        # Morning transition: 06:00-07:00 (6am to 7am) night→day
        elif hour == 6:
            # 06:00 = 100%, 07:00 = 0%
            return 1.0 - (minute / 60.0)

        # Full night: 00:00-06:00
        elif 0 <= hour < 6:
            return 1.0

        # Full day: 07:00-22:00
        else:
            return 0.0