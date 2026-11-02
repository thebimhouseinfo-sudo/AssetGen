# Enforcement inventory — actual implementation and missing boundaries

| Mechanism | State before real host smoke |
|---|---|
| Codex `.codex/hooks.json` + `harness/codex/hook.py` for SessionStart/PreToolUse/Stop | SCRIPT_TESTED; native trust UNVERIFIED |
| Direct apply_patch pre-edit snapshot, hash-check restoration | SCRIPT_TESTED on supported direct paths only |
| Verification + single-task trace/evidence link check | SCRIPT_TESTED; not human gate approval |
| Protected CRITERIA write warnings | GUIDED_ONLY, not a real authorization guard |
| Bash/MCP/hosted write interception | NOT_CONFIGURED |
| Authenticated gate ledger, human-only approvals | NOT_CONFIGURED |
| Subagent context isolation / independent sandbox | GUIDED_ONLY unless host-enforced and tested |
| Complete TRACE/STale, autonomous role orchestration | NOT_CONFIGURED |

ENFORCED requires real-host positive and negative tests of the *specific* boundary. Python fixture PASS never equals enforcement. Report rule, real evidence, limitations and recovery for each observed BLOCK.
