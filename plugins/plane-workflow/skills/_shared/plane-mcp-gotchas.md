# Plane MCP known tool bugs

Shared by `pick-next-issue`, `reprioritize-backlog`, and `whats-next`. Read this once; each
skill only states what's specific to its own step.

## Structured filters can 403

Do not pass `state_groups`, `priorities`, `label_ids`, or any filter param to
`mcp__plane__list_work_items` - that routes through Plane's advanced-search endpoint, which can
403 depending on the API key's permissions. Call it with only `project_id`, `expand`, and an
explicit `fields` list - filter and sort yourself over the full result. If the trimmed result
still exceeds the tool's output limit, it's auto-saved to a file - use `jq` rather than
re-requesting with filters.

## Relations calls can throw on a populated relation

`mcp__plane__list_work_item_relations(project_id, work_item_id)` can throw a pydantic validation
error (`Input should be a valid string ... input_type=dict`) whenever the issue actually *has* a
populated relation - it may only succeed cleanly when there are none. Do not crash on this; treat
it as "relation data unavailable for leverage scoring, not zero leverage" and don't penalize the
issue for it. If you hit this and can't find a working fallback in your Plane MCP server's docs,
treat the issue as having no *known* edges for graph purposes (don't let it be promoted by an
unverifiable "blocks N" count, and don't demote it either), and flag it explicitly in your output:
`"<ID>: has a relation the API client can't parse (known tool bug) - position not dependency-aware, verify manually."`
