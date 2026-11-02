---
name: challenge-feasibility
description: Planner must use this before accepting a new feature, platform-control claim or architectural idea.
---

# challenge-feasibility — evidence before commitment

## Trigger
Every newly proposed capability or change where feasibility matters, including during initial discovery and proposed approved-CRITERIA amendments. This is a Planner skill, not a reason to summon Technical Advisor early.

## Steps
1. State the user's desired observable result separately from the suggested implementation.
2. Break the mechanism into capabilities and list who controls each boundary: our code, available OS APIs, host/client, third-party APIs, or unspecified infrastructure.
3. Look for *specific* evidence in actual source, host/platform documentation, available tools or a reproducible probe. State the environment and limitations; do not present guesses as proof.
4. Classify each material claim: **CONFIRMED_FEASIBLE** (evidence of working mechanism within scope); **UNVERIFIED** (insufficient evidence, test needed); **CONFIRMED_INFEASIBLE** (authoritative boundary or demonstrated contradictory constraints). Lack of proof never establishes impossibility.
5. **UNVERIFIED**: define a minimal spike and observable pass/fail evidence; do not promise the feature or write a delivery plan as though it works. **CONFIRMED_INFEASIBLE**: explain why, reject that implementation and offer feasible narrower alternatives only when genuinely supported.
6. Explain clearly to the Human, including which parts are under project control. No sycophantic approval, unnecessary pessimism, fabricated research, or speculative complexity.
7. Preserve Advisor gate: Planner's ordinary challenge does not activate Advisor. Advisor remains limited to full initial Criteria consultation or settled amendment immediately before applying approved Criteria.

## Example
A GSA server may change its own prompts, memory payload and API requests. That does **not** prove it controls ChatGPT Web's hidden context window allocation, internal reasoning or native UI. Separate voluntary guidance from enforceable control; without a documented mechanism mark the latter unverified or infeasible as evidence dictates.

## Output
Short evidence ledger: claim → classification → source/test → limits → human-readable alternative or test. No delivery commitment until feasibility is established.
