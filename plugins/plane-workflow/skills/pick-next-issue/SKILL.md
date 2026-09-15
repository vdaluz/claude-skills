---
name: pick-next-issue
description: Recommend what to work on next in a Plane project, presenting up to 4 ranked candidates with brief rationale instead of silently picking one. Use when the user asks what to pick up next, wants a recommendation, or runs /pick-next-issue.
argument-hint: "[project] [--include-todo-only]"
---

Recommend what to work on next in a Plane project. This is the opinionated counterpart to a raw "what's next" listing (see the `whats-next` skill if you have it installed, which prints candidates with zero commentary) — this skill reads the candidates, ranks them, and presents up to 4 with a one-line reason each (fewer plus an explicit option to stop the session, if the pool is thin), then lets the user choose. Works on any Plane project — no per-project hardcoding required in the core logic.

Arguments: project identifier — optional, auto-detected from cwd. Optional `--include-todo-only` to skip Backlog and only consider Todo (for projects where Backlog is explicitly "not yet actionable").

## Step 1 — Resolve project

Resolve the project and its state UUIDs (Backlog, Todo, In Progress, Blocked, Done, Cancelled)
per `${CLAUDE_PLUGIN_ROOT}/skills/_shared/plane-project-resolve.md`. Not every project has a
state literally named "Blocked" — if none exists, skip the blocked-recovery path (Step 3)
entirely; there's nothing to recover.

## Step 2 — Fetch issues in scope

See `${CLAUDE_PLUGIN_ROOT}/skills/_shared/plane-mcp-gotchas.md` ("`pql`/structured filters can be entirely unsupported") before calling `mcp__plane__list_work_items` - call it with only `project_id`, `expand="state,labels"`, and `fields="id,sequence_id,name,priority,state,labels,target_date,created_at,description_html"`.

Partition by state name/group:
- **In Progress** (group `started`) — already being worked; note it exists but it's not a candidate for "what's next."
- **Todo** (group `unstarted`) and **Backlog** (group `backlog`) — the base candidate pool. If `--include-todo-only`, drop Backlog from the pool.
- **Blocked** (a state literally named "Blocked", if the project has one) — not in the base pool, but re-checked in Step 3 below when the base pool is thin (fewer than 4 legitimate candidates), and merged in if a blocker has actually resolved.

If your project uses a label or title convention to separate content backlog (blog drafts, dev logs, etc.) from actionable engineering work, exclude those from the candidate pool the same way — content backlog isn't "what to pick up next" for engineering work.

## Step 3 — Re-check Blocked issues when the base pool is thin

Run this when the base pool (Todo + Backlog) has fewer than 4 legitimate candidates — empty or thin both count. Skip this step when the base pool already has 4 or more good candidates: there's already enough to work with, and checking Blocked issues would spend relations/comments calls without being likely to change what gets presented. Also skip if the project has no state literally named "Blocked" (see Step 1).

