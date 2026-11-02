#!/usr/bin/env python3
"""Staged Bootstrap setup coordinator. Local human coordination, NOT an authenticated gate."""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
STATE = ROOT / "harness/setup-state.json"
REQUIRED = ("AGENTS.md", "docs/CRITERIA.md", "docs/ARCHITECTURE.md",
            "docs/PROJECT_PROFILE.md", "harness/common/checks.json")


def read_state():
    if not STATE.exists():
        return None  # legacy installs are deliberately not reinterpreted
    try:
        value = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"schema_version": 1, "phase": "BOOTSTRAPPING", "invalid": True}
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        return {"schema_version": 1, "phase": "BOOTSTRAPPING", "invalid": True}
    return value


def stage_active():
    """Only an intact, explicitly staged first install may defer hook guards."""
    state = read_state()
    return (isinstance(state, dict) and not state.get("invalid")
            and state.get("schema_version") == 1
            and state.get("phase") == "BOOTSTRAPPING"
            and state.get("runtime") in ("codex", "claude", "antigravity", "continue", "generic"))


def run(args, cwd=ROOT, data=None):
    try:
        return subprocess.run(args, cwd=str(cwd), input=data, text=True, capture_output=True,
                              encoding="utf-8", errors="replace", timeout=45, check=False)
    except (OSError, subprocess.TimeoutExpired) as err:
        return subprocess.CompletedProcess(args, 127, "", str(err))


def setup_intake_recorded():
    """Validate trace format, not host authentication or genuine user identity."""
    path = ROOT / "harness/setup-intake.json"
    if not path.is_file() or path.is_symlink():
        return False
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        state = read_state()
        if not isinstance(obj, dict) or obj.get("schema_version") != 1:
            return False
        channel = obj.get("channel")
        if (channel not in ("native_dialog", "cli_menu")
                or not isinstance(obj.get("runtime"), str)
                or (state and obj.get("runtime") != state.get("runtime"))
                or not isinstance(obj.get("responses"), list) or not obj["responses"]):
            return False
        ids = set()
        for entry in obj["responses"]:
            if (not isinstance(entry, dict)
                    or not isinstance(entry.get("id"), str) or not entry["id"].strip()
                    or entry["id"] in ids
                    or not isinstance(entry.get("value"), str) or not entry["value"].strip()
                    or entry.get("source") != channel):
                return False
            ids.add(entry["id"])
        recorded = {item["id"]: item["value"] for item in obj["responses"]}
        manifest_path = ROOT / "harness/.bootstrap-manifest.json"
        if not manifest_path.is_file() or manifest_path.is_symlink():
            return False
        installed = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(installed, dict) or installed.get("schema_version") != 1:
            return False
        return (recorded.get("tier") in ("Lite", "Standard", "Full")
                and recorded.get("tier") == installed.get("tier")
                and recorded.get("git_mode") in ("local", "tracked")
                and recorded.get("git_mode") == installed.get("config_git")
                and (not state or recorded["tier"] == state.get("tier")))
    except (OSError, ValueError, AttributeError):
        return False


def configured_checks():
    try:
        obj = json.loads((ROOT / "harness/common/checks.json").read_text(encoding="utf-8"))
        checks = obj.get("checks") if isinstance(obj, dict) else None
        return isinstance(checks, list) and bool(checks) and all(
            isinstance(c, dict) and isinstance(c.get("argv"), list) and
            bool(c["argv"]) and all(isinstance(a, str) and a for a in c["argv"])
            for c in checks)
    except (OSError, ValueError):
        return False


