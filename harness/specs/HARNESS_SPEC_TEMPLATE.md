# HARNESS_SPEC (Full): approved intent of every blocking rule

Install as `harness/HARNESS_SPEC.md`. Written by bootstrap from the approved plan, approved by the user via request. Keep it short: one row per guard. The fixer repairs the harness to match this file; it never loosens a rule to get past a block.

| Rule ID | Guard (hook/gate/policy) | Intent | Allowed example (in -> out) | Blocked example (in -> out) | Who can unlock, via which channel | Enforcement state |
|---|---|---|---|---|---|---|
| <R-01> | <e.g. pre-tool guard on CRITERIA> | <what it protects> | <input -> allowed> | <input -> BLOCK[code]> | <request type + channel> | UNVERIFIED |

## Required BLOCK message shape

`BLOCK[<code>] component=<..> rule=<id in this file> defined-at=<file:line> reason=<..> unlock-needs=<request/evidence> by=<who, which channel>`

Also write the same data to `harness/last-block.json`.

## Maintenance

- Record every change in `harness/CHANGELOG.md` (date, problem, tier T0/T1, request id, files, rollback).
- Ambiguity in this file: ask the user; do not guess.
