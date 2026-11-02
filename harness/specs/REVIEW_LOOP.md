# Review and repair orchestration — remaining Codex-first requirement

Codex native role TOMLs and Python Stop hook are installed, but **there is no autonomous Planner/Reviewer/Critic orchestration engine**. The Stop hook runs trace-link and configured-script checks and allows at most one prompted retry for the active turn. It does not pretend to call reviewers or approve gates.

When an approved milestone reaches a real trigger, the main agent may **coordinate manually**: verify/test → Reviewer evaluates approved goal/AC and exclusions → Critic checks only public artifact → Reviewer classifies findings → Coder minimally fixes in scope. Report any manual coordination as GUIDED_ONLY, never ENFORCED.

Future implementation must use Codex native subagents and their verified runtime controls, with a bounded task loop, target hashes and actual approval channel. Tests should cover trigger absent, no findings, unrelated suggestions, two consecutive failures, retry exhaustion and STOP. Do not introduce a separate daemon or VM for this.
