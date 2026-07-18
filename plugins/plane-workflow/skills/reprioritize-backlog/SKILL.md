---
name: reprioritize-backlog
description: Reorder a Plane project's Backlog (and optionally Todo) by urgency and dependency — issues blocked by open work sort after their blockers, issues that unblock the most work rank higher, ties broken by reading each tied issue's content (not just falling back to age). Proposes the new order and any priority mismatches, applies only after explicit confirmation. Use when the user asks to reprioritize, reorder, triage, or groom a backlog.
---

Reorder a Plane project's Backlog by urgency and dependency, then apply the new order (and any flagged priority changes) only after explicit approval. Works on any Plane project — no per-project hardcoding required.

Arguments: project identifier — optional; auto-detected from cwd if omitted, or ask the user. Optional: `--include-todo` (fold Todo into the same pass; default is Backlog only), `--limit N` (only compute/apply to the top N issues by current `sort_order`, for very large backlogs).

## Step 1 — Resolve project and scope

If you keep a cwd-to-project shortcut table, try it first. Otherwise ask which project, or resolve it via `mcp__plane__list_projects`.

Get the project ID and the Backlog (and Todo, if `--include-todo`) state UUIDs — from a cached reference file if you keep one, or via `mcp__plane__list_states` otherwise.

If your project uses a label or title convention to separate content backlog (blog drafts, dev logs, etc.) from actionable engineering work — the same one you'd use to filter a "what's next" listing — apply it here too, so content-backlog issues don't get mixed into an engineering reprioritization pass. Projects without that kind of convention: no filter, include everything.

## Step 2 — Fetch issues in scope

