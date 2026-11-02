#!/usr/bin/env python3
"""Tier-aware file and skill inventory, NOT a hook/approval/gate security doctor."""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "harness/specs/TIER_MANIFEST.json"

def role_names(manifest, tier):
    names, visited = set(), set()
    while tier:
        if tier in visited or tier not in manifest["tiers"]:
            raise ValueError("invalid tier/inheritance")
        visited.add(tier)
        entry = manifest["tiers"][tier]
        names.update(entry["agents"])
        tier = entry.get("inherits")
    return names

def check_skill(path):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    sections = text.split("---", 2)
    if len(sections) < 3 or sections[0].strip():
        return False
    props = sections[1].splitlines()
    return any(s.startswith("name: ") and s[6:].strip() for s in props) and any(
        s.startswith("description: ") and s[13:].strip() for s in props)

def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", choices=["Lite", "Standard", "Full"], default="Standard")
    parser.add_argument("--runtime", choices=["antigravity", "codex", "claude", "continue", "generic"], required=True)
    options = parser.parse_args(args)
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        roles = role_names(manifest, options.tier)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("NOT_CONFIGURED: tier manifest:", exc)
        return 2
    needed = [
        "AGENTS.md", "docs/CRITERIA.md", "docs/PROJECT_PROFILE.md", "TASKS.md",
        "harness/common/verify.py", "harness/common/checks.json",
        "harness/common/branch_authority.py", "harness/config/branch-authority.example.json",
    ]
    needed += [".agents/roles/" + role + ".md" for role in sorted(roles)]
    if options.runtime == "antigravity":
        needed.extend([".agents/hooks.json", ".agents/MODEL_SELECTION.md", ".antigravity/README.md"])
        needed += [".antigravity/agents/" + role + ".md" for role in sorted(roles)]
    elif options.runtime == "codex":
        needed.extend([".codex/hooks.json", "harness/codex/hook.py",
                       "harness/common/snapshot.py", "harness/common/task.py",
                       "harness/hook-policy.json", "harness/active-task.json"])
        needed += [".codex/agents/" + role + ".toml" for role in sorted(roles)]
    if options.runtime == "generic":
        needed += [".generic/README.md", ".generic/PORTING.md",
                   ".generic/platforms/cline.md", ".generic/platforms/qwen-code.md",
                   ".generic/platforms/deepseek.md"]
        needed += [".generic/agents/" + role + ".md" for role in sorted(roles)]
    if options.runtime == "continue":
        needed += [".continue/config.yaml", ".continue/rules/00-bootstrap.md",
                   ".continue/README.md"]
    needed += [".claude/agents/" + role + ".md" for role in sorted(roles)] if options.runtime == "claude" else []
    needed += [".continue/agents/" + role + "/config.yaml" for role in sorted(roles)] if options.runtime == "continue" else []
    if options.runtime == "claude":
        needed.append("CLAUDE.md")
    missing = [rel for rel in needed if not (ROOT / rel).is_file()]
    for rel in missing:
        print("MISSING:", rel)
    folders = [ROOT / ".agents/skills"]
    if options.runtime == "claude":
        folders.append(ROOT / ".claude/skills")
    malformed = [str(p.relative_to(ROOT)) for folder in folders for p in folder.glob("*/SKILL.md") if not check_skill(p)]
    for item in malformed:
        print("INVALID_SKILL:", item)
    if missing or malformed:
        return 1
    print("PASS: tier/runtime file inventory only; hooks, approvals and gates NOT_VERIFIED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
