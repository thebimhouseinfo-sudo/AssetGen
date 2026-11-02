#!/usr/bin/env python3
"""Antigravity Stop command: skip blocking verify during explicit staged setup only."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness/common"))
from setup_lifecycle import stage_active

if __name__ == "__main__":
    if stage_active():
        print("BOOTSTRAPPING: Stop verify deferred until final lock; no PASS claimed")
        sys.exit(0)
    sys.exit(subprocess.call([sys.executable, str(ROOT / "harness/common/verify.py")],
                             cwd=str(ROOT)))
