# Setup intake — IDE dialog and CLI menu contract

**Purpose:** prevent the user from confusing command/tool permission requests with project-configuration questions, while preserving selected answers in an auditable, local trace. The host is responsible for any native dialogs; the Bootstrap CLI provides a terminal wizard where needed.

## UX sequence

1. Emit one short **chat notice only** before invoking a command that may require permission. It explains that **after the command is authorized** the user will answer separate configuration questions. The notice contains no questions.
2. The host asks permission to run the command. **Never** treat permission-button selection as a setup answer.
3. In an **IDE**, use a genuine host-native structured dialog for unresolved settings. In a **CLI**, use its native numbered/text choice UI; if unavailable, run the checkout terminal wizard **before the staged install**: `python <BOOTSTRAP_CHECKOUT>/project-template/harness/common/setup_intake.py --preinstall --runtime RUNTIME --output PRIVATE_TEMP_FILE`. The wizard prints numbered options and reads from a **real TTY**. Pass that file to the installer with `--intake-file PRIVATE_TEMP_FILE` and match its chosen `--tier` / `--config-git`. Do not redirect or spoof stdin/TTY, or ask the user to paste choices into chat.
4. Store each non-secret response in private local `harness/setup-intake.json`; the question IDs, exact values, `channel`, `source`, and optional session/event reference make choices traceable.
5. The staged setup audit validates presence, shape, and the tier/Git choices against the installed manifest. It refuses mismatches; a syntactically valid trace is not sufficient. If none of these interactive input routes is possible, report `INTERACTIVE_INTAKE_UNAVAILABLE` and keep setup unfinished.

## Trace schema

```json
{
  "schema_version": 1,
  "channel": "cli_menu",
  "runtime": "codex",
  "host_event_ref": null,
  "responses": [
    {"id": "tier", "value": "Standard", "source": "cli_menu"},
    {"id": "git_mode", "value": "local", "source": "cli_menu"}
  ]
}
```

For an IDE, use `channel: "native_dialog"` and `source: "native_dialog"`. The `host_event_ref` is an observed session/event ID when the host exposes one; otherwise use null, not an invented ID. Both forms support `setup_lifecycle.py audit`. The audit checks structure/runtime consistency, **not real user identity or independent proof of the host interaction**.

## Only ask unresolved questions

- Tier (Lite / Standard / Full, Standard recommended for Planner/Tester)
- Git mode (local / tracked)
- Human-selected active development branch and any frozen branches, if applicable
- Other genuine choices not discoverable from verified workspace context

The short user prompt already states project directory and new/existing mode. Do not re-ask. Never store credentials, API keys or other secrets as intake answers. CRITERIA, technical direction, Final Lock and final handoff have independent Human Gates. The CLI wizard deliberately refuses noninteractive execution and refuses to overwrite prior intake without an explicit reviewed reconciliation; a replayed or synthetic CI fixture is not an approval.

**Compatibility:** The packaged wizard still supports post-install use in an already-staged project for a preselected tier, but will reject selecting a different tier. New CLI setups should use `--preinstall`. IDE tools should similarly capture selections before install when possible; store genuine native results as a temporary trace and use `--intake-file`. All paths are local/non-secret and are not an approval or user identity proof.
