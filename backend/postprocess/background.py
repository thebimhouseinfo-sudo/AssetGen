import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

WORKER_PATH = Path(__file__).resolve().parent / "bg_worker.py"
DEFAULT_MODEL = "ZhengPeng7/BiRefNet"
DEFAULT_TIMEOUT = 600


class BackgroundRemovalError(RuntimeError):
    pass


class BackgroundRemover:
    """Removes image background by running bg_worker.py in an external interpreter."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, timeout: int = DEFAULT_TIMEOUT):
        self.config = dict(config or {})
        self.timeout = int(self.config.get("timeout", timeout))

    def remove(self, image: Image.Image) -> Image.Image:
        python = self.config.get("python")
        if not python:
            raise BackgroundRemovalError(
                "Background removal is not configured: set settings['background_removal']['python'] "
                "to an interpreter that has torch and transformers installed"
            )
        if not Path(python).exists():
            raise BackgroundRemovalError(f"Background removal interpreter not found: {python}")

        command = [python, str(WORKER_PATH), "--model", self.config.get("model") or DEFAULT_MODEL]
        if self.config.get("device"):
            command += ["--device", self.config["device"]]

        with tempfile.TemporaryDirectory(prefix="assetgen_bg_") as directory:
            source = os.path.join(directory, "input.png")
            target = os.path.join(directory, "output.png")
            image.convert("RGB").save(source, format="PNG")
            try:
                result = subprocess.run(
                    command + ["--input", source, "--output", target],
                    capture_output=True, text=True, timeout=self.timeout,
                )
            except subprocess.TimeoutExpired as exc:
                raise BackgroundRemovalError(f"Background removal timed out after {self.timeout}s") from exc
            except OSError as exc:
                raise BackgroundRemovalError(f"Could not start background removal worker: {exc}") from exc
            if result.returncode != 0:
                detail = (result.stderr or result.stdout or "").strip()[-1000:]
                raise BackgroundRemovalError(f"Background removal worker failed (exit {result.returncode}): {detail}")
            if not os.path.exists(target):
                raise BackgroundRemovalError("Background removal worker produced no output")
            with Image.open(target) as out:
                return out.convert("RGBA")