def audit():
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    for item in missing:
        print("BLOCK: missing required setup file:", item)
    problems = list(missing)
    state = read_state()
    if state is not None and (state.get("invalid")
            or state.get("phase") not in ("BOOTSTRAPPING", "READY",
                                          "READY_WITH_LIMITATIONS", "HANDOFF_COMPLETE")
            or state.get("runtime") not in ("codex", "claude", "antigravity", "continue", "generic")):
        print("BLOCK: setup-state.json malformed or phase/runtime invalid; guard is NOT deferred")
        problems.append("invalid setup state")
    if read_state() is not None:
        if not setup_intake_recorded():
            print("BLOCK: IDE-dialog/CLI-menu setup-intake trace missing/invalid; permission is not an answer")
            problems.append("interactive setup intake trace")
        else:
            print("SETUP_INTAKE: RECORDED (IDE dialog or CLI menu; local trace only, no host authentication)")
    if "docs/CRITERIA.md" not in missing:
        criteria = (ROOT / "docs/CRITERIA.md").read_text(encoding="utf-8")
        if not any(x.strip().upper() == "STATUS: APPROVED" for x in criteria.splitlines()):
            print("NOT_CONFIGURED: CRITERIA is not explicitly APPROVED")
            problems.append("CRITERIA approval")
    for doc in ("docs/ARCHITECTURE.md", "docs/PROJECT_PROFILE.md"):
        if doc not in missing:
            value = (ROOT / doc).read_text(encoding="utf-8")
            if "PLACEHOLDER" in value or "UNVERIFIED" in value:
                print("NOT_CONFIGURED: review project-specific technical facts:", doc)
                problems.append(doc)
    if not configured_checks():
        print("NOT_CONFIGURED: checks.json requires real verified argv checks")
        problems.append("checks.json")
    git = run(["git", "rev-parse", "--is-inside-work-tree"])
    if git.returncode == 0 and git.stdout.strip() == "true":
        auth = run([sys.executable, str(ROOT / "harness/common/branch_authority.py"), "status"])
        if auth.returncode:
            print("BLOCK: Git branch authority:", (auth.stdout + auth.stderr)[-350:])
            problems.append("branch authority")
    elif (ROOT / ".git").exists():
        print("BLOCK: Git metadata present but unusable")
        problems.append("Git metadata")
    if problems:
        print("AUDIT: BLOCKED; resolve only observed mandatory gaps before lock")
        return 2
    print("AUDIT: SCRIPT_READY (native host and approvals need separate evidence)")
    return 0


def smoke():
    """Run native adapter handlers on a disposable Git fixture; never edit product files."""
    state = read_state()
    if state is None:
        print("SMOKE: LEGACY mode; use installed native preflight and host tests")
        return 2
    runtime = state.get("runtime")
    if runtime == "antigravity":
        with tempfile.TemporaryDirectory(prefix="bootstrap-antigravity-smoke-") as d:
            dest = pathlib.Path(d)
            common = dest / "harness/common"
            common.mkdir(parents=True)
            for relative in ("setup_hook.py", "setup_lifecycle.py", "verify.py"):
                shutil.copyfile(ROOT / "harness/common" / relative, common / relative)
            checks = common / "checks.json"
            checks.write_text(json.dumps({"checks": [{"name": "allow",
                "argv": [sys.executable, "-c", "pass"]}]}), encoding="utf-8")
            allowed = run([sys.executable, str(common / "setup_hook.py")], cwd=dest)
            checks.write_text(json.dumps({"checks": [{"name": "deny",
                "argv": [sys.executable, "-c", "raise RuntimeError('fixture reject')"]}]}), encoding="utf-8")
            denied = run([sys.executable, str(common / "setup_hook.py")], cwd=dest)
            good, bad = allowed.returncode == 0, denied.returncode != 0
            print("SMOKE_ALLOW:", "PASS" if good else "FAIL")
            print("SMOKE_DENY:", "PASS" if bad else "FAIL")
            if not (good and bad):
                return 1
        print("SMOKE: SCRIPT_TESTED Antigravity Stop wrapper, native dispatch UNVERIFIED")
        return 0
    if runtime not in ("codex", "claude"):
        print("SMOKE: portable adapter lacks a native blocking hook for", runtime,
              "; manual role/skill checks are required before limited handoff")
        return 2
    hook_rel = "harness/" + runtime + "/hook.py"
    hook = ROOT / hook_rel
    if not hook.is_file():
        print("SMOKE: missing adapter:", hook_rel)
        return 2
    with tempfile.TemporaryDirectory(prefix="bootstrap-smoke-") as d:
        dest = pathlib.Path(d) / "project"
        dest.mkdir()
        for relative in ("docs/ARCHITECTURE.md", "docs/CRITERIA.md",
                         "harness/hook-policy.json", "harness/active-task.json",
                         "harness/common/branch_authority.py", "harness/common/snapshot.py",
                         "harness/common/setup_lifecycle.py",
                         "harness/common/task.py", "harness/common/verify.py",
                         "harness/common/checks.json", hook_rel):
            src = ROOT / relative
            if not src.is_file():
                print("SMOKE: missing", relative)
                return 2
            dst = dest / relative
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        if run(["git", "init"], cwd=dest).returncode:
            print("SMOKE: git unavailable for isolated branch tests")
            return 2
        for args in (["git", "config", "user.name", "Bootstrap Fixture"],
                     ["git", "config", "user.email", "bootstrap@example.invalid"],
                     ["git", "add", "."], ["git", "commit", "-m", "smoke fixture"]):
            result = run(args, cwd=dest)
            if result.returncode:
                print("SMOKE: fixture error:", result.stderr[-350:])
                return 2
        branch = run(["git", "branch", "--show-current"], cwd=dest).stdout.strip()
        config = run([sys.executable, str(dest / "harness/common/branch_authority.py"),
                      "configure", "--active", branch, "--apply"], cwd=dest)
        if config.returncode:
            print("SMOKE: cannot configure isolated branch:", config.stdout[-350:])
            return 2
        if runtime == "codex":
            def hook_call(patch):
                payload = {"hook_event_name": "PreToolUse", "tool_name": "apply_patch",
                           "tool_input": {"command": patch}}
                p = run([sys.executable, str(dest / hook_rel)], cwd=dest, data=json.dumps(payload))
                try:
                    return p.returncode, json.loads(p.stdout)
                except ValueError:
                    return p.returncode, {}
            allowed = hook_call("*** Begin Patch\n*** Update File: docs/ARCHITECTURE.md\n@@\n-absent\n+present\n*** End Patch")
            blocked = hook_call("*** Begin Patch\n*** Add File: ../escape.md\n+bad\n*** End Patch")
            good = allowed[0] == 0 and allowed[1].get("hookSpecificOutput", {}).get("permissionDecision") != "deny"
            bad = blocked[1].get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
        else:
            def hook_call(path):
                payload = {"hook_event_name": "PreToolUse", "tool_name": "Edit",
                           "tool_input": {"file_path": path}}
                return run([sys.executable, str(dest / hook_rel)], cwd=dest, data=json.dumps(payload))
            good = hook_call("docs/ARCHITECTURE.md").returncode == 0
            bad = hook_call("../escape.md").returncode == 2
        print("SMOKE_ALLOW:", "PASS" if good else "FAIL")
        print("SMOKE_DENY:", "PASS" if bad else "FAIL")
        if not (good and bad):
            return 1
    print("SMOKE: SCRIPT_TESTED on isolated clone, NOT real host dispatch")
    return 0



