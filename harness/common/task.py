#!/usr/bin/env python3
"""Validate one scoped task's trace/evidence without inventing approvals or gates."""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFIG = ROOT / "harness" / "active-task.json"

def validate(path=CONFIG, stage="delivery"):
    try:
        task = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise ValueError("active task not configured: " + str(exc)) from exc
    if not isinstance(task, dict) or task.get("status") != "ACTIVE":
        raise ValueError("active task is NOT_CONFIGURED")
    goal = task.get("goal_id")
    theory = task.get("theory_ids")
    tests = task.get("tests")
    evidence = task.get("evidence")
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError("approved goal ID missing")
    if not isinstance(theory, list) or not theory or not all(isinstance(x, str) and x.strip() for x in theory):
        raise ValueError("approved theory IDs missing")
    plan = ROOT / "docs/IMPLEMENTATION_PLAN.md"
    if not plan.is_file():
        raise ValueError("Implementation Plan/GOALMAP missing")
    text = plan.read_text(encoding="utf-8")
    if not re.search(r"(?<![\w-])" + re.escape(goal) + r"(?![\w-])", text):
        raise ValueError("goal ID not found in Implementation Plan/GOALMAP: " + goal)
    if not isinstance(tests, list) or not tests or not all(isinstance(x, str) and x.strip() for x in tests):
        raise ValueError("planned test links missing")
    criteria = (ROOT / "docs/CRITERIA.md").read_text(encoding="utf-8")
    for theory_id in theory:
        if not re.search(r"(?<![\w-])" + re.escape(theory_id) + r"(?![\w-])", criteria):
            raise ValueError("theory ID not found: " + theory_id)
    if stage == "delivery":
        if not isinstance(evidence, list) or not evidence or not all(isinstance(x, str) and x.strip() for x in evidence):
            raise ValueError("actual evidence links required")
        for name in tests + evidence:
            rel = pathlib.Path(name)
            if rel.is_absolute() or any(x in (".", "..") for x in rel.parts):
                raise ValueError("link escapes project")
            path = ROOT / rel
            if not path.is_file() or not path.resolve().is_relative_to(ROOT):
                raise ValueError("missing in-project test/evidence: " + name)
    return goal, theory

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", choices=["plan", "delivery"], default="delivery")
    a = p.parse_args(argv)
    try:
        goal, theory = validate(stage=a.stage)
    except (OSError, ValueError) as exc:
        print("NOT_CONFIGURED:", exc)
        return 2
    print("TRACE_LINKS_VALID:", goal, "theory_ids=" + ",".join(theory))
    print("This is not a semantic review, authenticated approval or gate signature.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
