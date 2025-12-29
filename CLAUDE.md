# Claude Context - Chrono-Wallpaper

## Critical Fix: swaybg Daemon Lifecycle

**The Problem**: swaybg keeps exiting immediately after script terminates.

**Root Cause**: Calling `subprocess.Popen()` and exiting leaves swaybg as a child process. When parent exits, swaybg gets killed.

**The Solution**: Use `systemd-run --user --scope` to start swaybg in an isolated systemd scope:

```python
compositor_cmd = [self.compositor, "-i", str(image_path), "-m", mode]
cmd = ["systemd-run", "--user", "--scope", "--"] + compositor_cmd
subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
```

This ensures swaybg survives after the Python script exits.

**Key Points**:
- `--scope`: Creates a transient systemd scope, not a full service
- Popen (not run): Don't wait for swaybg to complete (it runs forever)
- DEVNULL: Prevents pipe blocking issues
- **Start before kill**: New compositor starts first to prevent black flash

## Systemd Timer Configuration

**Timer File**: `systemd/chrono-wallpaper.timer`

Runs every minute during transition periods:
- Morning: 06:00-07:00 (night → day)
- Evening: 22:00-23:59 (day → night)

```ini
OnCalendar=*-*-* 06:*:00
OnCalendar=*-*-* 22:*:00
OnCalendar=*-*-* 23:*:00
AccuracySec=1s
```

**Important**: Don't use `OnBootSec` with calendar timers - it interferes with scheduling.

**Service Type**: `Type=oneshot` - service exits after each run, but swaybg persists via systemd scope.

## Troubleshooting

**Check if timer is running**:
```bash
systemctl --user status chrono-wallpaper.timer
systemctl --user list-timers chrono-wallpaper.timer
```

**Check service logs**:
```bash
journalctl --user -u chrono-wallpaper.service -f
```

**Check if swaybg is running**:
```bash
pgrep -a swaybg
```

**Manually test**:
```bash
chrono-wallpaper run
```

**Reload after config changes**:
```bash
systemctl --user daemon-reload
systemctl --user restart chrono-wallpaper.timer
```

## Common Issues

### Black Wallpaper

**Symptom**: Wallpaper is black, swaybg not running

**Cause**: swaybg exiting when parent process terminates

**Fix**: Ensure using `systemd-run --scope` in compositor.py (already implemented)

### Timer Not Triggering

**Symptom**: Timer shows NEXT trigger but service never runs

**Possible Causes**:
1. Service stuck in "active (exited)" state - stop it manually
2. `OnBootSec` interfering - remove it from timer file
3. Need to reload systemd after timer changes

### Wallpaper Not Updating

**Symptom**: Wallpaper doesn't change even though timer runs

**Cause**: Hash check detects no change (blend factor not changing enough)

**Solution**: Check blend factor with `chrono-wallpaper run`, verify current time is in transition period

### Black Flash During Updates

**Fixed in v1.0.1** - New compositor starts before old one is killed to prevent brief black screen.

## Project Structure

Key files:
- `src/chrono_wallpaper/core/compositor.py` - swaybg lifecycle (CRITICAL)
- `src/chrono_wallpaper/core/scheduler.py` - Time → blend factor
- `src/chrono_wallpaper/core/blender.py` - Image blending + hash check
- `src/chrono_wallpaper/cli/main.py` - CLI entry point
- `systemd/chrono-wallpaper.timer` - Calendar-based timer
- `systemd/chrono-wallpaper.service` - Oneshot service
- `systemd/install.sh` - Installation script

## Dependencies

**Runtime**:
- Python 3.10+
- Pillow (image processing)
- numpy (blending)
- psutil (process management)
- click (CLI)
- systemd (for systemd-run command)
- swaybg (Wayland wallpaper daemon)

**Dev**:
- pytest, pytest-cov, pytest-mock
- black, ruff

## Installation

```bash
cd ~/git/chrono-wallpaper
pip install -e . --break-system-packages
./systemd/install.sh
```

## Configuration

Currently hardcoded in `src/chrono_wallpaper/cli/main.py`:
- Day image: `~/Pictures/anime-girl.png`
- Night image: `~/Pictures/wallpaper-night.png`
- Output dir: `~/.cache/chrono-wallpaper`

## Transition Times

Defined in `src/chrono_wallpaper/core/scheduler.py`:

**Morning (06:00-07:00)**: Night → Day
- Factor: 1.0 → 0.0 (linear interpolation)

**Evening (22:00-00:00)**: Day → Night
- Factor: 0.0 → 1.0 (linear interpolation)

**Static Periods**:
- 07:00-22:00: Full day (factor 0.0)
- 00:00-06:00: Full night (factor 1.0)

## Blending Formula

```python
blended = day_arr * (1 - factor) + night_arr * factor
```

Where:
- `factor = 0.0`: 100% day image
- `factor = 0.5`: 50/50 blend
- `factor = 1.0`: 100% night image

## Testing

```bash
pytest tests/ -v
```

All 12 tests should pass:
- 6 blender tests (full day, full night, halfway, invalid factor, hash checks)
- 6 scheduler tests (day, night, morning/evening transitions)

## Hyprland Integration

Add to `~/.config/hypr/hyprland.conf`:

```bash
exec-once = chrono-wallpaper run
```

This sets the initial wallpaper on login. The systemd timer handles updates during transitions.

## Migration from Old System

Replaced `~/git/dotfiles/scripts/wallpaper-gradient.py` which had daemon lifecycle issues.

Old timer disabled:
```bash
systemctl --user stop wallpaper-switcher.timer
systemctl --user disable wallpaper-switcher.timer
```

## Future Improvements

Potential enhancements:
1. TOML config file support (instead of hardcoded paths)
2. CLI commands: `status`, `config`, `install`
3. Multiple wallpaper sets (different profiles)
4. Configurable transition times
5. Support for other compositors (swww, hyprpaper)

## Version History

**v1.0.1** (2025-12-29):
- Fixed black flash during wallpaper updates
- New compositor now starts before killing old one

**v1.0.0** (2025-12-29):
- Initial release
- Fixed critical swaybg daemon lifecycle issue
- Systemd timer integration
- Hash-based change detection
- Linear blending for smooth transitions
- 12 passing tests

## Notes

Created to replace broken wallpaper-gradient.py system that couldn't keep swaybg running.
The key innovation is using `systemd-run --scope` for proper daemon isolation.
