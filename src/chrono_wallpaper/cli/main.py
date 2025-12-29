"""Command-line interface for chrono-wallpaper."""

import click
import logging
from pathlib import Path
from chrono_wallpaper.core.compositor import CompositorManager
from chrono_wallpaper.core.scheduler import TransitionScheduler
from chrono_wallpaper.core.blender import ImageBlender
from chrono_wallpaper.config.schema import WallpaperConfig


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@click.group()
def cli():
    """Chrono-Wallpaper: Time-based wallpaper transitions."""
    pass


@cli.command()
def run():
    """Run wallpaper update."""
    config = WallpaperConfig(
        day_image=Path.home() / "Pictures/anime-girl.png",
        night_image=Path.home() / "Pictures/wallpaper-night.png",
        output_dir=Path.home() / ".cache/chrono-wallpaper"
    )

    scheduler = TransitionScheduler()
    factor = scheduler.get_blend_factor()
    print(f"Blend factor: {factor:.2%}")

    # Create output directory
    config.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = config.output_dir / "current.png"

    # Blend images
    blender = ImageBlender(cache_dir=config.output_dir)
    blended = blender.blend(config.day_image, config.night_image, factor)

    # Check if update needed
    if not blender.needs_update(output_path, blended):
        print("Wallpaper unchanged, skipping update")
        return

    # Save blended image
    blended.save(output_path)
    print(f"Saved blended wallpaper to {output_path}")

    # Set wallpaper
    compositor = CompositorManager(compositor=config.compositor)
    if compositor.set_wallpaper(output_path):
        print("Wallpaper updated successfully")
    else:
        print("Failed to set wallpaper")
