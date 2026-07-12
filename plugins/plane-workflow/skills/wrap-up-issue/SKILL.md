---
name: wrap-up-issue
description: Wrap up and close a Plane issue by verifying work, writing a blog draft, routing KB-worthy findings, committing, merging to main, deleting the branch, and setting Done. Use when the user asks to "wrap up", "close out", or "finish" a Plane issue, or after implementation work is verified and ready to land. Never invoked manually mid-task; this is the only path that should merge or close an issue.
---

Wrap up and close a Plane issue.

Arguments: issue ID (optional — auto-detect from conversation context) and what "done" means (1–2 bullets).

## Steps

1. Auto-detect issue ID from conversation (recent MCP calls, issue mentions, codebase grep for project identifiers). If not found, ask.
2. Open issue via `mcp__plane__retrieve_work_item_by_identifier`. Check if it is a spike (title starts with "Spike:" or has a "spike" label). Determine project and any closeout requirements from project rules.
3. **If the issue is a spike:**
   - Validate that a findings comment has been posted to the issue (check comments via `mcp__plane__list_work_item_comments`). If not, write and post one now: what was tested, what was discovered, what the recommendation/decision is, any blockers or caveats.
   - Skip git steps (spikes produce no code changes).
   - Remind the user to run `/spike-to-issues <issue-ID>` to convert findings into implementation issues before marking Done.
   - Set issue to **Done**.

   **If the issue is not a spike:** continue with steps below.

4. Validate ready:
   - Workflow steps complete
   - Verification done with evidence (two-level: system + user-facing)

5. **Persist valuable findings** — ask: did this issue produce anything worth keeping beyond the issue itself?

   | Put in **Plane comment only** | Worth persisting elsewhere |
   |---|---|
   | Task-specific decisions and evidence | Infrastructure gotchas not derivable from code/state |
   | One-time investigation steps | Recurring patterns or known failure modes |
   | "We did X, here's proof" | Decisions whose rationale will matter in 6 months |

   If worth persisting: write findings to your preferred notes location (local KB, wiki, docs directory, etc.) and reference it in the Plane comment.

6. Draft final Plane comment: summary of what was done, evidence, any notes written, optional next step. Post via `mcp__plane__create_work_item_comment`.

7. Commit and push all changes: check `git status` for any uncommitted changes in both the main repo and the worktree (if one was used). Stage relevant files, write a concise commit message referencing the issue ID. **Before pushing**, run `gh run list --branch main -L 1` — if `conclusion` is `failure`, stop and surface the failing run URL to the user. Only push once CI is green (or user gives explicit approval).

8. Clean up the worktree if one was used: run `ExitWorktree` (or `git worktree remove <path>` if the tool is unavailable). Confirm the worktree is removed before proceeding.

9. **Delete the feature branch (mandatory).** Delete both local and remote:
   ```bash
   git branch -d <branch>
   git push origin --delete <branch>
   git fetch --prune
   ```
   Confirm `git branch -a` shows only `main` (and `origin/main`). If the branch no longer exists on the remote (already auto-deleted), skip the remote delete — but always delete the local branch.

10. **Close the task list (mandatory).** Use `TaskList` to fetch all tasks for this session. Mark every open task as `completed` or `cancelled` via `TaskUpdate`. If a task was genuinely not completed (deferred to a future issue), mark it `cancelled` and note the follow-up issue ID.

11. Call `mcp__plane__list_states` for the project to get the Done state UUID. Set issue to **Done** via `mcp__plane__update_work_item`. Only skip Done if user explicitly said to keep the issue open.

Always include a usable summary in chat (findings, decisions, any follow-up items).
