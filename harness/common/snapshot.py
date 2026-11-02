#!/usr/bin/env python3
"""Hash-checked, explicitly scoped snapshots. No destructive Git operations."""
import argparse
import hashlib
import json
import pathlib
import secrets
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
STORE = ROOT / "harness" / "snapshots"
MAX_BYTES = 8 * 1024 * 1024
FORBIDDEN = {".git", ".env", ".bootstrap-state", "snapshots", "__pycache__"}

def safe_store():
    # The generated snapshot directory must never redirect writes/reads outside
    # the installed project. Check the complete path before creating it.
    for loc in (ROOT / "harness", STORE):
        if loc.is_symlink() or (loc.exists() and not loc.resolve().is_relative_to(ROOT)):
            raise ValueError("unsafe snapshot store symlink or external path")
    return STORE

def digest(data):
    return hashlib.sha256(data).hexdigest()

def source_file(name):
    relative = pathlib.Path(name)
    if relative.is_absolute() or not relative.parts or any(
            part in ("", ".", "..") or part in FORBIDDEN or
            part.startswith(".env.") for part in relative.parts):
        raise ValueError("invalid or forbidden snapshot path")
    candidate = ROOT / relative
    for parent in [candidate, *candidate.parents]:
        if parent == ROOT.parent:
            break
        if parent.is_symlink():
            raise ValueError("symlink paths are not supported")
    if not candidate.is_file() or not candidate.resolve().is_relative_to(ROOT):
        raise ValueError("snapshot target must be a regular project file")
    if candidate.stat().st_size > MAX_BYTES:
        raise ValueError("snapshot target exceeds 8 MiB")
    return candidate, relative.as_posix()

def capture(names):
    if not names:
        raise ValueError("explicit file paths required")
    values = []
    for name in names:
        path, relative = source_file(name)
        data = path.read_bytes()
        values.append((relative, data))
    ident = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + secrets.token_hex(5)
    target = safe_store() / ident
    target.mkdir(parents=True, exist_ok=False)
    records = []
    for idx, (name, data) in enumerate(values):
        fname = "%04d.bin" % idx
        (target / fname).write_bytes(data)
        records.append({"path": name, "blob": fname, "sha256": digest(data)})
    (target / "manifest.json").write_text(json.dumps({"files": records}, indent=2) + "\n", encoding="utf-8")
    return ident

def inspect(ident, expected=None):
    if not ident or not all(ch.isalnum() or ch == "-" for ch in ident):
        raise ValueError("invalid snapshot ID")
    location = safe_store() / ident
    if location.is_symlink():
        raise ValueError("snapshot symlink rejected")
    manifest_path = location / "manifest.json"
    if manifest_path.is_symlink():
        raise ValueError("snapshot manifest symlink rejected")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("invalid snapshot manifest")
    changes = []
    for entry in files:
        path, relative = source_file(entry["path"])
        blob = entry["blob"]
        if not isinstance(blob, str) or not blob.endswith(".bin") or not blob[:-4].isdigit():
            raise ValueError("invalid blob name")
        payload = location / blob
        if payload.is_symlink():
            raise ValueError("snapshot blob symlink rejected")
        data = payload.read_bytes()
        if digest(data) != entry["sha256"]:
            raise ValueError("snapshot hash mismatch")
        current_sha = digest(path.read_bytes())
        if expected is not None and current_sha != expected.get(relative):
            raise ValueError("current hash not explicitly acknowledged: " + relative)
        changes.append((path, relative, data, current_sha))
    return changes

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("capture").add_argument("paths", nargs="+")
    restore = sub.add_parser("restore")
    restore.add_argument("snapshot_id")
    restore.add_argument("--apply", action="store_true")
    restore.add_argument("--expect-current", action="append", default=[], metavar="PATH=SHA256")
    args = parser.parse_args(argv)
    try:
        if args.action == "capture":
            print("SNAPSHOT:", capture(args.paths))
            return 0
        expected = {}
        for item in args.expect_current:
            name, sep, sha = item.rpartition("=")
            if not sep or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
                raise ValueError("expected PATH=SHA256")
            expected[name] = sha
        changes = inspect(args.snapshot_id, expected if args.apply else None)
        for _, name, _, sha in changes:
            print("RESTORE_PREVIEW:", name, "current_sha256=" + sha)
        if not args.apply:
            return 0
        # All current paths/hashes validated before any write. Restore never deletes files.
        for path, _, data, _ in changes:
            with path.open("wb") as dst:
                dst.write(data)
        print("RESTORED:", len(changes), "files")
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("BLOCKED:", exc, file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
