---
name: wrap-up-issue
description: Wrap up and close a Plane issue by verifying work, writing a blog draft, routing KB-worthy findings, committing, merging to main, deleting the branch, and setting Done. Use when the user asks to "wrap up", "close out", or "finish" a Plane issue, or after implementation work is verified and ready to land. Never invoked manually mid-task; this is the only path that should merge or close an issue.
---

Wrap up and close a Plane issue.

Arguments: issue ID (optional — auto-detect from conversation context) and what "done" means (1–2 bullets).

Steps:
1. Auto-detect issue ID from conversation (recent MCP calls, issue mentions, codebase grep for LAB-/WQ1K-/BLG-). If not found, ask.
2. Open issue via `mcp__plane__retrieve_work_item_by_identifier`. Check if it is a spike (title starts with "Spike:" or has a "spike" label). Determine project and any closeout requirements from project rules.
3. **If the issue is a spike:**
   - Validate that a findings comment has been posted to the issue (check comments via `mcp__plane__list_work_item_comments`). If not, write and post one now: what was tested, what was discovered, what the recommendation/decision is, any blockers or caveats.
   - **Present the full findings in chat.** Reproduce the key content inline — recommendation, service matrix, major gotchas, phases. Do NOT just say "see Plane". The user must be able to read and judge the findings without leaving the conversation.
   - **Hard gate: wait for explicit user approval before proceeding.** Ask "Do you approve these findings? Any changes before I close the spike?" Do not mark Done, run whats-next, or remind about /spike-to-issues until the user explicitly approves (e.g. "looks good", "approved", "yes", "close it").
   - Once approved: remind the user to run `/spike-to-issues <issue-ID>` to convert findings into implementation issues.
   - Skip git steps (spikes produce no code changes).
   - Skip blog draft question.
   - Set issue to **Done**.
   **If the issue is not a spike:** continue with steps below.
