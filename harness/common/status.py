#!/usr/bin/env python3
"""Print honest tier/runtime release capability status. Exit 2 until mandatory runtime features exist."""
import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPABILITY_FILE = HERE / "capabilities.json"
TIER_FILE = ROOT / "harness/specs/TIER_MANIFEST.json"
SATISFIED = {"SCRIPT_TESTED", "RUNTIME_VERIFIED", "ENFORCED"}

def inherited_requirements(manifest, tier):
    required = []
    visited = set()
    while tier:
        if tier in visited:
            raise ValueError("cyclic tier inheritance")
        visited.add(tier)
        entry = manifest["tiers"][tier]
        required.extend(entry.get("requires", []))
        tier = entry.get("inherits")
    return list(dict.fromkeys(required))

def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", choices=["Lite", "Standard", "Full"], default="Standard")
    parser.add_argument("--runtime", choices=["antigravity", "codex", "claude", "continue", "generic"], required=True)
    options = parser.parse_args(args)
    try:
        caps = json.loads(CAPABILITY_FILE.read_text(encoding="utf-8"))
        manifest = json.loads(TIER_FILE.read_text(encoding="utf-8"))
        reqs = inherited_requirements(manifest, options.tier)
        states = caps["capabilities"]
        if any(item not in states for item in reqs):
            raise ValueError("tier requires unknown capability")
        runtime = caps["runtime_smoke"][options.runtime]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("NOT_CONFIGURED: invalid release/manifest data:", exc)
        return 2
    print("RELEASE:", caps["release_kind"])
    print("TIER:", options.tier, "RUNTIME:", options.runtime)
    print("REAL_HOST_SMOKE:", runtime)
    missing = []
    for name in reqs:
        state = states[name]
        print("REQUIRED:", name, state)
        if state not in SATISFIED:
            missing.append(name)
    unresolved = [k for k, state in states.items() if state in ("NOT_CONFIGURED", "GUIDED_ONLY")]
    print("REMAINING_CAPABILITIES:", ", ".join(sorted(unresolved)))
    if missing or runtime != "RUNTIME_VERIFIED":
        print("NOT_CONFIGURED: not a fully operational automated harness")
        return 2
    print("PASS: supported capability inventory (not proof of enforcement)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
