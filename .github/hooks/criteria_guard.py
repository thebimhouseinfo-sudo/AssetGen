#!/usr/bin/env python3
import json
import re
import sys


PROTECTED_PATH = re.compile(
    r"""(?<![a-z0-9_.-])docs/+criteria\.md(?![a-z0-9_.-])""",
    re.IGNORECASE,
)
READ_ONLY_TOOLS = {
    "cat",
    "find",
    "findfiles",
    "get_file_contents",
    "getfilecontents",
    "grep",
    "list_dir",
    "list_directory",
    "listdirectory",
    "listfiles",
    "read",
    "read_file",
    "readfile",
    "read_file_contents",
    "search",
    "view",
}
NON_MUTATING_TOOLS = READ_ONLY_TOOLS | {"askuser"}
CRITERIA_DENIAL = (
    "Blocked before execution; do not retry this product-theory write. "
    "First invoke the Technical Advisor subagent with the exact proposal, "
    "present its advice to the Human, and wait for the Human's post-advice decision. "
    "If Advisor delegation is unavailable, stop and ask the Human to select that agent. "
    "This hook cannot verify the consultation or decision."
)


def respond(payload):
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        respond({
            "permissionDecision": "deny",
            "permissionDecisionReason": "Copilot preToolUse event was not valid JSON.",
        })
        return 0

    if not isinstance(event, dict):
        respond({
            "permissionDecision": "deny",
            "permissionDecisionReason": "Copilot preToolUse event was not an object.",
        })
        return 0

    tool_name = event.get("toolName")
    tool_args = event.get("toolArgs")
    if not isinstance(tool_name, str) or not tool_name.strip() or not isinstance(
        tool_args, (dict, list, str)
    ):
        respond({
            "permissionDecision": "deny",
            "permissionDecisionReason": "Copilot preToolUse event is missing toolName or toolArgs.",
        })
        return 0

    normalized_args = json.dumps(tool_args, ensure_ascii=False).replace("\\", "/")
    normalized_tool_name = re.sub(
        r"[^a-z0-9]", "", tool_name.rsplit("__", 1)[-1].lower()
    )
    if (
        PROTECTED_PATH.search(normalized_args)
        and normalized_tool_name not in NON_MUTATING_TOOLS
    ):
        respond({
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"{CRITERIA_DENIAL} Blocked tool: {tool_name.strip()}."
            ),
        })
        return 0

    respond({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
