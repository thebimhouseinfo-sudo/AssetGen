# Python verify — supported contract

`harness/common/verify.py` implements verified argv commands from `checks.json` without shell execution. Empty/invalid checks → NOT_CONFIGURED exit 2; failure/timeout → 1; all configured checks succeed → 0. Actual host acceptance and product behavior are separate.

Codex `Stop` calls the one-task `harness/common/task.py` validator and script verify **only** for a configured ACTIVE goal; a failing check requests **one bounded continuation**, not an indefinite retry. The `stop_hook_active` event flag prevents repeat. Python CI tests are SCRIPT_TESTED; native Codex hook loading/trust must still be smoke-tested.

Check lists must be written from verified target project commands and approved scope. Optional dependency/secret scans or full trace must not be claimed unless genuinely configured and tested. Snapshot covers recognized direct apply_patch edits, not Bash/MCP/hosted edits.
