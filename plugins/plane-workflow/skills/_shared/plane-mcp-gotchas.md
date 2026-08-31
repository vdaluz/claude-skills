# Plane MCP known tool bugs

Shared by `pick-next-issue`, `reprioritize-backlog`, and `whats-next`. Read this once; each
skill only states what's specific to its own step.

## `pql`/structured filters can be entirely unsupported

Do not pass a `pql` filter to `mcp__plane__list_work_items` unless the skill step you're on
explicitly needs it - some Plane editions reject query filtering outright, with an explicit
error rather than a permissions-style failure: "PQL and structured filters are not supported
on this Plane edition. Remove the pql/filters parameter and filter results client-side..." Call
it with only `project_id`, `expand`, and an explicit `fields` list instead - filter and sort
yourself over the full result. If the trimmed result still exceeds the tool's output limit, it's
auto-saved to a file - use `jq` rather than re-requesting with filters.

## Relations calls can fail entirely, two different ways

`mcp__plane__list_work_item_relations(project_id, work_item_id)` can fail in two distinct ways,
and they need different handling:

- **A pydantic validation error** (`Input should be a valid string ... input_type=dict`) -
  per-issue, fires only when *that* issue actually has a populated relation; it may succeed
  cleanly on issues with none. One throw doesn't mean the endpoint is broken for the rest of the
  run. Don't crash on it: treat that one issue as having *unknown* relations, not zero - don't
  let it be promoted or demoted by an unverifiable "blocks N" count, and flag it explicitly in
  your output: `"<ID>: has a relation the API client can't parse (known tool bug) - position not
  dependency-aware, verify manually."`
- **An outright `HTTP 404: Not Found`** - endpoint-wide, not tied to any one issue's relation
  state; every call fails identically for the rest of the run. Don't call this per issue and let
  it fail N times: **probe once**, on the first issue in scope. If that call 404s, skip relations
  entirely for the rest of the run and fall through to whatever non-relation ordering the skill
  otherwise uses (priority/content/tie-break), noting plainly in your output that relations were
  unavailable this run. If the probe succeeds (or throws the pydantic error above, which is a
  per-issue signal, not an endpoint-down signal), keep calling it normally for the remaining
  issues.
