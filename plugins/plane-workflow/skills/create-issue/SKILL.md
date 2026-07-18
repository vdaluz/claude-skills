---
name: create-issue
description: Create a new Plane issue in the correct project with the correct state and any required labels. Use when the user asks to "create an issue", "file a ticket", or "add this to the backlog". Always creates in Backlog, never Todo; project-specific label rules (if any) are workspace-configured, not built in.
---

Create a new Plane issue.

Arguments: project identifier (e.g. LAB, WQ1K), title, description, labels (optional).

## Steps

1. If any required input is missing, ask for it.
2. Call `mcp__plane__list_projects` to get the project UUID for the given identifier.
3. Call `mcp__plane__list_states` for the project and find the Backlog state UUID — new issues always go to Backlog, never Todo.
4. Create issue via `mcp__plane__create_work_item` with:
   - `name`: the title
   - `description_html`: body wrapped in HTML tags (e.g. `<p>…</p>`, `<ul><li>…</li></ul>`) — Plane silently drops plain text
   - `state`: Backlog UUID
   - `labels`: any requested labels
5. Apply any project-specific label rules your workspace has configured. For example:
   | Project | Required labels |
   |---------|----------------|
   | LAB (example) | `v3` |
   | Others | as specified by caller |
6. Output issue ID and a short summary of what was created.

## Notes

- Label requirements are workspace-specific. Configure your own project label rules in your project's CLAUDE.md or equivalent.
- `description_html` must use actual HTML tags — Plane silently discards plain text passed to this field.
