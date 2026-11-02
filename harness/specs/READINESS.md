# Readiness — Codex reference implementation

The authoritative machine-readable inventory is `harness/common/capabilities.json`; tier requirements are in `harness/specs/TIER_MANIFEST.json`.

## Two different readiness questions

**Generic template usability:** Codex and Google Antigravity IDE are `GENERIC READY` based on tested installed-app use: copy the prepared generic coding-agent package without rewriting shared roles, skills or hooks merely to start using it. Claude Code has a complete prepared adapter/configuration but is not host-tested. Continue has prepared role configs/rules and is near generic-ready, subject to actual provider/model selection and Continue host checks. Other coding agents may port adapters following the supplied instructions. The central product purpose is to **save setup tokens/quota** by reusing template content.

**Project/host capability verification:** Each target project still needs actual requirements, stack, host/API, paths, build/test commands, Git branch choice and optional model settings. `RUNTIME_VERIFIED`, `ENFORCED` and the capability inventory measure specific evidenced host behaviors and guard implementations, **not whether users can copy a generic agent template and start using it**. Do not edit `capabilities.json` to treat generic readiness as a signed-gate, runtime-hook trust or sandbox test.


**Implemented and Python CI-tested**: safe installer, role files, `common/verify.py` and `inventory.py`, scoped hash-checked `common/snapshot.py`, scoped one-task `common/task.py`, and Codex `SessionStart` / `PreToolUse` / `Stop` hook handler (including bounded single continuation). The `.codex/hooks.json` file is ready to request native registration; **the checked-in capability inventory still marks separately reproducible native hook trust, dispatch, event semantics and permissions UNVERIFIED unless corresponding evidence is supplied**.

**Not fully implemented**: authenticated human-only approvals, secure journal/ledger, signed gate engine, full trace and STALE propagation, milestone management, autonomous review orchestration, Full-tier Git admin / repair. Therefore no Standard/Full tier may claim a complete autonomous harness. Lite includes actual explicit snapshot support; a claim of host-level enforcement still requires real-host verification, independently of generic copy/use readiness.

Run `python harness/common/status.py --tier Standard --runtime codex`. Exit 2 means missing tier capability or host smoke. For Claude and other IDEs, Python can be reused, but native hook adapters are not implied by Codex hooks.

Labels:
- READY_CONTENT = files/presets exist; no proof loaded.
- SCRIPT_TESTED = Python logic exercised on named CI OS/Python versions.
- RUNTIME_VERIFIED = host actually loaded/dispatched hooks and agents with observed trust and permissions.
- ENFORCED = actual negative tests prove bypass impossible for that declared boundary.
- GUIDED_ONLY = prompts/coordinated process with no technical guard.
- NOT_CONFIGURED = engine, task or required capability absent.
- UNVERIFIED = actual host behavior not tested.

Codex subagents inherit effective parent permission policy; a "read-only" instruction is not an isolated security boundary. A manual chat instruction authorizes bounded coordination through host controls only, not an authenticated gate signature. See `APPROVAL.md` and `APPROVAL_MAINTENANCE.md`.

## Staged setup and handoff (new)
`harness/common/setup_lifecycle.py` provides an optional `--staged` setup coordinator (installer flag), config audit, disposable positive/negative Python smoke, a host-test checklist, hash-based operational lock and separate post-lock handoff. It is NOT an authenticated gate/immutable policy; user approval is manual coordination. Native hook enforcement must be verified separately on the actual client. Continue/generic may finish as READY_WITH_LIMITATIONS only when role and check evidence exists, never claim a native blocking hook was installed.

### Evidence scope of Tested labels
Generic template CLI/adapter regression: Linux, macOS, Windows × Python 3.9/3.12 (GitHub Actions `bootstrap-scripts.yml`; dated CI logs under the linked GitHub Actions workflow). Repository test code: `tests/test_installer.py`, `tests/test_setup_smoke.py`, `tests/test_staged_setup.py`. This supports packaged-file/script compatibility, **not** authenticated native hook dispatch. For the original historical installed-app usability claims, see `docs/reports/2026-10-18-setup-smoke.md`; do not fabricate client versions or dates not recorded there. Each new target project still needs fresh host tests before RUNTIME_VERIFIED.
