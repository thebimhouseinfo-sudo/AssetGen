# Approval contract — one mode, no fabricated signatures

This is a specification, not an installed authenticated approval engine.

## Precedence and modes (normative)
1. **Actual host permissions and human-only channels** always take priority. No document can relax them.
2. `APPROVAL_MAINTENANCE.md` defines whether the running workflow is `MANUAL_COORDINATION` or a **verified** `AUTHENTICATED_ADAPTER`. This is the authoritative distinction for *what kind* of user authorization exists.
3. This document defines request data, gates and signatures **only to the extent that the selected mode genuinely supports them**. On any conflict, preserve the stricter protection and report `NOT_CONFIGURED` / `AWAITING_USER`, never silently upgrade manual consent to a trusted signature.

### MANUAL_COORDINATION (default)
A **specific, direct instruction from the human through the host conversation** may authorize ordinary scoped manual work under the host's normal controls, including manually coordinated setup or maintenance. It is *not* independent identity authentication, a protected journal record, a G0/G11 gate signature or proof that the agent cannot impersonate the user. A vague "ok" alone does not establish the exact scope of a protected operation.

For a CRITERIA change: human and Planner settle the exact theory delta; Advisor consults on feasibility and actual technical impact immediately before the edit; **only then** may the human expressly instruct the authorized change under ordinary host controls. Record the scope and observed instruction as *manual coordination only*. Do not claim an electronically authenticated THEORY_CHANGE approval or sign its gate. An unimplemented gate remains `NOT_CONFIGURED`; a pending gate requiring independently authenticated authorization remains `AWAITING_USER`. Neither may be PASS.

### AUTHENTICATED_ADAPTER (opt-in only after negative tests)
Requires a user-only answer channel that the agent **cannot call or impersonate**, bound to request ID, unchanged content/scope hash and verified source. Test malicious agent attempts, changed requests and replay. Only this verified channel may issue attested AGREE / DISAGREE / OTHER and support signing user-only G0/G11. A command reachable by an agent under the same OS identity or a clipboard-generated response is not automatically human-only.

## Request and journal specification (not implemented by this template)
- Trusted, redacted, append-only hash-chain journal if such capture is actually supported.
- A decision quotes an exact substring of a trusted message; if trusted capture is missing, this guarantee is `NOT_CONFIGURED`.
- Request: ID, type, exact before/after, scope/hash, source, impacts, risks, PENDING state.
- Authenticated response choices: AGREE / DISAGREE / OTHER (OTHER requires a note). No automatic expiry.
- AGREE is valid only for the exact unchanged request. DISAGREE rejects. OTHER requires a revised request; it never authorizes the original.
- Reject fabricated quotes, agent self-approval, changed content after response, replay and missing OTHER note.
- Protect journal, decisions, request history and the CRITERIA update path from agent-controlled forgery.
- Never assert a user identity or signature from ordinary chat text.

## Request types
| Type | Intent |
|---|---|
| THEORY_CHANGE | Authorized modification to `docs/CRITERIA.md` after the Advisor checkpoint |
| THEORY_GAP | Human choice on otherwise missing product theory |
| COVERAGE_MAP | Goal-to-theory coverage |
| MILESTONE_SET / MILESTONE_ACCEPT | Milestone planning and final acceptance |
| PUSH / BRANCH_ACTION | Bounded Git change |
| HARNESS_PATCH | Protected harness and policy modifications |
| BREAK_GLASS | One-time explicitly controlled override, not a policy rewrite |
| DEP_ADD / MODEL_CHOICE | Dependency or agent model choice |

## Advisor timing
**First criteria:** Planner completes the full proposed draft, Advisor advises on **the whole draft before first approval**. **Later change:** Human and Planner settle the exact theory delta *without editing the approved file*, human requests application, Advisor consults on the **approved CRITERIA plus delta before any edit or merge**, and human selects the exact scope. Advisor does not sign or edit theory. CRITERIA supplies the requirements; Advisor may inspect relevant architecture, environment or source as needed for feasibility and impact, **never to review Plan/Code**. Explain technical prerequisites, complexity, realistic ripple effects and uncertainty; give Tạm dùng / Ổn / Nâng cao **only when meaningful alternatives exist**, not as a fixed requirement. This advice has no PASS/FAIL verdict or veto. Present plain-language consequences, not a mandatory technical diff.

## Supported release state
Only manual coordination instructions are currently packaged. The authenticated adapter, journal, approval ledger and G0/G11 signing engine remain `NOT_CONFIGURED`. Do not invent UI buttons or human-only commands. See `APPROVAL_MAINTENANCE.md` for a bounded independent repair when approval itself is broken.