**Do not pass `state_groups`, `priorities`, `label_ids`, or any other filter param to `mcp__plane__list_work_items`** — any of those can route the call through Plane's advanced-search endpoint, which can 403 depending on the API key's permissions. Call it with only `project_id`, `expand="state,labels"`, and `fields="id,sequence_id,name,priority,state,labels,target_date,created_at,sort_order"` — `fields`/`expand` alone stay on the working standard-list endpoint and also keep the payload small. Filter to the Backlog state UUID (and Todo's, if `--include-todo`) yourself over the full result. If the project is large enough that even the trimmed-fields result exceeds the tool's output limit, the result is auto-saved to a file — use `jq` on it (`select(.state == "<backlog-uuid>")`) rather than re-requesting with filters.

Apply the content-filter labels from Step 1 and `--limit` (by current `sort_order` ascending) after filtering to scope.

**The Backlog/Todo filter must be an inclusion match** (`state == <Backlog UUID>`, or `== <Todo UUID>` with `--include-todo`) — never an exclusion match (e.g. "state not in {Done, Cancelled}"). An exclusion-style filter lets a Cancelled or Done issue slip into scope on any state-UUID typo or stale cache entry; an inclusion filter can't accidentally admit them. If any in-scope issue's state group is `completed` or `cancelled` after this filter, that is a bug in this step, not a data problem to "fix" — stop and report it rather than proceeding.

If the scoped list is empty, say so and stop.

## Step 3 — Fetch dependency edges

For every issue in scope, call `mcp__plane__list_work_item_relations(project_id, work_item_id)` and keep the `blocked_by` and `blocking` lists.

**Known tool bug:** this call can throw a pydantic validation error (`Input should be a valid string ... input_type=dict`) whenever an issue actually *has* a populated relation — it may only work fine (returns empty lists) when there are none. If you hit this and can't find a working fallback in your Plane MCP server's docs, the safe handling is:
- On success (no error): use the returned `blocked_by`/`blocking` lists normally.
- On this validation error: the issue has at least one relation the tool can't parse. Do **not** crash the run or guess at the edge from the truncated error text. Treat the issue as having no *known* edges for graph purposes (don't let it be promoted by an unverifiable "blocks N" count, and don't demote it either), and flag it explicitly in the Step 6 output: `"<ID>: has a relation the API client can't parse (known tool bug) — position not dependency-aware, verify manually."`

For every distinct related item that *is* resolved, get its current state group from the relation response, or via `mcp__plane__retrieve_work_item` if not included. An issue only counts as a **live blocker** if its state group is not `completed` or `cancelled` — a blocker that's Done or Cancelled no longer constrains order.

Build a directed graph: live-blocker → blocked, restricted to edges where the blocked issue is in scope. An in-scope issue blocked by something *outside* scope (a different project, or a not-yet-fetched state) still counts as blocked for layering purposes — note it, but it can't be reordered relative to that external item.

**Cycle check:** if two or more in-scope issues block each other (directly or transitively), that's a data problem, not something to silently resolve. Report the cycle plainly by issue ID and treat its members as unconstrained by each other (fall through to the Step 4 urgency tie-break for them).

## Step 4 — Compute the proposed order

**Priority must not be the primary sort key.** If stored `priority` dominates the ordering and dependency leverage only breaks ties *within* a priority tier, a `low`-labeled issue blocking five others can never outrank a `medium` issue blocking nothing — dependency becomes decorative, and the whole exercise degenerates into "sort by the label a human typed in once at creation time," which Plane's UI already does natively. That defeats the point of a *dependency-aware* reprioritization. Score them together instead:

1. **Topological layers** over the dependency graph (Kahn's algorithm): layer 0 = issues with no live in-scope blocker; layer 1 = issues whose blockers are all resolved by layer 0; and so on. This is the one hard constraint — a blocked issue never outranks its own open blocker, no matter its score.
2. **Priority weight**: `urgent`=4, `high`=3, `medium`=2, `low`=1, `none`=0.
3. **Within each layer**, compute one composite score per issue: `own priority weight + sum of priority weights of every live in-scope issue it directly blocks`. This is what makes dependency genuinely *count*: an issue that unblocks one `urgent` issue (weight 4) outscores a `medium` issue (weight 2) that unblocks nothing, even though its own label is lower. Sort the layer by this score, descending.
4. **Tie-break** (score still equal): **do not fall straight to age.** A 3+-way tie on composite score is not a rare edge case — it's the normal outcome whenever priority labels are mostly uniform (a backlog where everything got triaged as `low`) and no Plane relations are recorded (most projects don't use them), which is common. Falling straight to age in that case makes the entire pass a no-op relabeled as analysis: the output is just "current creation order," dressed up as a reprioritization. Read each tied issue's actual `description_html` (not just the title — a title alone is not enough to judge this) and rank by content judgment: concrete and well-scoped with a clear next action beats a vague one-liner with no detail; an issue whose own description says it's explicitly gated, parked, or blocked on an unmet prerequisite ("build when X exists", "activate ~60 days before Y") sorts to the **bottom** of its tier regardless of age — it is not a real candidate for backlog priority no matter how long it's been sitting there, being old doesn't make it more actionable. Only fall back to `created_at` (older first), then `target_date` if set (soonest first), for issues that remain genuinely indistinguishable after that read — e.g. two equally-detailed, equally-actionable items, or a batch of equally-vague one-line TODOs from the same import with nothing to differentiate them content-wise.
5. Concatenate the layers in order. This is the proposed new Backlog order.

Note in the Step 6 output when an issue's rank was pulled up primarily by leverage rather than its own priority label — that's the signal worth surfacing, not just the final position. Note it the same way when judgment (not score) determined relative order within a tied group — state the actual reason ("concrete migration plan vs. an undetailed idea note", "self-declared gated, sorted last despite being oldest"), not just "tied, judgment call."

## Step 5 — Flag priority mismatches (informational only)

Check two distinct things here, not just one — they catch different failure modes:

1. **Score vs stored priority.** Flag issues where the stored `priority` looks stale next to the Step 4 composite score — e.g. its computed score lands it in the top quarter of the list but it's labeled `low`, or it's labeled `urgent`/`high` with a composite score at the bottom (no live blockers, nothing depending on it, and old).

2. **Uniform-priority blindness.** Check #1 is structurally blind whenever a large share of in-scope issues (roughly a third or more) already share one stored priority — the composite score is partly *derived from* that same stored value, so a stale-but-uniform label can never produce a mismatch by comparison alone. Reordering the pile without ever revisiting the label just leaves every issue's `priority` field saying "these are all equally urgent" forever, which quietly breaks any other tooling that reads `priority` as a signal (a "what's next" listing, a next-issue picker) — they'll keep treating a fully-scoped, low-effort, live bug fix as identical in urgency to an undetailed one-line idea note, because nothing ever told Plane otherwise. When this condition is met, **actively derive priority suggestions from the same Step 4 content-judgment tiers used for ordering** — don't stop at reordering and call the job done. For each tier: content that's concrete, well-scoped, and has a clear next action generally deserves a priority visibly above vague undifferentiated notes, which in turn generally deserves a priority at or above anything the issue's own description says is gated/parked/blocked-on-a-prerequisite. State an actual proposed value per issue or per tier, not just a description of the imbalance — e.g. "PROJ-298, PROJ-243, PROJ-275: propose low → medium, each is concrete/actionable/low-effort and currently indistinguishable in the tracker from a one-line idea note that will never get picked up otherwise."

List each suggestion with a one-line reason tied to the actual score or tier, not a vague "seems off." **Do not change `priority` unless the user explicitly approves a specific bump in Step 6** — this is a suggestion, not part of the reorder.

## Step 6 — Present and get explicit approval (hard gate)

Show in chat:
- The proposed order as a table: `# | Issue | Priority | Title | Why moved`. "Why moved" only needs to be filled for issues whose rank changed meaningfully — state the score composition when leverage did the work (e.g. "score 6: medium (2) + unblocks 1 urgent issue (4)"), not just a restated label. Other reasons: "blocked by PROJ-40 (open)", "oldest at its score, tied". Unchanged-position issues can just show their slot.
- Any detected cycles, plainly.
- Any priority-mismatch suggestions from Step 5.

This reorders and potentially reprioritizes shared Plane state visible to anyone looking at the project — **never apply it without an explicit go-ahead.** Ask: "Apply this order? Reply 'go' to apply as-is, tell me which priority bumps to include, or adjust specific issues first." An implicit or assumed yes does not satisfy this gate; wait for an actual reply.

## Step 7 — Apply (only after approval)

- **Order**: `mcp__plane__update_work_item` per issue, setting `sort_order` to strictly increasing values spaced 10000 apart (10000, 20000, 30000…) in the new rank order — wide spacing leaves room for manual drag-adjustments later without a full renumber. Skip any issue whose rank didn't change.
- **Priority bumps**: only for issues the user explicitly approved in Step 6, via `priority` on the same call.
- **Never pass or change `state`, for any issue, under any circumstance.** This skill only ever writes `sort_order` and, with explicit per-issue approval, `priority` — `update_work_item` calls that omit `state` should leave the existing state untouched (verify this against your own Plane MCP server if you're unsure). If an issue's state looks surprising or inconsistent with its content mid-run, stop and flag it in chat instead of silently correcting it.

## Step 8 — Confirm

Show the final order back to the user in the same table format as Step 6 so they can see what actually landed in Plane — a bare "done" is not sufficient. Note how many issues were reordered and how many priorities were changed.
