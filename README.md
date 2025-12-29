# Chrono-Wallpaper

Time-based wallpaper transitions for Wayland compositors.

## Features

- Smooth wallpaper transitions based on time of day
- Morning transition (6-7 AM): Night → Day
- Evening transition (10 PM - Midnight): Day → Night
- Efficient hash-based change detection
- Proper swaybg daemon lifecycle management
- Systemd timer integration

## Requirements

- Python 3.10+
- Wayland compositor (swaybg)
- uv package manager

## Installation

```bash
# Clone the repository
cd ~/git
git clone https://github.com/tom-doerr/chrono-wallpaper.git
cd chrono-wallpaper

# Install with uv
uv pip install -e .
```

## Usage

### Manual Run

```bash
chrono-wallpaper run
```

This will:
1. Calculate current blend factor based on time
2. Blend day and night wallpapers
3. Set the blended wallpaper using swaybg

### Systemd Timer

Install the systemd timer to run automatically during transition periods:

```bash
./systemd/install.sh
```

Check status:
```bash
systemctl --user status chrono-wallpaper.timer
journalctl --user -u chrono-wallpaper -f
```

## Configuration

Edit `src/chrono_wallpaper/cli/main.py` to set your wallpaper paths:

```python
config = WallpaperConfig(
    day_image=Path.home() / "Pictures/anime-girl.png",
    night_image=Path.home() / "Pictures/wallpaper-night.png",
    output_dir=Path.home() / ".cache/chrono-wallpaper"
)
```

### Transition Times

- **Morning**: 6:00-7:00 AM (night → day, factor 1.0 → 0.0)
- **Day**: 7:00 AM - 10:00 PM (factor 0.0)
- **Evening**: 10:00 PM - Midnight (day → night, factor 0.0 → 1.0)
- **Night**: Midnight - 6:00 AM (factor 1.0)

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
chrono-wallpaper/
├── src/chrono_wallpaper/
│   ├── cli/main.py        # CLI commands
│   ├── core/
│   │   ├── compositor.py  # swaybg lifecycle
│   │   ├── scheduler.py   # Time-based blend
│   │   └── blender.py     # Image blending
│   └── config/schema.py   # Configuration
├── tests/                 # pytest tests
└── systemd/               # Timer & service
```

## Key Features

### Proper Daemon Lifecycle

The compositor manager uses `psutil` for reliable swaybg lifecycle:
1. Kill existing swaybg processes
2. Wait for clean termination (timeout 2s)
3. Start new swaybg with `start_new_session=True`
4. Verify successful startup

This fixes the critical issue where swaybg would exit immediately.

## License

MIT
