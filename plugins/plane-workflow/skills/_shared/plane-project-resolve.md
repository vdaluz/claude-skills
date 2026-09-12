# Resolving the project and its state UUIDs

Shared by `whats-next`, `reprioritize-backlog`, and `pick-next-issue`. Read this once; each
skill only states its own project-identifier argument and which state UUIDs it needs.

If you keep a cwd-to-project shortcut table, try it first. Otherwise ask which project, or
resolve it via `mcp__plane__list_projects`.

Get the project ID and the state UUIDs this skill needs — from a cached reference file if you
keep one, or via `mcp__plane__list_states` otherwise.

## Priority weight

Canonical urgency ranking used by any skill that needs to rank issues by priority:
`urgent`=4, `high`=3, `medium`=2, `low`=1, `none`/unset=0. Higher number means more urgent.
