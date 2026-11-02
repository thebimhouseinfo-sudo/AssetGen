> SUPERSEDED: the current handoff is [HANDOFF_GSA.md](./HANDOFF_GSA.md). This historical document may contain stale status.

# AssetGen — handoff for Qwen Code

## Start here

This is a personal, single-user application. Read the following in order:

1. `AGENTS.md` (if included in your environment): project-specific rules. If unavailable, see the explicit boundaries below; do not infer that host hooks enforce them.
2. `docs/CRITERIA.md`: the **only approved source of product requirements**. Do not rewrite or change it as part of implementation. A product-theory amendment has a separate Human and Technical Advisor decision process described in `AGENTS.md`.
3. `docs/IMPLEMENTATION_PLAN.md`, `docs/MILESTONES.md`, `docs/TECHNICAL_PROPOSAL.md`: approved direction and order, with open technical questions.
4. `TASKS.md` and `docs/reports/task-06-evidence.md`: current delivery state and actual verification. If `TASKS.md` was excluded from the transfer, use this handoff's status and tell the Human it is missing.

Historical records are clearly marked or under `docs/archive/`. They describe the discarded frame/crop/mask product and are not current requirements. `docs/ARCHITECTURE.md` and `docs/PROJECT_PROFILE.md` are dated host evidence; their old concept/offline-only direction is superseded. Reinspect source and environment before relying on host-specific claims.

## What exists

- Batch: React/Vite frontend and Python/FastAPI backend; local model adapter, file-based project/job/revision data and configured default output root. Existing project IDs are internal UUIDs.
- Concept: the old React editor was removed. The tab is an explicitly unconnected placeholder. The old concept-only backend routes and processing have also been removed. Stored data remains; legacy concept jobs are excluded from Batch and protected from ID collisions. This does not mean the new workflow is working.
- TASK-06: Chrome placeholder/Batch-navigation test and frontend build passed. TASK-07 removed the old concept backend; 26 remaining backend tests passed with isolated settings, and a copied-data check read three projects, four Batch jobs and six revision records. See `docs/reports/task-07-evidence.md`. No new real local-model inference was run; `frontend/dist` may be stale.
- ChatGPT Web/plugin/tunnel, HTML renderer, copy ID/image, and the full new concept workflow are **unverified or unimplemented**. Do not describe them as complete.

## Next work: Batch project selection

The approved direction is to let the user create a project with a chosen name or select an existing project by name. Keep the existing system-generated ID internally and the configured default output location. Do not ask for an output folder or make the user remember an ID. Plan for duplicate names without making IDs the user-facing choice. Preserve access to existing projects, generated images and revision history; do not silently overwrite earlier images. Use the same conventions for the future concept flow without implementing its engine now.

First inspect project creation, storage, queue, image publication and gallery code. Derive the smallest scoped task against goal G-05 and obtain any approval required by applicable project instructions before implementing. Verify new/existing project selection, duplicate names, repeated generation, errors and legacy compatibility with temporary directories or copies. If a real local model or UI is unavailable, say exactly what could not be run; do not claim inference passed.

## Afterwards

Design the plugin in detail: inputs, generated files, responsibilities, errors, HTML/asset paths, render, selection, clipboard and revision handling. Identify the actual plugin and tunnel and verify a bounded one-asset bridge before committing to integration. User approval occurs after ChatGPT's analysis and before HTML/prompts and generation. Preserve images and allow restoration. Product goals are in Criteria; technical control of ChatGPT and the bridge is not established by this document.

## Environment, safety and verification

- Qwen online may not have this Mac, local model, GPU, browser, user data, installed dependencies or runtime hooks. Paths in `settings.json` are Mac-specific. Check availability; use isolated settings via `ASSETGEN_SETTINGS` and temporary project/output roots. Never run destructive cleanup, migration or tests against the user's real project or output folders.
- Preserve unrelated files, generated assets, model weights, binary runtime and local user data. Do not install dependencies without Human authorization. Do not assume this directory is a Git repository; if it is Git in your environment, follow the project's branch-authority checks and do not guess the active branch.
- Portable harness and role/skill configurations are provided for reference; their presence does not prove Qwen invokes their hooks or enforces gates. Do not fabricate approval, tests, trace, enforcement or successful local inference. If a required native capability or approval is unavailable, report it and continue safe independent work.
- Historical configured backend check: `python3 harness/common/verify.py` with isolated `ASSETGEN_SETTINGS`. Frontend build and browser check are documented in `README.md`. Confirm dependencies and actual environment before using these commands. Do not weaken tests to pass.

## Transfer warning

This workspace currently has no Git metadata. `.gitignore` excludes `AGENTS.md`, `TASKS.md`, `harness/`, `.agents/`, `docs/PROJECT_PROFILE.md`, model binaries, local projects and output data. A Git-based transfer will not automatically include those paths. When giving Qwen context, deliberately include the project instructions, `TASKS.md` and relevant harness/role configuration if wanted; inspect these files for local paths and sensitive material before sharing. Do not upload model weights, private projects, generated images, logs, credentials or personal files merely to provide source context. The tracked `docs/CRITERIA.md`, Plan, milestones, technical proposal and this handoff must also be included in the transferred source.
