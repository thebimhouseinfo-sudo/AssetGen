# Tasks — current delivery status

## TASK-06 — concept placeholder and cleanup: completed

Goal G-06. The old concept-only frontend components were removed; the tab now shows an explicitly unconnected placeholder. At TASK-06 the backend concept routes and user data remained; the later TASK-07 removed concept-only backend code without deleting user data. Chrome navigation test, frontend build and 42 isolated backend checks passed; no new real-model inference was run. See [evidence](docs/reports/task-06-evidence.md). Independent code review found no actionable regression. `frontend/dist` was not updated.

## Active — TASK-07: retire old Concept backend (implementation verified)

- Goal G-06; Human requested removal of the old Concept implementation while retaining Batch and user data.
- Remove legacy Concept-only routes, processing and tests after tracing shared code. Keep generic project/export/Batch functionality and leave persisted user files untouched. No new Concept engine in this task.
- Verify retired routes, recovery with mixed legacy/Batch job data, retained Batch tests, build and browser placeholder. Reviewer noted that legacy jobs pass through the shared project reader and must not be rewritten or break startup.
- Result: old concept-only API, model and processing code removed; legacy concept job files are preserved and excluded from Batch. 26 isolated backend checks and the Chrome placeholder test passed; copied-data check read 3 projects, 4 Batch jobs and 6 revision records without changing original data. No real local-model inference was rerun. See `docs/reports/task-07-evidence.md`. Task stays active for delivery verification.
- Snapshot: `20261102T151006-85e15664c1`; legacy browser test snapshot `20261102T151153-65f6506ebf`.

## Next — G-05: named project selection for Batch

Approved plan direction, but no task is active or separately scoped yet. User can create a project with a chosen name or select an existing project by name. Internal IDs and configured default output location remain; no folder picker. Preserve old projects, images and revisions, including duplicate-name and repeated-generation cases. Derive a bounded task and verification from the approved [plan](docs/IMPLEMENTATION_PLAN.md) and [technical proposal](docs/TECHNICAL_PROPOSAL.md); do not fabricate model or host verification.

## Later — G-07 and G-08

Design plugin input/output and responsibilities in detail and test the actual bridge before implementing the complete concept workflow. The plugin, tunnel, HTML render and clipboard are unverified.

Historical tasks are preserved in [archive](docs/archive/tasks-2026-10-22.md). The former TASK-06 proposal for a working renderer was superseded by the UI-only task.
