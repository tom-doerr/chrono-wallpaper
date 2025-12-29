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
            # 1. Kill existing compositor
            self._kill_existing()

            # 2. Wait for termination
            if not self._wait_for_termination(timeout=2.0):
                logger.warning("Compositor did not terminate cleanly")

            # 3. Start new compositor using systemd-run for proper isolation
            compositor_cmd = [self.compositor, "-i", str(image_path), "-m", mode] + self.args
            cmd = ["systemd-run", "--user", "--scope", "--"] + compositor_cmd
            logger.info(f"Starting: {' '.join(compositor_cmd)}")

            # Use Popen instead of run() since swaybg runs forever
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 4. Wait for compositor to appear
            if not self._wait_for_startup(timeout=1.0):
                raise RuntimeError("Compositor failed to start")

            logger.info("Compositor started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to set wallpaper: {e}")
            return False

    def _kill_existing(self):
        """Kill existing compositor processes gracefully."""
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if proc.info['name'] == self.compositor:
                    logger.debug(f"Killing {self.compositor} (PID: {proc.pid})")
                    proc.terminate()
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
