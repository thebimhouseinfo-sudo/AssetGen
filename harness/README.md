# Harness — multi-runtime Python scripts and contracts

**No primary runtime.** For unconfigured hosts the `.generic/` package contains portable tier-scoped roles and native-adaptation instructions (not a registered extension). Continue shares the common `.agents/` role/skill contracts with Antigravity while keeping `.continue/` model/role configs separate.  Codex and Google Antigravity IDE are **GENERIC READY**: copy/use has been tested on installed clients without rewriting the generic agent template. Claude Code is configured but lacks real-host testing; Continue is near generic ready but requires model/provider mapping and host testing. Other apps can port the adapter instructions. Shared scripts in `harness/common/` are ordinary Python >=3.9. Runtime-native role and hook adapters are selected deliberately during installation. All projects still need project-specific configuration. Distinguish user-observed generic usability from independent native hook/gate enforcement tests; a reusable setup's READY label does not make a gate engine READY.

| Area | Actual executable | State |
|---|---|---|
| Inventory / configured checks | `common/inventory.py`, `common/verify.py` | SCRIPT_TESTED |
| Explicit file snapshot / guarded restore | `common/snapshot.py` | SCRIPT_TESTED; no pre-edit intercept coverage |
| Single-task link/evidence validation | `common/task.py` with `active-task.json` | SCRIPT_TESTED; not full trace or stale propagation |
| Stop verify hook (Antigravity) | `.agents/hooks.json` → `python harness/common/verify.py` | SCRIPT_TESTED; native Stop dispatch UNVERIFIED until smoke-tested |
| Codex hook bridge | `codex/hook.py` + `.codex/hooks.json` | SCRIPT_TESTED; runtime trust UNVERIFIED |
| Claude Code adapter | `claude/hook.py` + `.claude/settings.json` | SCRIPT_TESTED; runtime trust UNVERIFIED |
| Full gate engine, user-signed gate, journal | `specs/GATES.md`, `APPROVAL.md` | NOT_CONFIGURED |
| Auto Planner/Reviewer/Critic orchestration | `specs/REVIEW_LOOP.md` | NOT_CONFIGURED |
| Full trace generator/stale propagation | `specs/TRACE.md` | NOT_CONFIGURED |

Do not add a VM, server, background daemon or another framework. `specs/` defines what remains to be implemented for the approved tier, not automatic features simply because an instruction exists. Run `python harness/common/status.py --tier Standard --runtime RUNTIME` and record actual CLI smoke results before claiming RUNTIME_VERIFIED or ENFORCED.

### Active Git development branch
`harness/common/branch_authority.py` works across every tier and runtime as an explicit Git branch/merge/push **preflight**; `harness/specs/BRANCH_AUTHORITY.md` explains the authority model. This does not provide universal shell/MCP/remote Git enforcement.
