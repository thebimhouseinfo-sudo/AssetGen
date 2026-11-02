Follow the root `AGENTS.md` as the project-wide instructions and the selected role contract in `.agents/roles/`. Reusable skills remain in `.agents/skills/`; read the relevant skill when its role contract requires it.

Before every requested finalization or change to the product-theory document, Planner must prepare the exact proposal without writing, invoke the Technical Advisor subagent, present its advice, and wait for the Human's decision afterward. If subagent invocation is unavailable, stop and ask the Human to select Technical Advisor manually. Never retry a denied protected write before that sequence. This is prompt-mediated and must be verified in the Copilot harness.

The Copilot custom agents in `.github/agents/` expose the Bootstrap roles in VS Code. They are prompt-level role definitions, not tool sandboxes or authenticated approvals.

The criteria hook explicitly permits the non-mutating `Ask User` interaction so Planner can collect the requested change before preparing an Advisor proposal.

The repository `preToolUse` hook in `.github/hooks/criteria-policy.json` is best-effort only. It denies tool calls whose arguments name `docs/CRITERIA.md`, except recognized read-only tools. Do not treat it as a complete write restriction or as evidence that Advisor/Human approval occurred. Keep Criteria changes GUIDED_ONLY and require Human review.
