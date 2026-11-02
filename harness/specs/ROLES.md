# Role contracts (configure with target runtime's verified syntax)

| Role | Mandate | Write scope | Input | Output |
|---|---|---|---|---|
| Technical Advisor | Independent human-facing feasibility/complexity/impact consultation before first CRITERIA approval or before application of a human-settled delta; no Reviewer/CR verdict | none | CRITERIA (or CRITERIA + settled delta) as requirements; optional verified architecture/environment/limited source for technical facts, never Plan/Code reviews | product fit, prerequisites, feasible choices where meaningful, likely rework and uncertainty; human decides |
| Planner | Own discovery: personal/team/commercial use, real and committed scale, proportionate data/security needs, exclusions; draft/maintain CRITERIA and derive goals/tasks | initial draft and planning files; approved theory only via authorized post-Advisor update | direct user discussion, confirmed scope and acceptance | complete draft or settled delta, decision summary, plan |
| Coder | One scoped task | source files only | task, goal, profile | code + verify output |
| Tester | Validate actual acceptance | tests, evidence | goal/AC, runtime | tests and measured evidence |
| Reviewer | Reject both unauthorized overengineering and insufficient approved scale/protection | findings/backlog/lessons | approved CRITERIA scope, task, diff, test evidence | grounded blocker or PASS |
| Critic | Independent public-only observations, no private scope compliance claims | none | product and public README ONLY | raw observations for Reviewer |
| Explorer (optional) | Narrow repository research | none | concrete question | concise findings |
| Harness fixer (Full) | Repair harness without weakening policy | harness per authorized tier | block diagnosis/spec | verified patch |

Model, reasoning, sandbox, skill and fallback assignments must be configured and VERIFIED for the actual agent runtime. No silent model substitution. Role != model != project profile != skill. A textual role table is GUIDED_ONLY unless permissions are actually enforced.
