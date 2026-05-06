Resume work on a Plane issue from a previous session.

Arguments: issue ID (optional) and what to do next (1 sentence).

## Steps

1. **Resolve the issue**: Use provided ID, or search codebase for project identifiers (e.g. LAB-, WQ1K-), or ask.

2. **Pull context from Plane** (not from chat history — there is none across sessions):
   - Open issue via `mcp__plane__retrieve_work_item_by_identifier`
   - Read all issue comments via `mcp__plane__list_work_item_comments` to reconstruct what was done, decisions made, current state, and any open blockers
   - Summarize: what's been completed, what's open, any blockers

3. **Set In Progress** if not already: call `mcp__plane__list_states` for the project to get the In Progress state UUID, then update via `mcp__plane__update_work_item`.

4. **Check codebase state**: Read relevant state files, configs, or code to verify what was actually deployed (don't rely only on Plane comments — the codebase is ground truth).

5. **Check for an existing worktree**: if one exists for this issue branch (e.g. `lab-123-title`), use `EnterWorktree` to resume inside it. If not, create one with `EnterWorktree` before making any changes.

6. **Identify next atomic step**: one action, which files/areas, how to verify it. For learning-oriented projects, explain why this step is needed, not just what it is. Do not implement unless the user says to.

Put a context-rehydration summary in Plane comment if the issue was stale; always include a usable summary in chat.
