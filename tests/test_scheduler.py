"""Tests for TransitionScheduler."""

import pytest
from datetime import datetime
from chrono_wallpaper.core.scheduler import TransitionScheduler


class TestTransitionScheduler:
    """Test time-based blend factor calculations."""

    def test_full_day(self):
        """Test full day period returns 0.0."""
        scheduler = TransitionScheduler()
        day_time = datetime(2024, 1, 1, 12, 0)  # Noon
        assert scheduler.get_blend_factor(day_time) == 0.0

    def test_full_night(self):
        """Test full night period returns 1.0."""
        scheduler = TransitionScheduler()
        night_time = datetime(2024, 1, 1, 3, 0)  # 3 AM
        assert scheduler.get_blend_factor(night_time) == 1.0

    def test_morning_start(self):
        """Test morning transition start (6:00)."""
        scheduler = TransitionScheduler()
        morning_start = datetime(2024, 1, 1, 6, 0)
        assert scheduler.get_blend_factor(morning_start) == 1.0

    def test_morning_middle(self):
        """Test morning transition middle (6:30)."""
        scheduler = TransitionScheduler()
        morning_mid = datetime(2024, 1, 1, 6, 30)
        assert scheduler.get_blend_factor(morning_mid) == 0.5

    def test_evening_start(self):
        """Test evening transition start (22:00)."""
        scheduler = TransitionScheduler()
        evening_start = datetime(2024, 1, 1, 22, 0)
        assert scheduler.get_blend_factor(evening_start) == 0.0

    def test_evening_middle(self):
        """Test evening transition middle (23:00)."""
        scheduler = TransitionScheduler()
        evening_mid = datetime(2024, 1, 1, 23, 0)
        assert scheduler.get_blend_factor(evening_mid) == 0.5