def locked_files(runtime):
    """Local change detection, not OS-level immutability or authenticated locking."""
    names = ["harness/hook-policy.json", "harness/common/setup_lifecycle.py",
             "harness/common/branch_authority.py", "harness/common/snapshot.py",
             "harness/common/task.py", "harness/common/verify.py",
             "harness/common/checks.json"]
    names += {
        "codex": [".codex/hooks.json", "harness/codex/hook.py"],
        "claude": [".claude/settings.json", "harness/claude/hook.py"],
        "antigravity": [".agents/hooks.json", "harness/common/setup_hook.py"],
    }.get(runtime, [])
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in names if (ROOT / name).is_file()}


def check_lock(state):
    expected = state.get("locked_files", {})
    if not isinstance(expected, dict) or not expected:
        print("LOCK_INTEGRITY: UNVERIFIED (no recorded hashes)")
        return False
    actual = locked_files(state.get("runtime"))
    if actual != expected:
        print("LOCK_INTEGRITY: DRIFT; do not call setup complete, request reviewed maintenance")
        for name in sorted(set(actual) | set(expected)):
            if actual.get(name) != expected.get(name):
                print("DRIFT:", name)
        return False
    print("LOCK_INTEGRITY: HASHES_MATCH (not host enforcement)")
    return True


