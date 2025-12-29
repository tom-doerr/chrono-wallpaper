#!/bin/bash
# Install chrono-wallpaper systemd timer and service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "Installing chrono-wallpaper systemd units..."

# Create systemd user directory if it doesn't exist
mkdir -p "$SYSTEMD_USER_DIR"

# Create symlinks
ln -sf "$SCRIPT_DIR/chrono-wallpaper.service" "$SYSTEMD_USER_DIR/chrono-wallpaper.service"
ln -sf "$SCRIPT_DIR/chrono-wallpaper.timer" "$SYSTEMD_USER_DIR/chrono-wallpaper.timer"

echo "Reloading systemd daemon..."
systemctl --user daemon-reload

echo "Enabling and starting timer..."
systemctl --user enable chrono-wallpaper.timer
systemctl --user start chrono-wallpaper.timer

echo ""
echo "Installation complete!"
echo "Check status: systemctl --user status chrono-wallpaper.timer"
echo "View logs: journalctl --user -u chrono-wallpaper -f"
