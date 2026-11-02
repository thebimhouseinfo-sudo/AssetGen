---
name: safe-change
description: Use for safe change work when the task calls for this repeatable workflow.
---

# safe-change

## Procedure
1. Inspect status, allowed paths, and for Git projects run `harness/common/branch_authority.py check-write`; block on frozen/unknown/detached branch.
2. preserve user changes.
3. snapshot scoped files and a tested restore path.
4. make small isolated edit.
5. inspect diff and unsafe changes.
6. no destructive reset, secret exposure, unauthorized push.

## Output
Actual findings, evidence, limitations and next authorized action. This skill never changes user-approved theory, role permissions or approval policy.
