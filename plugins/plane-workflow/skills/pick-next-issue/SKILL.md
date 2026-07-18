---
name: pick-next-issue
description: Recommend what to work on next in a Plane project, presenting 3 ranked candidates with brief rationale instead of silently picking one. If everything actionable is Blocked, re-checks each blocker before giving up. Use when the user asks what to pick up next, wants a recommendation (not just a raw list), or runs /pick-next-issue.
---

Recommend what to work on next in a Plane project. This is the opinionated counterpart to a raw "what's next" listing (see the `whats-next` skill if you have it installed, which prints candidates with zero commentary) — this skill reads the candidates, ranks them, and presents exactly 3 with a one-line reason each, then lets the user choose. Works on any Plane project — no per-project hardcoding required in the core logic.

Arguments: project identifier — optional, auto-detected from cwd. Optional `--include-todo-only` to skip Backlog and only consider Todo (for projects where Backlog is explicitly "not yet actionable").

## Step 1 — Resolve project

If you keep a cwd-to-project shortcut table (e.g. "when cwd contains `my-app`, that's project `APP`"), try it first. Otherwise, or if it doesn't match, ask the user which project — or resolve it via `mcp__plane__list_projects` if they gave you a project name or identifier.

Get the project ID and state UUIDs (Backlog, Todo, In Progress, Blocked, Done, Cancelled) — from a cached reference file if you keep one, or via `mcp__plane__list_states` otherwise. Not every project has a state literally named "Blocked" — if none exists, skip the blocked-recovery path (Steps 4-5) entirely; there's nothing to recover.

## Step 2 — Fetch issues in scope

**Known tool bug:** do not pass `state_groups`, `priorities`, `label_ids`, or any filter param to `mcp__plane__list_work_items` — that routes through Plane's advanced-search endpoint, which can 403 depending on the API key's permissions. Call it with only `project_id`, `expand="state,labels"`, and `fields="id,sequence_id,name,priority,state,labels,target_date,created_at,description_html"` — filter to scope yourself over the full result. If the trimmed result still exceeds the tool's output limit, it's auto-saved to a file — use `jq` rather than re-requesting with filters.

Partition by state name/group:
- **In Progress** (group `started`) — already being worked; note it exists but it's not a candidate for "what's next."
- **Todo** (group `unstarted`) and **Backlog** (group `backlog`) — the candidate pool. If `--include-todo-only`, drop Backlog from the pool.
- **Blocked** (a state literally named "Blocked", if the project has one) — excluded from the candidate pool by default.

If your project uses a label or title convention to separate content backlog (blog drafts, dev logs, etc.) from actionable engineering work, exclude those the same way here — content backlog isn't "what to pick up next" for engineering work.

## Step 3 — If the candidate pool is non-empty, rank it

1. **Cheap objective triage first**, to cut a possibly-large pool down to a shortlist before reading anything in full:
   - Priority weight: `urgent`=4, `high`=3, `medium`=2, `low`=1, `none`=0.
   - Overdue/due-soon bump: any candidate with `target_date` on or before today (or within a few days) gets an urgency bump — this covers recurring/rolling-style issues even where the project doesn't use that exact label.
   - Best-effort blocking leverage: for the top ~15 by the above, call `mcp__plane__list_work_item_relations(project_id, work_item_id)` and note how many other in-scope issues each one blocks. **Known tool bug:** this call can throw a pydantic validation error (`Input should be a valid string ... input_type=dict`) whenever the issue actually *has* a populated relation — it may only succeed cleanly when there are none. Do not crash on this; treat it as "relation data unavailable for leverage scoring, not zero leverage" and don't penalize the issue for it.
   - Take the top 6-10 by this cheap score as the shortlist.
