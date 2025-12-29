"""Configuration schema."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class WallpaperConfig:
    """Main configuration."""
    day_image: Path
    night_image: Path
    output_dir: Path
    compositor: str = "swaybg"
    morning_start: int = 6
    morning_end: int = 7
    evening_start: int = 22
    evening_end: int = 0