1. Use the Blocked list Step 2 already fetched — no separate call needed.
2. For each, try to establish what's actually blocking it, in this order:
   - **Formal relations**: `mcp__plane__list_work_item_relations`, probing once on the first Blocked issue the same way as Step 4's leverage check (skip the rest of this loop on a 404, keep going per-issue on a pydantic validation error - see `${CLAUDE_PLUGIN_ROOT}/skills/_shared/plane-mcp-gotchas.md`). If it returns a `blocked_by` list, resolve each blocker's current state via the state data you already fetched (or `mcp__plane__retrieve_work_item` if it's outside the original fetch, possibly in a different project).
   - **Stated blocker in comments**: `mcp__plane__list_work_item_comments` — a Blocked issue should ideally have a comment noting the specific blocker, which is often the *only* record for a human-action block (nothing to query — Plane has no relation for "waiting on a person"). Read the most recent comments for language like "blocked on", "waiting on", "needs X before".
3. Classify each Blocked issue:
   - **Blocker resolved** (the blocking issue is now Done/Cancelled, or the comment's blocker condition reads as satisfied given current context): this issue is **actually unblocked now** — merge it into the candidate pool for Step 4's ranking alongside Todo/Backlog, and flag clearly in the final output that it was reclassified (its Plane state still says Blocked until the user or a start-work step moves it — don't silently change state yourself here).
   - **Still blocked on another open issue**: note the blocking issue's ID, title, and state plainly.
   - **Still blocked on a human action** (comment reads as needing the user): note what the user specifically needs to do, as stated in the comment — don't paraphrase it into something vaguer. Do not merge these into the candidate pool just because the base pool is thin; a human-action block doesn't resolve itself by being re-read.

**Don't stop at reporting the blocker table — if your project has a convention for proactively helping with a blocked issue's next unblock step, apply it here, not just when the user separately asks later.** Identify the highest-priority issue among the still-blocked set and, for that one specifically, state the concrete next unblock action and offer to walk through it live right now, in the same message as the blocker table — not deferred to a follow-up the user has to ask for. Lower-priority Blocked issues can stay as a plain table entry.

If the merged pool (base pool + any reclassified Blocked issues) ends up empty, don't just report zero — report plainly first: a table of every Blocked issue with what specifically is blocking it, so the user knows exactly what to go unblock. Then use `AskUserQuestion` with two options: the proactive top-priority unblock offer above (walk through it now), and "Stop here for now" (nothing else is actionable right now). This is a valid, useful stopping point, not a failure to route around. Skip Step 4 in that case.

## Step 4 — Rank the merged candidate pool

1. **Cheap objective triage first**, to cut a possibly-large pool down to a shortlist before reading anything in full:
   - Priority weight: per `${CLAUDE_PLUGIN_ROOT}/skills/_shared/plane-project-resolve.md`'s Priority weight section (`urgent`=4 … `none`=0).
   - Overdue/due-soon bump: any candidate with `target_date` on or before today (or within a few days) gets an urgency bump.
   - Best-effort blocking leverage: for the top ~15 by the above, probe `mcp__plane__list_work_item_relations(project_id, work_item_id)` once on the first candidate. If that call 404s, skip the leverage check entirely for the rest of the run (relations unavailable this run - unknown leverage, not zero). Otherwise call it for each of the ~15 and note how many other in-scope issues each one blocks, treating any individual pydantic-validation-error issue as unknown leverage rather than skipping the rest. See `${CLAUDE_PLUGIN_ROOT}/skills/_shared/plane-mcp-gotchas.md` ("Relations calls can fail entirely, two different ways") for the full handling.
   - Take the top 6-10 by this cheap score as the shortlist.
2. **Read the shortlist for real** — full `description_html`, AND `mcp__plane__list_work_item_comments` for every single shortlisted candidate, no exceptions (issues already read in Step 3 don't need re-reading). Skipping the comments call is a common way to produce a wrong rationale: a description can cite something (a bug, a blocker) that a later comment already resolved or marked out of scope. A description can be stale in a way only the comments reveal — do not treat "read the shortlist" as description-only. If you catch yourself about to present options without having called this for every one of the candidates you're about to present, stop and do it first. Also skim any project notes/memory you keep for this project — they often carry live context (an active initiative, a current deadline, a "this is the flagship feature" note) that changes what "makes sense next" means beyond raw priority. This step is what makes the recommendation actually good instead of a mechanical sort — use judgment, the same kind a competent engineer would use picking their own next task:
   - Concrete and well-scoped beats vague and open-ended ("fix this specific null check" beats "improve the UX, make sure it's good").
   - A correctness bug in something load-bearing outranks a cosmetic issue or a nice-to-have feature, all else equal.
   - An issue that unblocks several others (from the leverage check) outranks one that unblocks nothing.
   - **Favor issues with no human-intervention step on the critical path.** An issue you can carry start-to-finish yourself (code, config, docs, git/deploy work) outranks one whose plan requires a manual action partway through — a GUI click only the user can make, an external account/signup, physical/hardware access, or a decision only they can make — even at equal priority. Human-gated work stalls an autonomous session; when a candidate needs a human step, say so in its rationale rather than letting the user find out mid-work.
   - Live project context matters — if your notes say something is the active/current focus, work that touches it ranks higher than equally-priority-tagged work that doesn't.
   - Don't present near-duplicates (e.g. four cosmetic label-overlap bugs) if the shortlist has more variety than that — favor a set that gives the user a real choice.
3. Select up to 4 (fewer only if the merged pool genuinely has fewer than 4 legitimate candidates — don't pad with weak options just to hit 4; Step 5 covers what to do with the unused slot(s) instead). For each, write a **brief** rationale (1-2 sentences, concrete — cite something from the actual issue, not a generic "this seems important") explaining why it's a reasonable next pick, and how it compares to the others if relevant. For any option reclassified from Blocked in Step 3, explicitly note that in its rationale — don't bury that fact, the user should know their tracker is stale here.

## Step 5 — Present up to 4 options and get the user's pick

Use `AskUserQuestion` with the ranked candidates as options (label = `<ID>: <short title>`, description = the brief rationale). The tool always offers an "Other" fallback automatically, so the user can reject all of them without needing an extra one from you.

**If Step 4.3 produced fewer than 4 candidates, add one final option to stop the session** — label something like "Stop here for now", description stating plainly that the pool came up short (e.g. "Only 2 legitimate candidates right now — nothing else is worth padding the list with"). This makes "there's nothing good to pick up right now" a first-class choice instead of relying on the user to notice the list is short or reach for the generic "Other" fallback themselves. Never add this option when the pool already has 4 real candidates — don't burn a slot on it when there's real work to show.

Do not add editorializing beyond the per-option rationale — no "I'd go with the first one" unless explicitly asked. Up to four good options with honest tradeoffs (fewer plus the stop option, when the pool is thin) is the deliverable; the choice is the user's.

## Step 6 — Hand off

Once the user picks an issue (from the ranked options, or names something else via Other), begin work on it per your project's normal issue-start process (a dedicated start-issue skill if you have one, or setting it In Progress and planning manually otherwise). If they picked an issue that Step 3 identified as reclassified-from-Blocked, mention that starting it will move it out of Blocked as part of setting it In Progress — no separate state-fix step needed.

If the user picks the "Stop here for now" option, end the turn without starting any issue — this is a deliberate decision to end the session, not a decline-to-choose.

If the user declines to pick anything else (wants to keep browsing, or the Step 3 blocked-report was the actual answer they needed), stop here — don't force a selection.
