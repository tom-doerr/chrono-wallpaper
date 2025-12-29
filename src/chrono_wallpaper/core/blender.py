"""Image blending for wallpaper transitions."""

from PIL import Image
import numpy as np
from pathlib import Path
import hashlib
import logging


logger = logging.getLogger(__name__)


class ImageBlender:
    """Blend two images with caching and optimization."""

    def __init__(self, cache_dir: Path, hash_check: bool = True):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.hash_check = hash_check

    def blend(self, day_path: Path, night_path: Path, factor: float) -> Image.Image:
        """Blend two images based on factor (0.0 = day, 1.0 = night)."""
        # Validate inputs
        if not 0 <= factor <= 1:
            raise ValueError(f"Blend factor must be 0-1, got {factor}")

        if not day_path.exists():
            raise FileNotFoundError(f"Day image not found: {day_path}")
        if not night_path.exists():
            raise FileNotFoundError(f"Night image not found: {night_path}")

        # Load images
        day_img = Image.open(day_path)
        night_img = Image.open(night_path)

        if day_img.size != night_img.size:
            raise ValueError(
                f"Images must have same dimensions. "
                f"Day: {day_img.size}, Night: {night_img.size}"
            )

        # Blend using numpy
        day_arr = np.array(day_img, dtype=np.float32)
        night_arr = np.array(night_img, dtype=np.float32)

        blended = day_arr * (1 - factor) + night_arr * factor
        return Image.fromarray(blended.astype(np.uint8))

    def needs_update(self, current_path: Path, new_image: Image.Image) -> bool:
        """Check if wallpaper needs updating using hash comparison."""
        if not self.hash_check:
            return True

        if not current_path.exists():
            return True

        new_hash = hashlib.md5(new_image.tobytes()).hexdigest()
        old_img = Image.open(current_path)
        old_hash = hashlib.md5(old_img.tobytes()).hexdigest()

        return new_hash != old_hash