def host_test(surface="local"):
    state = read_state()
    if state is None:
        print("BLOCK: no staged setup; follow legacy host-specific instructions")
        return 2
    runtime = state.get("runtime")
    if surface == "codex-cloud":
        if runtime != "codex":
            print("BLOCK: codex-cloud test instructions require primary runtime codex")
            return 2
        print("CODEX_CLOUD_LIMITED_VERIFICATION: use the CURRENT cloud task; do not require a new IDE tab/session.")
        print("1. Preserve the original source; use a disposable checkout/temporary test project in the same task.")
        print("2. Run setup_lifecycle.py audit and smoke, plus relevant installer regression in that disposable workspace.")
        print("3. Record which native hook events, if any, the cloud service actually dispatched.")
        print("4. Same-task Python probes are SCRIPT_TESTED only; do NOT claim fresh-session, native-hook enforcement,")
        print("   trusted host integration, authenticated Human approval, or a completed final lock.")
        print("5. Submit the tested changes and limitations to Human for review (e.g. PR); the agent cannot")
        print("   impersonate the Human-operated activate/finalize terminal confirmation.")
        print("If no independent Human confirmation/host test is available, leave BOOTSTRAPPING and report")
        print("HOOK_RUNTIME_UNVERIFIED / MANUAL_HANDOFF_REQUIRED. This is not a failure of code smoke.")
        return 0
    print("WARNING: DO NOT CLOSE THE ORIGINAL SETUP TAB.")
    print("Keep setup session open. Open a NEW coding agent tab in a safe temporary COPY,")
    print("never a production branch when testing forbidden writes. Return FAIL/BLOCK logs")
    print("to the setup tab, not to a new repair agent.")
    if runtime == "codex":
        print("CODEX: in fresh tab run /hooks and check registered SessionStart/PreToolUse/Stop.")
        print("Test one harmless allowed patch and one explicitly disallowed patch against")
        print("a DISPOSABLE Git worktree with branch authority and trusted native hooks.")
    elif runtime == "claude":
        print("CLAUDE: in fresh session check UserPromptSubmit and PreToolUse native hook events.")
        print("Use Edit on a safe test file; attempt a blocked Edit ONLY in disposable clone.")
    elif runtime == "antigravity":
        print("ANTIGRAVITY: inspect installed .agents/hooks.json and test actual Stop dispatch")
        print("with configured passing and failing verification in a disposable clone.")
    else:
        print("GENERIC/CONTINUE: native hooks are not registered by this portable setup.")
        print("Verify real roles/skills and configured checks; report native guard UNVERIFIED.")
    print("Staged project hooks intentionally defer blocking until lock. For negative")
    print("pre-lock tests, inspect a DISPOSABLE fixture with the staged marker absent;")
    print("do not remove/change setup-state.json in the actual project.")
    print("Report host version, exact observed allow/deny events and logs. Supply evidence")
    print("in harness/setup-live-evidence.json (state/private), not in an approved plan.")
    print('Required JSON fields: {"runtime": "' + str(runtime) + '",')
    print(' "host_version": "observed-version", "fresh_session": true,')
    if runtime in ("continue", "generic"):
        print(' "roles_loaded": true, "checks_executed": true,')
        print(' "native_hook_available": false, "notes": "actual observed results"}')
    else:
        print(' "hook_dispatched": true, "allow_observed": true,')
        print(' "deny_observed": true, "notes": "actual event evidence"}')
    print("Never claim real native verification from this printed checklist.")
    return 0