2. **Read the shortlist for real** — full `description_html`, AND `mcp__plane__list_work_item_comments` for every single shortlisted candidate, no exceptions. Skipping the comments call is a common way to produce a wrong rationale: a description can cite something (a bug, a blocker) that a later comment already resolved or marked out of scope. A description can be stale in a way only the comments reveal — do not treat "read the shortlist" as description-only. If you catch yourself about to present options without having called this for every one of the 3, stop and do it first. Also skim any project notes/memory you keep for this project — they often carry live context (an active initiative, a current deadline, a "this is the flagship feature" note) that changes what "makes sense next" means beyond raw priority. This step is what makes the recommendation actually good instead of a mechanical sort — use judgment, the same kind a competent engineer would use picking their own next task:
   - Concrete and well-scoped beats vague and open-ended ("fix this specific null check" beats "improve the UX, make sure it's good").
   - A correctness bug in something load-bearing outranks a cosmetic issue or a nice-to-have feature, all else equal.
   - An issue that unblocks several others (from the leverage check) outranks one that unblocks nothing.
   - Live project context matters — if your notes say something is the active/current focus, work that touches it ranks higher than equally-priority-tagged work that doesn't.
   - Don't present 3 near-duplicates (e.g. three cosmetic label-overlap bugs) if the shortlist has more variety than that — favor a set that gives the user a real choice.
3. Select exactly 3. For each, write a **brief** rationale (1-2 sentences, concrete — cite something from the actual issue, not a generic "this seems important") explaining why it's a reasonable next pick, and how it compares to the others if relevant.

Skip to Step 6.

## Step 4 — If the candidate pool is empty, don't just report zero

Before concluding there's nothing to work on:

1. Fetch every issue in the Blocked state (if one exists — see Step 1).
2. For each, try to establish what's actually blocking it, in this order:
   - **Formal relations**: `mcp__plane__list_work_item_relations`, same bug-handling as Step 3. If it returns a `blocked_by` list, resolve each blocker's current state via the state data you already fetched (or `mcp__plane__retrieve_work_item` if it's outside the original fetch, possibly in a different project).
   - **Stated blocker in comments**: `mcp__plane__list_work_item_comments` — a Blocked issue should ideally have a comment noting the specific blocker, which is often the *only* record for a human-action block (nothing to query — Plane has no relation for "waiting on a person"). Read the most recent comments for language like "blocked on", "waiting on", "needs X before".
3. Classify each Blocked issue:
   - **Blocker resolved** (the blocking issue is now Done/Cancelled, or the comment's blocker condition reads as satisfied given current context): this issue is **actually unblocked now** — pull it into the candidate pool for Step 3's ranking, and flag clearly in the final output that it was reclassified (its Plane state still says Blocked until the user or a start-work step moves it — don't silently change state yourself here).
   - **Still blocked on another open issue**: note the blocking issue's ID, title, and state plainly.
   - **Still blocked on a human action** (comment reads as needing the user): note what the user specifically needs to do, as stated in the comment — don't paraphrase it into something vaguer.
4. If step 3 surfaced one or more now-unblocked issues, continue to Step 3's ranking using just those (skip re-running the cheap triage over the whole Blocked set — you already have what you need from the comment/relation read).
5. If nothing is actually unblocked: **do not present 3 options** — there's nothing legitimate to choose from. Report plainly instead: a table of every Blocked issue with what specifically is blocking it (issue ID+title+state, or the human action needed), so the user knows exactly what to go unblock. This is a valid, useful stopping point, not a failure to route around.

## Step 5 — (only reached via Step 4) present the reclassified candidates

Same as Step 3.2-3.3, but explicitly note for each option that it was found sitting in Blocked with a since-resolved blocker — don't bury that fact, the user should know their tracker is stale here.

## Step 6 — Present exactly 3 options and get the user's pick

Use `AskUserQuestion` with the 3 ranked candidates as options (label = `<ID>: <short title>`, description = the brief rationale). The tool always offers an "Other" fallback automatically, so the user can reject all 3 without needing a 4th option from you.

Do not add editorializing beyond the per-option rationale — no "I'd go with the first one" unless explicitly asked. Three good options with honest tradeoffs is the deliverable; the choice is the user's.

## Step 7 — Hand off

Once the user picks one (from the 3, or names something else via Other), begin work on it per your project's normal issue-start process (a dedicated start-issue skill if you have one, or setting it In Progress and planning manually otherwise). If they picked an issue that Step 4 identified as reclassified-from-Blocked, mention that starting it will move it out of Blocked as part of setting it In Progress — no separate state-fix step needed.

If the user declines to pick anything (wants to keep browsing, or the Step 4 blocked-report was the actual answer they needed), stop here — don't force a selection.
