#!/usr/bin/env python3
"""Safe verified-command runner. Python >=3.9. Exit 0 pass, 1 failed, 2 not configured."""
import json
import math
import os
import pathlib
import signal
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFIG = pathlib.Path(__file__).with_name("checks.json")

def load_checks(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("cannot read valid JSON: " + str(exc)) from exc
    if not isinstance(data, dict):
        raise ValueError("root must be an object")
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("checks must be a non-empty array of verified commands")
    names = set()
    for i, check in enumerate(checks):
        if not isinstance(check, dict):
            raise ValueError("check %d must be an object" % i)
        name = check.get("name")
        argv = check.get("argv")
        timeout = check.get("timeout_seconds", 120)
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("each check needs a unique nonempty name")
        names.add(name)
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x.strip() for x in argv):
            raise ValueError("argv must be nonempty list of command/argument strings")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0 or timeout > 3600:
            raise ValueError("timeout_seconds must be finite number in (0, 3600]")
    return checks

def stop_tree(proc):
    """Kill owned process group on POSIX; use taskkill tree on Windows. Best effort."""
    if proc.poll() is not None:
        return
    if os.name == "nt":
        try:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, check=False)
        except (OSError, subprocess.TimeoutExpired):
            proc.kill()
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except (OSError, PermissionError):
            proc.kill()
    try:
        proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()

def execute(check):
    kwargs = {"cwd": str(ROOT), "shell": False, "stdin": subprocess.DEVNULL}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(check["argv"], **kwargs)
    try:
        return proc.wait(timeout=check.get("timeout_seconds", 120))
    except subprocess.TimeoutExpired:
        stop_tree(proc)
        raise

def main(config=CONFIG):
    try:
        checks = load_checks(pathlib.Path(config))
    except ValueError as exc:
        print("NOT_CONFIGURED:", exc)
        return 2
    for check in checks:
        print("RUN:", check["name"], flush=True)
        try:
            result = execute(check)
        except subprocess.TimeoutExpired:
            print("TIMEOUT:", check["name"], "(owned process tree termination attempted)")
            return 1
        except OSError as exc:
            print("FAIL:", check["name"], "cannot launch:", exc)
            return 1
        if result != 0:
            print("FAIL:", check["name"], "exit", result)
            return 1
        print("PASS:", check["name"])
    print("PASS: configured checks only; independent real-host tests are separate")
    return 0

if __name__ == "__main__":
    sys.exit(main())