def finalize(evidence):
    state = read_state()
    if state is None or state.get("phase") not in ("READY", "READY_WITH_LIMITATIONS"):
        print("BLOCK: finalization requires completed final lock and post-lock checks")
        return 2
    if not check_lock(state):
        return 2
    path = pathlib.Path(evidence).resolve()
    if not path.is_file() or not path.is_relative_to(ROOT) or path == STATE:
        print("BLOCK: post-lock evidence must be an existing in-project file")
        return 2
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print("BLOCK: post-lock evidence is invalid JSON")
        return 2
    limited = state.get("phase") == "READY_WITH_LIMITATIONS"
    required = (("fresh_session", "roles_loaded", "checks_executed", "post_lock_allow")
                if limited else ("fresh_session", "hook_dispatched", "post_lock_allow", "post_lock_deny"))
    if (not isinstance(record, dict) or record.get("runtime") != state.get("runtime") or
            not isinstance(record.get("host_version"), str) or not record["host_version"].strip()
            or any(record.get(k) is not True for k in required)
            or not isinstance(record.get("notes"), str) or not record["notes"].strip()):
        print("BLOCK: post-lock verification evidence incomplete")
        return 2
    updated = dict(state, phase="HANDOFF_COMPLETE",
                   limited_native_hooks=limited,
                   post_lock_evidence_path=str(path.relative_to(ROOT)),
                   post_lock_evidence_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    temp = STATE.with_name("setup-state.json.new")
    if temp.exists() or temp.is_symlink():
        print("BLOCK: setup state transaction already pending")
        return 2
    try:
        temp.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
        temp.replace(STATE)
    finally:
        if temp.exists():
            temp.unlink()
    print("HANDOFF_COMPLETE: manual observations recorded, NOT independently authenticated")
    if limited:
        print("LIMITATION: native blocking hooks NOT_CONFIGURED, GUIDED_ONLY workflows")
    print("PLANNER START PROMPT: Invoke Planner. Read approved CRITERIA, ARCHITECTURE,")
    print("PROJECT_PROFILE and codebase; create/review Implementation Plan and GOALMAP.")
    print("Start EVERY Plan section with a GOAL: why does this code exist and what")
    print("observable product result will it achieve? Link approved CRITERIA IDs,")
    print("acceptance and tests. Derive milestones; ask Human to approve before tasks.")
    return 0


def activate(evidence):
    state = read_state()
    if state is None or state.get("invalid"):
        print("BLOCK: no valid staged setup state")
        return 2
    if state.get("phase") in ("READY", "READY_WITH_LIMITATIONS", "HANDOFF_COMPLETE"):
        print("READY: already activated; do not rewrite lock evidence")
        return 0
    limited = state.get("runtime") in ("continue", "generic")
    audit_result = audit()
    smoke_result = smoke()
    if audit_result or (smoke_result and not limited):
        print("BLOCK: setup audit/smoke incomplete")
        return 2
    path = pathlib.Path(evidence).resolve()
    if not path.is_file() or not path.is_relative_to(ROOT) or path == STATE:
        print("BLOCK: evidence must be an existing file inside project")
        return 2
    try:
        item = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print("BLOCK: invalid evidence JSON")
        return 2
    if (not isinstance(item, dict) or item.get("runtime") != state.get("runtime") or
            not isinstance(item.get("host_version"), str) or not item["host_version"].strip()):
        print("BLOCK: observed host evidence missing or mismatched")
        return 2
    required_observations = (("fresh_session", "roles_loaded", "checks_executed")
        if limited else ("fresh_session", "hook_dispatched", "allow_observed", "deny_observed"))
    if any(item.get(name) is not True for name in required_observations):
        print("BLOCK: missing verified observations:", ", ".join(required_observations))
        return 2
    if limited and item.get("native_hook_available") is not False:
        print("BLOCK: portable adapter must honestly record missing native hook")
        return 2
    if not isinstance(item.get("notes"), str) or not item["notes"].strip():
        print("BLOCK: provide concrete observation notes")
        return 2
    updated = dict(state, phase="READY_WITH_LIMITATIONS" if limited else "READY", evidence_path=str(path.relative_to(ROOT)),
                   evidence_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                   locked_files=locked_files(state.get("runtime")))

    temp = STATE.with_name("setup-state.json.new")
    if temp.exists() or temp.is_symlink():
        print("BLOCK: unfinished state transaction")
        return 2
    try:
        temp.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
        temp.replace(STATE)
    finally:
        if temp.exists():
            temp.unlink()
    print("READY_WITH_LIMITATIONS: native hooks unavailable; GUIDED_ONLY" if limited
          else "READY: configuration activation recorded; requires POST-LOCK LIVE retest")
    print("MANUAL_COORDINATION ONLY: file evidence does not authenticate human approval")
    return 0



def manual_terminal_gate(action):
    """Human-operated terminal friction only: a capable agent can still emulate a TTY."""
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("BLOCK: " + action + " requires Human to open a separate interactive terminal.")
        print("Do not run this through an agent command tool, pipeline, CI or redirected input.")
        return False
    print("MANUAL CHECK: review evidence and observations before proceeding.")
    print("This is NOT cryptographic identity verification. Do NOT ask an AI agent to type it.")
    phrase = "CONFIRM " + action.upper()
    print("Type", phrase, "to continue:")
    try:
        typed = input("> ")
    except (EOFError, KeyboardInterrupt):
        return False
    if typed != phrase:
        print("BLOCK: confirmation phrase did not match")
        return False
    return True



def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    choices = p.add_subparsers(dest="action", required=True)
    choices.add_parser("status")
    choices.add_parser("audit")
    choices.add_parser("smoke")
    host = choices.add_parser("host-test")
    host.add_argument("--surface", choices=("local", "codex-cloud"), default="local",
                      help="Host verification instructions; Codex Cloud uses same-task LIMITED checks")
    act = choices.add_parser("activate")
    act.add_argument("--evidence", required=True, help="Manual real-host observation JSON inside the project")
    act.add_argument("--human-approved", action="store_true", help="Deprecated compatibility flag; never bypasses manual terminal gate")
    done = choices.add_parser("finalize")
    done.add_argument("--post-lock-evidence", required=True)
    done.add_argument("--human-approved", action="store_true", help="Deprecated; interactive confirmation is still required")
    a = p.parse_args(argv)
    if a.action == "status":
        state = read_state()
        print(json.dumps(state or {"phase": "LEGACY_NO_STAGED_STATE"}, indent=2))
        if state and state.get("phase") in ("READY", "READY_WITH_LIMITATIONS", "HANDOFF_COMPLETE"):
            return 0 if check_lock(state) else 2
        return 0
    if a.action == "audit":
        return audit()
    if a.action == "smoke":
        return smoke()
    if a.action == "host-test":
        return host_test(a.surface)
    if not manual_terminal_gate(a.action):
        return 2
    if a.action == "activate":
        return activate(a.evidence)
    return finalize(a.post_lock_evidence)


if __name__ == "__main__":
    sys.exit(main())
