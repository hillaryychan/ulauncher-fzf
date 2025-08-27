from __future__ import annotations

import shutil
import subprocess


def get_executable(cmd: str) -> str | None:
    """Get the executable of the provided command, otherwise return None."""
    try:
        return shutil.which(cmd)
    except subprocess.CalledProcessError:
        return None
