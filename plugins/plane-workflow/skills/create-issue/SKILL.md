---
name: create-issue
description: Create a new Plane issue in the correct project with the correct state and any required labels. Use when the user asks to "create an issue", "file a ticket", or "add this to the backlog".
argument-hint: "[project] [title] [description] [labels]"
effort: low
---

Create a new Plane issue.

Arguments: project identifier (e.g. LAB, WQ1K), title, description, labels (optional), priority (optional - inferred if not given, see step 4).

## Steps

1. If any required input is missing, ask for it. Priority is never a blocking ask - infer it per step 4 instead. If the issue claims that a bug or gap confirmed in one repo also exists in another because they share a pattern, template or architecture, check the other repo's own current code, docs or config for that specific claim before creating the issue. A shared pattern is not evidence of a shared gap.
2. Get the project UUID for the given identifier — from a cached reference file if you keep one, or via `mcp__plane__list_projects` otherwise.
3. Get the Backlog state UUID for the project — from a cached reference file if you keep one, or via `mcp__plane__list_states` otherwise. New issues always go to Backlog, never Todo.
4. **Priority is mandatory - never leave it unset.** If the caller stated one, use it. Otherwise infer from the title/description:
   - `urgent`: active outage, data loss risk, security exposure, broken production service
   - `high`: blocks other work, a hard deadline, or a confirmed bug affecting real usage
   - `medium`: normal feature work, non-blocking bugs, most maintenance - **default when no signal points elsewhere**
   - `low`: cosmetic, nice-to-have, exploratory/research spikes with no urgency
5. Resolve the full label set **before** creating the issue: any caller-requested labels, plus any project-specific label rules your workspace has configured. Look up each label's UUID with `mcp__plane__list_labels` for the project, since `labels` takes UUIDs, not names. For example:
   | Project | Required labels |
   |---------|----------------|
   | LAB (example) | `v3` |
   | Others | as specified by caller |
6. Create issue via `mcp__plane__create_work_item` with:
   - `name`: the title
   - `description_html`: body wrapped in HTML tags (e.g. `<p>…</p>`, `<ul><li>…</li></ul>`) — Plane silently drops plain text
   - `state`: Backlog UUID
   - `priority`: from step 4
   - `labels`: the full set from step 5
7. Output issue ID, the priority that was set (flag it if inferred rather than caller-stated), and a short summary of what was created.

## Notes

- Label requirements are workspace-specific. Configure your own project label rules in your project's CLAUDE.md or equivalent.
- `description_html` must use actual HTML tags — Plane silently discards plain text passed to this field.
- **Batch callers** (e.g. `prd-to-issues`, `spike-to-issues` creating several issues in one run): resolve the project UUID, Backlog state UUID and required label UUIDs **once** yourselves, then call `mcp__plane__create_work_item` directly per issue - applying step 4's priority-inference and step 5's label rules per issue - instead of re-invoking this skill's steps 2-5 on every call, which re-resolves the same UUIDs each time.
