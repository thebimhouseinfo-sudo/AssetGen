---
name: write-criteria
description: Planner uses this to draft or amend the single human-readable product theory in docs/CRITERIA.md.
---

# write-criteria — human-readable product theory

## Purpose
`docs/CRITERIA.md` is the **single source of truth about the product humans want**, not a code specification, implementation plan, architecture diagram or agent execution log. A Human should understand what is being made, who uses it, why, the expected behaviors and accepted limits without needing software-engineering knowledge.

## Two inputs, two distinct responsibilities

**A. New project / no established requirements:** `brainstorm-theory` leads discovery, including its full scope, intended-use, scale, trust, risk and explicit-exclusions questions. Do **not** delete, replace or shortcut those questions. Use `challenge-feasibility` where proposals depend on technical control. Once Human decisions are settled, `write-criteria` converts the resulting product theory into readable CRITERIA; it does not rerun the whole interview.

**B. Existing project / already settled decisions:** `write-criteria` consolidates confirmed Human decisions and, where needed, inspects source code, tests, configuration and observable behavior to reconstruct **CURRENT** implementation. Distinguish (1) Human-confirmed **DESIRED**, (2) evidence-supported **CURRENT**, and (3) **GAP / OPEN**. Implemented code is evidence of what exists, **never automatic Human approval of what should exist**. Do not silently turn accidental/legacy behavior into a requirement or invent product intent from implementation details. Ask only unresolved decisions that materially change scope, rather than repeating new-project brainstorming.

For both paths, reuse any known answers to the scope questions (who uses it; real scale and environment; current versus optional future ambitions; real risks; acceptable protections; exclusions). If an important answer is missing, ask just that question in ordinary language. Keep the questions in `brainstorm-theory`; CRITERIA records **answers and confirmed outcomes**, not a copied questionnaire, raw source notes or a technical threat model. Leave unresolved matters OPEN.

## Mandatory pre-write handoff
Drafting a proposal in conversation is allowed without Advisor. Immediately before **any write to the finalized/approved CRITERIA file**, including initial finalization and edits to an existing file, check: (a) Advisor consulted on the exact material proposal, and (b) Human made a decision after the advice. If missing, do not write; invoke Advisor and return to Human for keep/revise/reject. A materially revised scope resets consultation. Advisor never decides or approves. If actual delegation is unavailable, report the blocker rather than falsely claiming the consultation occurred.

## Required writing approach
1. Write in clear, natural language centered on the user's real problem: what the product is, who it serves, what it is for, user journeys, observable behavior, important constraints, exclusions and success criteria.
2. Express requirements as outcomes and examples understandable to a non-developer. Stable identifiers can be used for traceability but never dominate readability.
3. Document desired behavior separately from current observed behavior. Label unresolved product decisions OPEN and unverified feasibility UNVERIFIED. Never assert a promise just because it was suggested.
4. Include necessary product-level boundaries (e.g. 'works offline', 'never edits files without approval') when Human has chosen them; omit algorithms, libraries, classes, API endpoints, file tree, task breakdown, test commands, milestones, rollout plan, and architecture alternatives unless a specific technical constraint is itself a Human-approved product requirement.
5. Use `challenge-feasibility` before proposing an unverified technical dependency as a committed capability. Treat research evidence as support for the discussion, not as a reason to turn CRITERIA into a technical research paper.
6. For an existing product, reconstruct observed CURRENT behavior from evidence but only the Human sets DESIRED behavior. Follow existing Advisor and Human approval gates before any protected CRITERIA update; do not create a competing theory file.

## Helpful outline (adapt to product; don't fill with boilerplate)
- What we are building and why
- Who will use it and in what circumstances
- What users must be able to do and how it should behave
- What is explicitly outside scope
- Constraints, tradeoffs, assumptions and unresolved decisions
- Plain-language examples of successful use

## Quality check
Could a non-technical stakeholder read this alone and explain what the product should do? Can technical implementers later derive a Plan without smuggling new product decisions into it? If either answer is no, revise.
