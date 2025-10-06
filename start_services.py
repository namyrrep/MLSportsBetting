"""Utility script to launch the FastAPI backend and Vite frontend together."""
from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import List

# Absolute paths for the workspace
PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_SCRIPT = PROJECT_ROOT / "src" / "api_server.py"

# Commands for each service
BACKEND_CMD = [sys.executable, str(BACKEND_SCRIPT)]
if os.name == "nt":  # Resolve npm executable on Windows (npm.cmd)
    _npm = shutil.which("npm.cmd") or shutil.which("npm")
else:
    _npm = shutil.which("npm")

FRONTEND_CMD = [_npm, "run", "dev"] if _npm else []


class ManagedProcess:
    """Small helper to track spawned subprocesses and shut them down cleanly."""

    def __init__(self, name: str, cmd: List[str], cwd: Path | None = None):
        self.name = name
        self.cmd = cmd
        self.cwd = cwd
        self.process: subprocess.Popen | None = None

    def start(self) -> None:
        creationflags = 0
        if os.name == "nt":  # Windows needs NEW_PROCESS_GROUP for CTRL_BREAK
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        print(f"▶️  Starting {self.name}: {' '.join(self.cmd)}")
        self.process = subprocess.Popen(
            self.cmd,
            cwd=self.cwd,
            creationflags=creationflags,
        )

    def stop(self) -> None:
        if not self.process or self.process.poll() is not None:
            return

        print(f"⏹️  Stopping {self.name}...")
        try:
            if os.name == "nt":
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
                # Give the process a moment to exit gracefully
                time.sleep(1.0)
            self.process.terminate()
            self.process.wait(timeout=10)
        except Exception:
            self.process.kill()
        finally:
            self.process = None

    def has_exited(self) -> bool:
        return self.process is not None and self.process.poll() is not None

    def returncode(self) -> int | None:
        return None if not self.process else self.process.returncode


def main() -> None:
    backend = ManagedProcess("FastAPI backend", BACKEND_CMD, cwd=PROJECT_ROOT)
    frontend = ManagedProcess("React frontend", FRONTEND_CMD, cwd=FRONTEND_DIR)
    processes = [backend, frontend]

    # Launch services
    backend.start()
    # Give backend a head start so it can bind to port 8000 before the UI requests data
    time.sleep(2)
    frontend.start()

    print("🚀 Both services are running. Press Ctrl+C to stop them.")

    try:
        while True:
            time.sleep(1)
            for proc in processes:
                if proc.has_exited():
                    code = proc.returncode()
                    print(f"⚠️  {proc.name} exited with code {code}.")
                    raise SystemExit(code if code is not None else 0)
    except KeyboardInterrupt:
        print("\n🛑 Received stop signal. Shutting down services...")
    finally:
        for proc in processes:
            proc.stop()


if __name__ == "__main__":
    # Basic environment checks
    if not BACKEND_SCRIPT.exists():
        sys.exit("Backend script not found at src/api_server.py")
    if not FRONTEND_DIR.exists():
        sys.exit("Frontend directory not found at ./frontend")
    if not FRONTEND_CMD:
        sys.exit("Unable to locate 'npm'. Please install Node.js and ensure npm is on your PATH.")

    main()
