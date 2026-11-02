import subprocess
import os
import time
from typing import Optional, Dict, Any, Tuple
from ..projects.models import TextAssetJob

class ModelAdapter:
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.sd_cli = settings["model"]["runtime_path"]
        self.model_path = settings["model"]["diffusion_model"]
        self.llm_path = settings["model"]["llm_encoder"]
        self.vae_path = settings["model"]["vae"]
        self.vae_format = settings["model"]["vae_format"]
        self.steps = int(settings["model"].get("steps", 4))
        self.cfg_scale = float(settings["model"].get("cfg_scale", 1.0))

    def generate_text_asset(self, job: TextAssetJob, output_path: str) -> Dict[str, Any]:
        width, height = self._resolve_dimensions(job.ratio)

        # Assemble prompt: style_prompt + prompt
        full_prompt = job.prompt
        if job.style_prompt:
            full_prompt = f"{job.style_prompt}, {job.prompt}"

        cmd = [
            self.sd_cli,
            "--diffusion-model", self.model_path,
            "--llm", self.llm_path,
            "--vae", self.vae_path,
            "--vae-format", self.vae_format,
            "--steps", str(self.steps),
            "--cfg-scale", str(self.cfg_scale),
            "-p", full_prompt,
            "-W", str(width),
            "-H", str(height),
            "-s", str(job.seed),
            "-o", output_path
        ]

        return self._run_inference(cmd, job.seed, width, height, output_path)

    def _run_inference(self, cmd: list, seed: int, width: int, height: int, output_path: str) -> Dict[str, Any]:
        start_time = time.time()
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            duration = time.time() - start_time

            if process.returncode != 0:
                raise RuntimeError(f"Generation failed: {process.stderr}")

            return {
                "path": output_path,
                "duration": duration,
                "seed": seed,
                "width": width,
                "height": height
            }
        except subprocess.TimeoutExpired:
            raise RuntimeError("Generation timed out after 10 minutes")

    def _resolve_dimensions(self, ratio_str: Optional[str]) -> Tuple[int, int]:
        if not ratio_str:
            return 512, 512

        try:
            w, h = map(int, ratio_str.split(':'))
            scale = 512 / (max(w, h))
            return max(64, round(w * scale / 16) * 16), max(64, round(h * scale / 16) * 16)
        except:
            return 512, 512
