# Manual coordination and protected approval boundaries

Read `APPROVAL.md` for the canonical request/gate contract. This document controls **available authorization mode**, not extra signatures.

**Default MANUAL_COORDINATION:** an explicit human instruction in the current host conversation can coordinate a specific ordinary action, subject to real host permissions. A generic chat "ok" is not enough to infer a sensitive scope. This mode is **not an authenticated gate answer**, so never write AGREE to a trusted ledger, sign G0/G11, claim the human was cryptographically identified or mark an unimplemented gate PASS. The request may be `AWAITING_USER` if authenticated authorization is still required, or `NOT_CONFIGURED` when the adapter is absent.

**Verified AUTHENTICATED_ADAPTER:** allowed only after demonstrating a human-only, agent-unreachable reply channel bound to exact request hash, role isolation and negative tests. Same-identity terminal commands and copy-to-clipboard pages do not prove human-only origin.

**Repair when approval itself is broken:** prepare an exact read-only candidate, original hashes, bounded operations, snapshot/restore instructions and human-visible impacts. Human may authorize a manual maintenance operation through the host's explicit controls, but it remains MANUAL_COORDINATION, *not* a signature retroactively approving the broken ledger. Changes to policy/guard engines are T1. The engine must never approve its own repair.

**Precedence:** host/platform enforced controls → this mode boundary → `APPROVAL.md` authenticated request/gate semantics → role prompts. Under ambiguity use the least-privileged, evidence-backed meaning; never weaken real controls via documentation.