4. Validate ready:
   - Workflow steps complete
   - Verification done with evidence (two-level: system + user-facing)
   - **If this is a blog draft issue** (has your project's "Blog Draft" label) **AND a file was written to `src/content/blog/`** (flat, or `src/content/blog/en/` for an i18n-enabled blog — see `_shared/blog-locale-layout.md`)**:** STOP before step 7. Run `/fact-check-article` against the English file, post the results, then ask: "Review the fact-check report above and reply **'pass'** to proceed with commit/push, or describe any corrections needed." Do NOT commit, push, or mark Done until the user explicitly says pass/go/looks good/approved. A clean automated result (0 FAIL) does NOT count as approval — only an explicit user message does. This is a hard gate — bypassing it by calling wrap-up-issue directly does not exempt the fact-check.
   - Blog draft step satisfied (for non-blog-draft issues): always write a blog draft unless the user explicitly said not to. Write it **inline in the conversation** (do NOT invoke `/draft-article`, `/publish-article`, or any file-write to a repo). Post the draft as a comment on a new Plane issue. **The new issue must always be created in the Backlog with no due date** — leave `target_date` unset (null). Scheduling is the job of your blog-backlog-processing skill, if you have one, never issue creation.
     - **If your setup routes blog drafts to different projects by source** (e.g. software/dev-log projects go to a dev-log blog, general/infra projects go to a personal blog project), apply that routing here — get project/state/label IDs via `mcp__plane__list_projects`/`mcp__plane__list_labels`, or from a cached reference file if you keep one (see `reference_plane_ids.md` pattern referenced elsewhere in this plugin). This skill ships without a specific routing table; define your own project's convention in that project's `CLAUDE.md` and follow it here.
5. **KB routing check** — before writing the Plane comment, ask: did this issue produce anything worth persisting beyond the issue itself?

   | Goes to **Plane only** | Goes to **KB** (also post in Plane as reference) |
   |---|---|
   | Task-specific decisions and evidence | Infrastructure gotchas not derivable from code/state |
   | One-time investigation steps and results | Recurring patterns or known failure modes |
   | "We did X, here's proof" | "Anyone touching this service needs to know Y" |
   | Issue-scoped debugging steps | Decisions whose rationale will matter in 6 months |

   If KB-worthy: write to `~/Repos/vdaluz-kb/` (use the correct subfolder — `infrastructure/`, `patterns/`, or `alerts/` — and include frontmatter with `projects: [homelab-v3]`; see KB format in `fact-check-article` step 7 for infrastructure notes, or `review-alerts` step 4 for alert findings). Then reference the file in the Plane comment and commit+push: `git -C ~/Repos/vdaluz-kb add <file> && git -C ~/Repos/vdaluz-kb commit -m "kb: <topic> (LAB-XXX)" && git -C ~/Repos/vdaluz-kb push`.

   > **Legacy path note:** Any skill/doc referencing `homelab-v3/knowledge/` resolves to `~/Repos/vdaluz-kb/` with the same subpath.

6. Draft final Plane comment: summary of what was done, evidence, KB files written (if any), optional next step. Post via `mcp__plane__create_work_item_comment`.
7. **Commit and land on `main`.**
   - **If you're already directly on `main`** (the new default): `git status` for uncommitted changes, stage relevant files, commit with a message referencing the issue ID, then `git push origin main`.
   - **If this issue used a worktree or branch:** commit there, rebase onto latest main so the merge can fast-forward, then fast-forward-merge and push. Exact commands, the vault merge-conflict handling, and worktree/branch cleanup (**mandatory, do not skip or leave for the user**): `_shared/git-isolation.md`.
   - **CI gate (either path):** run `gh run list --branch main -L 1` — if `conclusion` is `failure`, stop and surface the failing run URL per CLAUDE.md §CI. Only proceed once CI is green (or the user gives explicit approval).
8. **If a worktree or branch was used, clean it up now (mandatory)** — worktree removal and branch deletion (local + remote) steps are in `_shared/git-isolation.md`. Confirm `git worktree list` / `git branch -a` show it's gone before proceeding. Skip entirely if you worked directly on `main`.
9. **Close the task list (mandatory).** Use `TaskList` to fetch all tasks for this session. Mark every open task as `completed` or `cancelled` via `TaskUpdate` — no task should remain `pending` or `in_progress` after wrap-up. If a task was genuinely not completed (deferred to a future issue), mark it `cancelled` and note the follow-up issue ID. Never leave a dangling open task list.
10. Set issue to **Done** via `mcp__plane__update_work_item` (get state UUID from memory `reference_plane_ids.md` — only call `mcp__plane__list_states` if the project isn't cached there). Only skip Done if user explicitly said to keep the issue open. **If `write-article` already set Done** after a blog push to `main`, re-fetch the issue and **skip** this step if state is already Done.
11. **Refresh backlog memory and show what's next (mandatory).**
   - Invoke the `whats-next` skill for the same project (e.g. LAB). This makes fresh Plane calls and produces the formatted Todo / Backlog / Blocked output.
   - After the output is ready, overwrite `~/.claude/projects/-Users-vic-Repos-<project>/memory/project_backlog.md` with the full list in the same format as the existing file: today's date in "Last updated:", one bullet per issue under each section header, section counts updated. Mark it "orientation only — run /whats-next to confirm before starting work."
   - Display the `whats-next` output **verbatim** in chat — the exact Todo/Backlog/Blocked list the tool printed, nothing added. **Do NOT** regroup by theme, summarize, prioritize, recommend which issue to pick next, or wrap it in narrative ("Where things stand", "splits into themes", etc.). The `whats-next` skill's rule — "print stdout verbatim, no commentary/recommendation/opinion" — applies here too, even when you run `plane-api` directly instead of invoking the skill. This raw list is the "what's available" view; the issue-wrap summary (line below) is the only place for findings/decisions — keep the two separate.

Always include a usable summary in chat (findings, decisions, any follow-up items).
