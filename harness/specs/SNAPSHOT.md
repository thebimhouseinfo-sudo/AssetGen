# Implemented scoped Python snapshot and restore

Run in the installed project:

```bash
python harness/common/snapshot.py capture docs/ARCHITECTURE.md
python harness/common/snapshot.py restore SNAPSHOT_ID
python harness/common/snapshot.py restore SNAPSHOT_ID --apply --expect-current docs/ARCHITECTURE.md=CURRENT_SHA256
```

`capture` accepts **explicit existing regular project files** (maximum 8 MiB per file); rejects symlinks, traversal, secrets such as `.env`, and snapshot storage. Blobs and SHA-256 manifest go under Git-ignored `harness/snapshots/`. Restore is preview-only by default. `--apply` requires **the exact current SHA for every restored file**; if anything changed again, restoration is blocked. Does not delete files or run `git reset`.

Codex `PreToolUse` attempts pre-edit snapshots only for recognized `apply_patch` paths. Shell/MCP/hosted edits are **not** reliably intercepted, and snapshots do not protect secrets or guarantee rollback after arbitrary operations. Treat broader interception as a runtime-specific future requirement, not as implemented protection.
