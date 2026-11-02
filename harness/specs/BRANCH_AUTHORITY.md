# Git branch authority — local operational source of truth

Admin is a **function**, not an extra agent. The currently authorized development branch is not necessarily Git's default `main`. Branch selection is operational state, **not product CRITERIA**.

## Canonical state
Python reads exactly `<git-common-dir>/bootstrap/branch-authority.json`, shared by worktrees of **one clone**, and independent of branch checkout. The tracked sample `harness/config/branch-authority.example.json` is only a reference, **never live authority**. Other clones/machines MUST be configured separately and must not infer active branch from Git default, latest checkout, remotes or commit history.

## Human-directed setup (Python 3.9+, no packages)
Run from the project with the desired branch already existing locally:

```bash
python harness/common/branch_authority.py configure --active v5 --freeze main --remote origin --work feat/task-x
python harness/common/branch_authority.py configure --active v5 --freeze main --remote origin --work feat/task-x --apply
python harness/common/branch_authority.py status
```

The first command previews; `--apply` writes. To change an already configured policy, explicitly choose a full replacement and add `--replace --apply`. The command's presence is **not proof of authenticated human consent**: Planner/Admin must first obtain explicit Human selection under actual host controls. `--remote` may be omitted for local-only development; then push checks fail closed. `--work` may be omitted for direct edits on active. Every work branch must be pre-registered against the active branch, rather than assumed valid from its name.

## Before consequential actions
- **Planner:** read `status` to plan integration on the active branch; do not propose merging into frozen `main`.
- **Coder:** `check-write` before edits. On an unregistered branch, detached HEAD or missing authority: do not edit. For a new work branch, use `check-create --base v5 --new feat/task-x` before creating it; registration and initial checkout of active are required.
- **PR/merge:** `check-merge --source feat/task-x --target v5`; merge target must be active and unfrozen.
- **Push:** `check-push --source feat/task-x --target feat/task-x --remote origin`. It validates explicit remote/ref and current checkout. Do not push to a different destination ref without a separately agreed workflow.
- The Codex `PreToolUse` adapter checks branch authority before observed **direct apply_patch** writes in Git projects. For non-Git projects it skips branch checks. It does **not** intercept arbitrary shell, MCP, hosted Git operations or manual IDE edits.
- Human-authorized branch freeze/release or active branch switch updates the Git common-dir state **before** new write/merge operations. Without state or when uncertain: BLOCKED, not default main.

## Boundaries
These are Python guard/check commands and model instructions, not OS/git-server protection. Full automated Git admin, a centrally distributed authority between clones, and authenticated Git policy updates remain NOT_CONFIGURED. To truly prevent server merges/pushes into `main`, configure branch protection and permissions on the Git host. Do not claim a CLI pre-check remains binding after other agents or humans change refs; re-check immediately before performing the actual Git operation.
