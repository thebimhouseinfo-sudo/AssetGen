import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
GUARD = ROOT / ".github/hooks/criteria_guard.py"


def invoke(event):
    return subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        check=False,
    )


class CopilotCriteriaGuardTests(unittest.TestCase):
    def test_denies_tool_arguments_targeting_criteria(self):
        result = invoke({
            "toolName": "editFiles",
            "toolArgs": {"files": [{"filePath": "docs/CRITERIA.md"}]},
        })

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            json.loads(result.stdout)["permissionDecision"],
            "deny",
        )
        self.assertIn(
            "editFiles",
            json.loads(result.stdout)["permissionDecisionReason"],
        )

    def test_denies_windows_style_criteria_path(self):
        result = invoke({
            "toolName": "runInTerminal",
            "toolArgs": {"command": "python write.py ..\\docs\\CRITERIA.md"},
        })

        self.assertEqual(
            json.loads(result.stdout)["permissionDecision"],
            "deny",
        )

    def test_denies_criteria_path_with_punctuation(self):
        result = invoke({
            "toolName": "applyPatch",
            "toolArgs": {"patch": "(docs/CRITERIA.md)"},
        })

        self.assertEqual(
            json.loads(result.stdout)["permissionDecision"],
            "deny",
        )

    def test_allows_recognized_read_only_tool(self):
        result = invoke({
            "toolName": "read_file",
            "toolArgs": {"path": "docs/CRITERIA.md"},
        })

        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {})

    def test_allows_ask_user_tool_with_criteria_context(self):
        result = invoke({
            "toolName": "Ask User",
            "toolArgs": {
                "message": "What change do you want in "
                + "/".join(("docs", "CRITERIA.md"))
                + "?"
            },
        })

        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {})

    def test_allows_unrelated_tool_call(self):
        result = invoke({
            "toolName": "editFiles",
            "toolArgs": {"files": [{"filePath": "frontend/App.jsx"}]},
        })

        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {})

    def test_denies_malformed_event(self):
        result = subprocess.run(
            [sys.executable, str(GUARD)],
            input="{}",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            json.loads(result.stdout)["permissionDecision"],
            "deny",
        )


if __name__ == "__main__":
    unittest.main()
