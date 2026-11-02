#!/usr/bin/env python3
"""Manual native hook recovery. Run in a separate OS terminal, not the blocked agent tab."""
import argparse
import hashlib
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKUPS = ROOT / "harness/recovery-backups"
CONFIGS = {
    "codex": ".codex/hooks.json",
    "claude": ".claude/settings.json",
    "antigravity": ".agents/hooks.json",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe(path):
    if not path.is_relative_to(ROOT):
        raise ValueError("path escapes project")
    for p in (path, *path.parents):
        if p == ROOT.parent:
            break
        if p.is_symlink():
            raise ValueError("symlink refused: " + str(p))
    return path


def confirm(action):
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise ValueError("manual OS terminal with interactive stdin/stdout required; pipelines and agent tools refused")
    challenge = "CONFIRM " + action.upper()
    print("WARNING: changes native hook registration; human-only operating procedure, not identity authentication.")
    print("Current agent session may retain cached hooks. Keep original SETUP tab open.")
    print("Type", challenge, "to proceed:")
    if input("> ") != challenge:
        raise ValueError("manual confirmation rejected")


def status(runtime):
    target = safe(ROOT / CONFIGS[runtime])
    print("Runtime:", runtime, "registration:", target.relative_to(ROOT))
    print("Native config:", "PRESENT" if target.is_file() else "ABSENT")
    if target.is_file():
        print("SHA256:", sha(target.read_bytes()))
    print("Backups directory:", BACKUPS)


def disable(runtime):
    target = safe(ROOT / CONFIGS[runtime])
    if not target.is_file():
        raise ValueError("native config missing; cannot create recovery backup")
    before = target.read_bytes()
    if runtime == "claude":
        data = json.loads(before.decode("utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("hooks"), dict):
            raise ValueError("no native hook group to disable")
        data.pop("hooks")
        after = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    else:
        after = None  # config is moved out of the native registration path
    confirm("DISABLE " + runtime)
    safe(BACKUPS)
    BACKUPS.mkdir(parents=True, exist_ok=True)
    name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + "-" + runtime
    location = safe(BACKUPS / name)
    location.mkdir(exist_ok=False)
    (location / "before.bin").write_bytes(before)
    meta = {"runtime": runtime, "native_path": CONFIGS[runtime],
            "before_sha256": sha(before), "after_sha256": sha(after) if after is not None else None}
    (location / "manifest.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    if target.read_bytes() != before:
        raise ValueError("config changed during backup; existing backup kept, native config untouched")
    if after is None:
        target.unlink()
    else:
        with target.open("wb") as out:
            out.write(after)
    print("RECOVERY_BACKUP:", location.relative_to(ROOT))
    print("NATIVE_HOOKS_DISABLED: restart the affected host session; do not claim approved policy change")
    print("To restore: python harness/common/recover.py --runtime", runtime, "restore --backup", name)


def restore(runtime, backup):
    if not re.fullmatch(r"[0-9]{8}T[0-9]{12}-(?:codex|claude|antigravity)", backup):
        raise ValueError("invalid backup ID")
    location = safe(BACKUPS / backup)
    metadata = json.loads(safe(location / "manifest.json").read_text(encoding="utf-8"))
    if metadata.get("runtime") != runtime or metadata.get("native_path") != CONFIGS[runtime]:
        raise ValueError("backup runtime mismatch")
    original = safe(location / "before.bin").read_bytes()
    if sha(original) != metadata.get("before_sha256"):
        raise ValueError("backup hash mismatch")
    target = safe(ROOT / CONFIGS[runtime])
    after_sha = metadata.get("after_sha256")
    if after_sha is None:
        if target.exists():
            raise ValueError("native config was recreated: manual merge required, no overwrite")
    else:
        if not target.is_file() or sha(target.read_bytes()) != after_sha:
            raise ValueError("native config changed after recovery: manual merge required")
    confirm("RESTORE " + runtime)
    target.parent.mkdir(parents=True, exist_ok=True)
    if after_sha is None:
        with target.open("xb") as out:
            out.write(original)
    else:
        if sha(target.read_bytes()) != after_sha:
            raise ValueError("native config changed during restore")
        target.write_bytes(original)
    print("RESTORED:", CONFIGS[runtime], "restart the host and redo native smoke tests")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runtime", choices=sorted(CONFIGS), required=True)
    sub = p.add_subparsers(dest="action", required=True)
    sub.add_parser("inspect")
    sub.add_parser("disable")
    a = sub.add_parser("restore")
    a.add_argument("--backup", required=True)
    args = p.parse_args(argv)
    try:
        if args.action == "inspect":
            status(args.runtime)
        elif args.action == "disable":
            disable(args.runtime)
        else:
            restore(args.runtime, args.backup)
        return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print("BLOCK:", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
