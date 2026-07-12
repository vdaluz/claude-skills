---
name: research
description: Research a topic across in-repo docs, official documentation, and communities, with a mandatory hard-requirements gate before recommending anything. Use when the user asks to research, evaluate, compare, or choose between tools/approaches/services, or wants sourced findings on a topic. Always cites sources and calls advisor() before delivering results; does not implement changes.
---

Research a topic across in-repo docs, official documentation, and communities.

Arguments: topic/question, issue ID (optional — defaults to active issue), constraints/scope.

## Steps

**1. Scope and topic**

Use provided issue ID, or detect from recent conversation (MCP calls, issue mentions). Derive topic from issue name/description if not given.

**2. Research in this order**

- **In-repo first**: CLAUDE.md files (authoritative project rules), README, docs/, runbooks/, state files, referenced configs, existing playbooks/scripts (check if a solution already exists)
- **Official docs**: vendor/project documentation for the relevant tools — always check version-specific docs
- **Communities**: Reddit, GitHub discussions/issues, forums — prefer practical operator experience over theory

**3. Sources**

Cite URLs for every claim and recommendation. If something is opinion or inference, say so explicitly. Never present findings without sources.

**4. Output**

- **Issue tracker comment** (full detail): findings (bullets), options with pros/cons, recommendation with rationale, risks/unknowns, all sources. Post via `mcp__plane__create_work_item_comment` if Plane MCP is available.
- **Chat summary** (5–10 bullets): decision/recommendation, key evidence, next step — usable without opening the issue tracker.

**5. No implementation**

Do not implement changes unless the user explicitly asks.
