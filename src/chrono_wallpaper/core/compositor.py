"""Compositor management for reliable swaybg lifecycle control."""

import subprocess
import time
import logging
import os
from pathlib import Path
from typing import Optional
import psutil


logger = logging.getLogger(__name__)


class CompositorManager:
    """Manage wallpaper compositor lifecycle (swaybg, swww, etc.)."""

    def __init__(self, compositor: str = "swaybg", args: Optional[list[str]] = None):
        self.compositor = compositor
        self.args = args or []
        self.process: Optional[subprocess.Popen] = None

    def set_wallpaper(self, image_path: Path, mode: str = "fill") -> bool:
        """Set wallpaper and ensure compositor is running."""
        try:
            # Check if swww-daemon is running - if so, use swww instead
            if self._is_swww_running():
                return self._set_wallpaper_swww(image_path)

            # 1. Get existing PIDs
            old_pids = self._get_existing_pids()

            # 2. Start new compositor first (prevents black flash)
            compositor_cmd = [self.compositor, "-i", str(image_path), "-m", mode] + self.args
            cmd = ["systemd-run", "--user", "--scope", "--"] + compositor_cmd
            logger.info(f"Starting: {' '.join(compositor_cmd)}")

            # Use Popen instead of run() since swaybg runs forever
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 3. Wait for new compositor to start
            time.sleep(0.2)  # Brief pause to let new compositor initialize

            # 4. Kill only the old compositor instances
            self._kill_pids(old_pids)

            logger.info("Compositor started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to set wallpaper: {e}")
            return False

    def _get_existing_pids(self) -> set:
        """Get PIDs of existing compositor processes."""
        pids = set()
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] == self.compositor:
                    pids.add(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return pids

    def _kill_existing(self):
        """Kill existing compositor processes gracefully."""
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if proc.info['name'] == self.compositor:
                    logger.debug(f"Killing {self.compositor} (PID: {proc.pid})")
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def _kill_pids(self, pids: set):
        """Kill specific processes by PID."""
        for pid in pids:
            try:
                psutil.Process(pid).terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def _wait_for_termination(self, timeout: float = 2.0) -> bool:
        """Wait for compositor to terminate."""
        start = time.time()
        while time.time() - start < timeout:
            found = any(
                p.info['name'] == self.compositor
                for p in psutil.process_iter(['name'])
            )
            if not found:
                return True
            time.sleep(0.1)

        # Force kill if still running
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == self.compositor:
                proc.kill()  # SIGKILL

        return False

    def _wait_for_startup(self, timeout: float = 1.0) -> bool:
        """Wait for compositor to stabilize."""
        if not self.process:
            return False

        start = time.time()
        while time.time() - start < timeout:
            retcode = self.process.poll()
            if retcode is not None:
                return False

            try:
                proc = psutil.Process(self.process.pid)
                if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                    return True
            except psutil.NoSuchProcess:
                return False

            time.sleep(0.05)

        return self.process.poll() is None

    def _is_swww_running(self) -> bool:
        """Check if swww-daemon is running."""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] == 'swww-daemon':
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False

    def _set_wallpaper_swww(self, image_path: Path) -> bool:
        """Set wallpaper using swww (smooth transitions, no restart needed)."""
        try:
            cmd = ["swww", "img", str(image_path),
                   "--transition-type", "fade",
                   "--transition-duration", "0.5"]
            result = subprocess.run(cmd, capture_output=True, timeout=5)

            if result.returncode == 0:
                logger.info(f"Wallpaper set via swww: {image_path}")
                return True
            else:
                logger.error(f"swww failed: {result.stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"Failed to set wallpaper via swww: {e}")
            return False
