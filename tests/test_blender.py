"""Tests for ImageBlender."""

import pytest
import numpy as np
from pathlib import Path
from PIL import Image
from chrono_wallpaper.core.blender import ImageBlender


@pytest.fixture
def test_images(tmp_path):
    """Create test day and night images."""
    # Create 10x10 images
    day_img = Image.new("RGB", (10, 10), color=(255, 255, 255))  # White
    night_img = Image.new("RGB", (10, 10), color=(0, 0, 0))  # Black

    day_path = tmp_path / "day.png"
    night_path = tmp_path / "night.png"
    day_img.save(day_path)
    night_img.save(night_path)

    return day_path, night_path


class TestImageBlender:
    """Test image blending functionality."""

    def test_blend_full_day(self, test_images, tmp_path):
        """Test blend with factor 0.0 (full day)."""
        day_path, night_path = test_images
        blender = ImageBlender(cache_dir=tmp_path)
        result = blender.blend(day_path, night_path, 0.0)

        # Should be all white
        arr = np.array(result)
        assert np.all(arr == 255)

    def test_blend_full_night(self, test_images, tmp_path):
        """Test blend with factor 1.0 (full night)."""
        day_path, night_path = test_images
        blender = ImageBlender(cache_dir=tmp_path)
        result = blender.blend(day_path, night_path, 1.0)

        # Should be all black
        arr = np.array(result)
        assert np.all(arr == 0)

    def test_blend_halfway(self, test_images, tmp_path):
        """Test blend with factor 0.5 (halfway)."""
        day_path, night_path = test_images
        blender = ImageBlender(cache_dir=tmp_path)
        result = blender.blend(day_path, night_path, 0.5)

        # Should be gray (127)
        arr = np.array(result)
        assert np.all(arr == 127)

    def test_invalid_factor(self, test_images, tmp_path):
        """Test that invalid blend factor raises ValueError."""
        day_path, night_path = test_images
        blender = ImageBlender(cache_dir=tmp_path)

        with pytest.raises(ValueError):
            blender.blend(day_path, night_path, 1.5)

    def test_needs_update_new_file(self, test_images, tmp_path):
        """Test needs_update returns True for non-existent file."""
        day_path, night_path = test_images
        blender = ImageBlender(cache_dir=tmp_path)
        img = blender.blend(day_path, night_path, 0.5)

        output_path = tmp_path / "output.png"
        assert blender.needs_update(output_path, img) is True

    def test_needs_update_same_content(self, test_images, tmp_path):
        """Test needs_update returns False for identical file."""
        day_path, night_path = test_images
        blender = ImageBlender(cache_dir=tmp_path)
        img = blender.blend(day_path, night_path, 0.5)

        output_path = tmp_path / "output.png"
        img.save(output_path)
        assert blender.needs_update(output_path, img) is False
