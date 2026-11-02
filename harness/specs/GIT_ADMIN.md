# Git administration contract (Full, optional)

Not an executable script. Install only when Git is in use and the user approved the mechanism.

- Inspect repo, remote, working tree, branch and merge state before action.
- Default: do not push. Direct push forbidden by real guard if claimed ENFORCED.
- Authorized push binds exact request, remote, ref and commit set, one use only, with required gate PASS.
- Protect uncommitted work, unknown branches and unrelated commits. No unconditional reset --hard, force push, unreviewed branch deletion or history rewrite.
- If no Git: NOT_APPLICABLE. If integration unknown or unverified: BLOCKED/UNVERIFIED.
- Test with local disposable remotes, both legitimate and prohibited operations.

## Active development branch authority — all Git tiers

Before any Git write, checkout, branch creation, push, PR or merge, consume the shared `harness/common/branch_authority.py` checker and human-selected local policy from the **Git common directory**; see `BRANCH_AUTHORITY.md`. This minimal branch check applies to all tiers using Git, even though advanced Git administration remains Full/NOT_CONFIGURED.

The stable Git default branch may be **frozen** while `v5` is active. Planner plans against `v5`; Coder writes to `v5` or explicitly registered work branches; PRs merge into `v5`, never automatically into `main`. Registered work branches require explicit policy entries. A missing authority, detached HEAD or unknown target fails closed. Changes to the authority need the Human's explicit choice; the Python configure flag cannot authenticate consent.

The Python guard and observed apply_patch hook are not hard Git-server protections. A repo administrator should use server-side branch protection where preventing direct push/merge into frozen branches is essential. The authorization used for push/merge still obeys `APPROVAL.md`.
