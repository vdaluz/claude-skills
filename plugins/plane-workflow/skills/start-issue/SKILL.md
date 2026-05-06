Start work on a Plane issue.

Arguments: issue ID (e.g. LAB-123) and optionally what we're doing today (1 sentence).

> **Issue specs are suggestions, not requirements.** Before including any file path, tool, or approach from the issue description in the plan, verify it against project conventions. Flag mismatches and propose the correct approach.

## Steps

1. If user said "new issue": create it via `mcp__plane__create_work_item` (call `mcp__plane__list_projects` to get the project UUID; set `name`, `description_html` with HTML tags — Plane silently drops plain text). Skip to step 3 after creation. Otherwise, confirm issue ID — if missing, ask.

2. Fetch issue via `mcp__plane__retrieve_work_item_by_identifier`. Check if it is a spike (title starts with "Spike:" or has a "spike" label). Summarize in 3–6 bullets: goal, current status, constraints, open questions.

3. **Rename your session.** Output a prominent labeled block with the rename command:

   > **Run this to rename your session:**
   > `/rename <ID> - <title>`

   On macOS, optionally copy to clipboard: `echo "/rename <ID> - <title>" | pbcopy`

4. Call `mcp__plane__list_states` for the project to get state UUIDs. Set status to **In Progress** via `mcp__plane__update_work_item`. Add any required labels per your project's conventions (check your project's CLAUDE.md).

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

   Then produce a short research-backed implementation plan (tasks only, no "research X" steps), risks/unknowns. Include a brief "why" for each step on learning-oriented projects.

   Wait for user "go" before touching files or running commands.

6. Once user approves the plan:
   - **Spike:** begin research. No worktree. Post findings incrementally as Plane comments. When complete, post a final findings comment and remind the user to run `/wrap-up-issue` and then `/spike-to-issues` to convert findings into implementation issues.
   - **Non-spike:** check the project `CLAUDE.md` for a "No worktrees" directive **before** calling `EnterWorktree`. If the project opts out, create a feature branch directly (`git checkout -b <issue-id>-<slug>`). Otherwise, create a worktree using `EnterWorktree` (branch named after the issue ID, e.g. `lab-571-slug`). In either case, post the plan as a Plane comment, then begin making changes.

Dual documentation: put full detail in Plane; always include a usable summary in chat.

## Optional integrations

- **cmux** (macOS terminal multiplexer): if cmux is installed and `$CMUX_SURFACE_ID` is set, the session rename can be injected directly into the terminal. This is not required — output the rename command in chat if cmux is unavailable.
