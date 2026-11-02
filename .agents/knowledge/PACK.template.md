# <Project or host knowledge pack> (OPTIONAL)

- Applies to: <project/host/dialect>
- Version range: <verified>
- Source / official reference: <URL or repo path>
- Last verified: <date or UNVERIFIED>
- Intended consumers: coder / tester / both
- Load when: <scope, file extensions, task type>

## Correct API / language boundaries
<Only verified constraints; distinguish incompatible similarly named languages>

## Idioms and examples
<Verified examples; separate tested from illustrative>

## Test strategy
<How to validate in real host, integration edge cases>

## Gaps
<UNKNOWN / UNVERIFIED>

## Required verification before enabling a project-specific pack
- Confirm exact runtime/SDK and language dialect from actual code and official documentation.
- For Coder, note accepted API patterns, forbidden cross-dialect syntax, real build/debug commands and example source with provenance.
- For Tester, note fixture isolation, passing/failing cases, real-host launch requirements, regression targets and evidence capture.
- Mark pack optional when absent; reuse generic Coder/Tester investigation but never invent a host API.
- Keep selected packs referenced in `docs/PROJECT_PROFILE.md` and load only when relevant to the current task.
