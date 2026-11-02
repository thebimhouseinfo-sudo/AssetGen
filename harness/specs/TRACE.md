# Trace and stale propagation — implementation boundary (Standard+)

**Implemented**: `python harness/common/task.py --stage plan|delivery` checks one explicitly `ACTIVE` goal from `harness/active-task.json`, with approved theory IDs present in `docs/CRITERIA.md` and an explicit GOAL identifier present in `docs/IMPLEMENTATION_PLAN.md`, planned tests, and (delivery) existing in-project test/evidence files. No task / empty links / missing files → `NOT_CONFIGURED` (exit 2), not PASS. It does **not** certify test semantics or human approval.

**Not yet implemented**: full graph CRITERIA ID → Plan GOAL → milestone → task → files/tests/evidence, `docs/TRACE.md` generation, automatic STALE propagation, signed gate expiry and affected-goal dependency update. Those must remain NOT_CONFIGURED.

When implementing, do not edit generated `docs/TRACE.md` by hand; scope stale propagation to truly affected approved IDs and mark unsourced goals OPEN, not silently approved.
