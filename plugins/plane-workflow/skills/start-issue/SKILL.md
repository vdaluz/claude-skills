---
name: start-issue
description: Start work on a Plane issue, fetching context, setting In Progress, and producing a research-backed plan. Use when the user asks to "start issue X", "begin work on LAB-123", or gives an issue ID to work on. Never edits files or runs commands before the user says "go" on the plan.
---

Start work on a Plane issue.

Arguments: issue ID (e.g. LAB-123) and optionally what we're doing today (1 sentence).

> **Issue specs are suggestions, not requirements.** Before including any file path, tool, or approach from the issue description in the plan, verify it against your project's actual conventions. Example: a script meant to run on a remote host might belong in an existing automation framework (an Ansible role, a deploy script) rather than a loose one-off; a new service might belong in a tracked config file rather than hardcoded inline. Flag mismatches against what the project actually does and propose the correct approach.

Steps:
1. If user said "new issue": create it via `mcp__plane__create_work_item` (get the project ID from a cached reference file if you keep one, or via `mcp__plane__list_projects` otherwise; set `name`, `description_html` with HTML tags — Plane silently drops plain text; `priority` is mandatory, infer it per `create-issue`'s step 4 if the user didn't state one). Skip to step 3 after creation. Otherwise, confirm issue ID — if missing, ask.

2. Fetch issue via `mcp__plane__retrieve_work_item_by_identifier`. **ALWAYS also read the issue's own comments** via `mcp__plane__list_work_item_comments` — never the description alone. Comments routinely carry prior-session notes, decisions, status changes, and blockers ("scan already done", "blocked on X") that the description does not. Check if it is a spike (title starts with "Spike:" or has a "spike" label). Summarize in 3–6 bullets: goal, current status (incl. anything from comments), constraints, open questions.

3. **Rename the session.** On macOS, `echo "/rename <ID> - <title>" | pbcopy` copies the rename command to the clipboard (swap in your platform's clipboard tool, or skip it — copying is a convenience, not a requirement). Output the session rename command as a **prominent labeled block** either way — never inline or buried in prose:

   > **Run this to rename your session:**
   > `/rename <ID> - <title>`

   Do not skip or defer this step. Do not proceed to planning before this block appears in the response.

4. Get state UUIDs (from a cached reference file if you keep one, or via `mcp__plane__list_states` otherwise). Set status to **In Progress** via `mcp__plane__update_work_item`. Add required labels if your project has any (e.g. a label your team always applies to a given issue type) — check project-specific label rules in the project's `CLAUDE.md`.

5. Research and plan:

   ### Spike path
   Produce a research plan — what to test, what docs/APIs to read, what questions to answer, and what the done criteria are (findings documented in a Plane comment). No worktree. No code changes expected.

   **Always include "is it worth it?" as an explicit research question.** Cover cost/benefit and alternatives — not just how to implement. Spike findings must state a clear recommendation: *do it / do it differently / don't do it*, with rationale. A spike that concludes "don't build this" is a success.

   Wait for user "go".

   ### Non-spike path
   BEFORE writing the plan, do actual research:
   - Fetch every reference link in the issue description (WebFetch)
   - Run WebSearch if the issue mentions research, evaluation, or alternatives
   - Cite sources in the plan (e.g. "per official docs at X…")

   Then produce a short research-backed implementation plan (tasks only, no "research X" steps), risks/unknowns. For learning-oriented projects, include a brief "why" for each step. If the issue is a service deployment and your project has a deployment checklist skill or doc, use it as a mandatory checklist. For complex or infrastructure-changing plans, suggest running a review/roast pass before proceeding.

   **If the issue touches UI** (pages under `src/pages/`, components, layouts, styles, or markdown that ships HTML): include an a11y verification item in the done-criteria — run `npm run a11y` locally (or check with the browser axe DevTools extension on changed pages) and record the result in the Plane wrap-up comment.

   Wait for user "go" before touching files or running commands.

6. Once user approves the plan:
   - **Spike:** begin research. No worktree. Post findings incrementally as Plane comments. When complete, post a final findings comment and remind the user to close out the spike (mark it Done, and if your workflow converts findings into follow-up issues, do that next) and then run `/spike-to-issues` to convert findings into implementation issues.
   - **Non-spike — work directly on `main` by default**, isolating only when this session genuinely needs it. Decision rule, worktree/branch creation, and the vault merge-conflict note: `_shared/git-isolation.md`.

     In all cases, post the plan as a Plane comment, then begin making changes.

     **When implementation is complete and verified: commit, merge, and close out the issue per your project's own wrap-up process** (a dedicated wrap-up skill if you have one, or your normal commit/merge/close routine otherwise). Don't skip this step — it's easy to leave an issue open after the code lands.

Dual documentation: put full detail in Plane; always include a usable summary in chat.
