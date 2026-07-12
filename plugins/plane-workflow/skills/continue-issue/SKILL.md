---
name: continue-issue
description: Resume work on a Plane issue from a previous session by rebuilding context from Plane comments and codebase state, not chat history. Use when the user asks to "continue issue X", "pick this back up", or resumes a session on a previously-started LAB/VDA/etc. issue.
---

Resume work on a Plane issue from a previous session.

Arguments: issue ID (optional) and what to do next (1 sentence).

Steps:

1. **Resolve the issue**: Use provided ID, or search codebase for LAB-/WQ1K- identifiers, or ask.

2. **Pull context from Plane** (not from chat history — there is none across sessions):
   - Open issue via `mcp__plane__retrieve_work_item_by_identifier`
   - Read all issue comments via `mcp__plane__list_work_item_comments` to reconstruct what was done, decisions made, current state, and any open blockers
   - Summarize: what's been completed, what's open, any blockers

3. **Set In Progress** if not already: get state UUIDs from memory `reference_plane_ids.md` (only call `mcp__plane__list_states` if not cached), update via `mcp__plane__update_work_item`.

4. **Check codebase state**: Read relevant state files, configs, or code to verify what was actually deployed (don't rely only on Plane comments — the codebase is ground truth).

5. **Resume directly on `main` by default.** Isolation is opt-in now, not mandatory. Resuming an existing worktree/branch, creating one if this session genuinely needs isolation, the pre-edit rebase, and the vault merge-conflict note: `_shared/git-isolation.md`.

6. **Identify next atomic step**: one action, which files/areas, how to verify it. For learning-oriented projects (e.g. LAB), explain why this step is needed, not just what it is. Do not implement unless the user says to.

Put a context-rehydration summary in Plane comment if the issue was stale; always include a usable summary in chat.
