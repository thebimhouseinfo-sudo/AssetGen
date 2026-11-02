#!/usr/bin/env python3
"""Branch authority for one Git clone. Read the Git common dir; never infer main."""
import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")

class Blocked(ValueError):
    pass

def git(*args, check=True):
    result = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                            text=True, encoding="utf-8", errors="replace", check=False)
    if check and result.returncode:
        raise Blocked("Git unavailable or ref missing (" + " ".join(args[:2]) + ")")
    return result

def repo_root():
    result = git("rev-parse", "--show-toplevel", check=False)
    if result.returncode:
        return None
    resolved = pathlib.Path(result.stdout.strip()).resolve()
    if resolved != ROOT.resolve():
        raise Blocked("Git root differs from installed harness project")
    return resolved

def authority_path():
    if repo_root() is None:
        raise Blocked("not a Git project")
    result = git("rev-parse", "--git-common-dir")
    common = pathlib.Path(result.stdout.strip())
    if not common.is_absolute():
        common = ROOT / common
    return common.resolve() / "bootstrap" / "branch-authority.json"

def name(value):
    if not isinstance(value, str) or not NAME.fullmatch(value) or value in ("HEAD", "."):
        raise Blocked("invalid explicit Git branch")
    if git("check-ref-format", "--branch", value, check=False).returncode:
        raise Blocked("invalid Git ref: " + value)
    return value

def exists(value):
    return git("show-ref", "--verify", "--quiet", "refs/heads/" + value, check=False).returncode == 0

def current():
    result = git("symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    if result.returncode or not result.stdout.strip():
        raise Blocked("detached or unknown HEAD; select the approved branch explicitly")
    return name(result.stdout.strip())

def validate(data):
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise Blocked("invalid branch authority schema")
    active = name(data.get("active_development_branch"))
    frozen = data.get("frozen_branches")
    work = data.get("work_branches")
    remote = data.get("remote")
    if not isinstance(frozen, list) or not isinstance(work, dict):
        raise Blocked("invalid frozen_branches/work_branches")
    if not all(isinstance(x, str) for x in frozen) or len(set(frozen)) != len(frozen):
        raise Blocked("invalid frozen branch list")
    for x in frozen:
        name(x)
    if active in frozen or not exists(active):
        raise Blocked("active development branch missing or frozen")
    for branch, base in work.items():
        name(branch)
        if branch == active or branch in frozen or base != active:
            raise Blocked("work branch requires explicit active base: " + branch)
    if remote is not None:
        if not isinstance(remote, str) or not remote or remote not in git("remote").stdout.splitlines():
            raise Blocked("configured remote not present in this clone")
    return data

def load():
    path = authority_path()
    if path.is_symlink() or (path.parent.exists() and path.parent.is_symlink()):
        raise Blocked("symlinked branch authority path rejected")
    if not path.is_file():
        raise Blocked("NOT_CONFIGURED: human must select active development branch")
    try:
        return validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise Blocked("invalid branch authority file: " + str(exc)) from exc

def check_write(data=None):
    data = load() if data is None else data
    branch = current()
    if branch in data["frozen_branches"]:
        raise Blocked("branch is frozen: " + branch)
    if branch != data["active_development_branch"] and data["work_branches"].get(branch) != data["active_development_branch"]:
        raise Blocked("checkout is not the active or registered work branch: " + branch)
    if not exists(branch):
        raise Blocked("current branch has no local ref")
    return branch

def status():
    config = load()
    actual = current()
    print("ACTIVE_DEV:", config["active_development_branch"])
    print("CURRENT:", actual)
    print("FROZEN:", ",".join(config["frozen_branches"]) or "(none)")
    print("WORK_BRANCHES:", ",".join(sorted(config["work_branches"])) or "(none)")
    print("MERGE_TARGET:", config["active_development_branch"])
    check_write(config)
    print("PASS: approved checkout (not a host-enforced Git write guard)")

def configure(args):
    active = name(args.active)
    frozen = [name(x) for x in args.freeze]
    work = {name(x): active for x in args.work}
    config = validate({"schema_version": 1, "active_development_branch": active,
                       "frozen_branches": frozen, "work_branches": work,
                       "remote": args.remote})
    path = authority_path()
    rendered = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    if path.exists() and (path.is_symlink() or path.read_text(encoding="utf-8") != rendered) and not args.replace:
        raise Blocked("existing authority differs; require explicit --replace after human decision")
    print("AUTHORITY_PATH:", path)
    print(rendered.strip())
    if not args.apply:
        print("PREVIEW_ONLY: add --apply after human chooses the exact branch/freeze set")
        return
    if path.parent.is_symlink():
        raise Blocked("authority directory is a symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise Blocked("authority file is a symlink")
    # Single local writer; human confirmation is governed by host permissions, not this flag.
    temp = path.with_suffix(".new")
    if temp.exists() or temp.is_symlink():
        raise Blocked("pending authority temp file exists")
    try:
        temp.write_text(rendered, encoding="utf-8")
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()
    print("CONFIGURED: local Git common-dir authority (not authenticated human approval)")

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("status")
    sub.add_parser("check-write")
    create = sub.add_parser("check-create")
    create.add_argument("--base", required=True)
    create.add_argument("--new", required=True)
    merge = sub.add_parser("check-merge")
    merge.add_argument("--source", required=True)
    merge.add_argument("--target", required=True)
    push = sub.add_parser("check-push")
    push.add_argument("--source", required=True)
    push.add_argument("--target", required=True)
    push.add_argument("--remote", required=True)
    cfg = sub.add_parser("configure")
    cfg.add_argument("--active", required=True)
    cfg.add_argument("--freeze", action="append", default=[])
    cfg.add_argument("--work", action="append", default=[])
    cfg.add_argument("--remote")
    cfg.add_argument("--apply", action="store_true")
    cfg.add_argument("--replace", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "configure":
            configure(args)
            return 0
        if args.action == "status":
            status()
            return 0
        data = load()
        if args.action == "check-write":
            print("PASS: write target:", check_write(data))
        elif args.action == "check-create":
            new = name(args.new)
            if current() != data["active_development_branch"] or args.base != data["active_development_branch"]:
                raise Blocked("new work branch must start from checked-out active development branch")
            if data["work_branches"].get(new) != data["active_development_branch"] or exists(new):
                raise Blocked("work branch not registered or already exists")
            print("PASS: create registered work branch", new, "from", args.base)
        elif args.action == "check-merge":
            source, target = name(args.source), name(args.target)
            check_write(data)
            if target != data["active_development_branch"] or target in data["frozen_branches"]:
                raise Blocked("merge target must be the unfrozen active development branch")
            if data["work_branches"].get(source) != target or not exists(source):
                raise Blocked("merge source must be a registered existing work branch based on active")
            print("PASS: merge", source, "into", target)
        elif args.action == "check-push":
            source, target = name(args.source), name(args.target)
            actual = check_write(data)
            if args.remote != data["remote"] or data["remote"] is None:
                raise Blocked("push remote has not been explicitly authorized")
            if source != actual or target != source or target in data["frozen_branches"]:
                raise Blocked("push must publish current approved branch to same-named unfrozen ref")
            print("PASS: push", source, "to", args.remote + "/" + target)
        return 0
    except (Blocked, OSError) as exc:
        print("BLOCKED:", exc, file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
