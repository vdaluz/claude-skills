---
name: research
description: Research a topic across in-repo docs, official documentation, and communities, with a mandatory hard-requirements gate before recommending anything. Use when the user asks to research, evaluate, compare, or choose between tools/approaches/services, or wants sourced findings on a topic. Always cites sources; does not implement changes.
---

Research a topic across in-repo docs, official documentation, and communities.

Arguments: topic/question, issue ID (optional — defaults to active issue), constraints/scope.

## Steps

**0. Hard-requirements gate (BLOCKING — do this before anything else).**

Before any searching, shortlisting, evaluation, or recommendation, make the user's **hard requirements / dealbreakers explicit and confirmed**. This applies whenever the task is to evaluate, compare, choose, or recommend a tool / approach / service — *and* whenever it's to research how to use or onboard one (a tool you can't actually use for its core purpose is the wrong tool, no matter how good the onboarding research is).

- List what would **disqualify** a candidate, and get the user to confirm that list — ask via `AskUserQuestion` BEFORE researching, not after. Do not start until the list is pinned.
- During research, verify **each hard requirement against a PRIMARY source** (official docs / source / API), per candidate. A single unmet hard requirement **disqualifies** the candidate — report it as a flat "no", never soften a dealbreaker into a caveat, a footnote, or "almost certainly".
- The failure this gate exists to prevent: validating the easy, mechanical part ("how do I use X") while skipping the dealbreaker ("can X even do the thing I need"). Check the dealbreaker first.

**1. Scope and topic**

Use provided issue ID, or detect from recent conversation (MCP calls, issue mentions). Derive topic from issue name/description if not given.

**2. Research in this order**

- **In-repo first**: CLAUDE.md files (authoritative project rules), README, docs/, runbooks/, state files, referenced configs, existing playbooks/scripts (check if a solution already exists)
- **Official docs**: vendor/project documentation for the relevant tools — always check version-specific docs
- **Communities**: Reddit, GitHub discussions/issues, forums — prefer practical operator experience over theory

**3. Sources**

Cite URLs for every claim and recommendation. If something is opinion or inference, say so explicitly. Never present findings without sources.

**4. Advisor review (optional)**

If your environment has an advisor-style second-opinion tool available, call it before delivering results — it can catch missed sources, weak reasoning, or conclusions that outrun the evidence. Skip this step if no such tool is available; it's not required to complete the research.

**5. Output**

- **Issue tracker comment** (full detail): findings (bullets), options with pros/cons, recommendation with rationale, risks/unknowns, all sources. Post via `mcp__plane__create_work_item_comment` if Plane MCP is available.
- **Chat summary** (5–10 bullets): decision/recommendation, key evidence, next step — usable without opening the issue tracker.

**6. No implementation**

Do not implement changes unless the user explicitly asks.
