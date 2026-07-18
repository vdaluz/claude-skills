---
name: whats-next
description: Show what's next for a Plane project across In Progress, Rolling, Todo, Backlog, and Blocked sections. Use when the user asks what's next, what to work on, or runs /whats-next.
---

Show what's next for a Plane project: In Progress → Rolling (due) → Todo → Backlog → Blocked.

Arguments: project identifier — optional; auto-detected from cwd if omitted, or ask the user. Optional filter/sort flags:

| Flag | Effect | Default |
|---|---|---|
| `--include-labels=<uuid,...>` | Keep only issues with at least one of these label UUIDs | (none — keep all) |
| `--exclude-labels=<uuid,...>` | Drop any issue with at least one of these label UUIDs | (none) |
| `--sort-by=priority\|target_date\|created_at\|updated_at` | Sort key within each section | `priority` |
| `--sort-order=asc\|desc` | Sort direction | `asc` |
| `--nulls=first\|last` | Null placement for date sorts | `last` |
| `--include-content` | Disable the default content filter below (show blog-draft/dev-log-style issues too) | off |

Unrecognized flags: error and stop.

## Default content filter

By default, if your project distinguishes content backlog (blog drafts, dev logs, etc.) from actionable engineering work via a label or title convention, exclude that content backlog from the output — it drowns the real engineering issues. Only show it when `--include-content` is passed or the user explicitly asks (e.g. "show blog drafts too"). Projects with no such convention: show everything, same as before.

When issues are excluded this way, do not silently drop them from the user's mental model — if the resulting section would otherwise be empty or very short, it's fine to note "(N content issues hidden, pass --include-content to show)" as a single factual line. This is not commentary or recommendation, just accounting for what was filtered.

## Step 1 — Resolve project

If you keep a cwd-to-project shortcut table, try it first. Otherwise ask which project, or resolve it via `mcp__plane__list_projects`.

Get the project ID and state UUIDs (In Progress, Rolling if your project uses one, Todo, Backlog, Blocked) — from a cached reference file if you keep one, or via `mcp__plane__list_states` otherwise.

## Step 2 — Fetch and partition issues

**Known tool bug:** do not pass `state_groups`, `priorities`, `label_ids`, or any filter param to `mcp__plane__list_work_items` — that routes through Plane's advanced-search endpoint, which can 403 depending on the API key's permissions. Call it with only `project_id`, `expand="state,labels"`, and `fields="id,sequence_id,name,priority,state,labels,target_date,created_at,updated_at"` — filter and sort yourself over the full result. If the trimmed result still exceeds the tool's output limit, it's auto-saved to a file — use `jq` rather than re-requesting with filters.

Partition by state name/group:
- **In Progress** (group `started`)
- **Rolling (due)** — only if your project has a dedicated recurring/rolling state, and only issues with `target_date` on or before today
- **Todo** (group `unstarted`)
- **Backlog** (group `backlog`)
- **Blocked** (a state literally named "Blocked", if the project has one)

Apply `--include-labels`/`--exclude-labels` and the default content filter (Step 1 above, unless `--include-content`) to every section. Sort each section by `--sort-by`/`--sort-order`/`--nulls`:

- **`--sort-by=priority`** (the default): rank by urgency, not alphabetically or by the raw string value. Map `urgent`→0, `high`→1, `medium`→2, `low`→3, `none`/unset→4, then sort by that rank. `asc` (the default) means urgent-first; `desc` means none/low-first.
- **`--sort-by=target_date|created_at|updated_at`**: sort by that field's actual value, `asc`/`desc` as given, with `--nulls` (default `last`) controlling where missing values land.

## Step 3 — Display

Show the In Progress, Rolling (due), Todo, Backlog, and Blocked sections, **capped at 20 issues total** across all sections combined. Fill from the top of each section in order (In Progress → Rolling → Todo → Backlog → Blocked) until the cap is reached. If a section is cut short, append a line like `… and N more` so the user knows there are additional items.

**In Progress always shows** — it is not affected by `--include-content` or any other flag, and is never omitted for brevity. It's the whole point of asking "what's next": knowing what's already started.

**Format (mandatory, no exceptions).** Every issue line must show at minimum `<ID> [priority] <title>` — a markdown table (`Issue | Pri | Title`) is the default. **A bare list of issue IDs (e.g. "PROJ-55, PROJ-48, PROJ-47") is never acceptable output, under any circumstance** — an ID alone carries no information; the entire point of this command is showing what the tickets *are*, not that they exist. This holds even when:
- the display is a short recap after closing an issue, not a full run of this skill
- the data came from an improvised fallback query rather than the standard path
- only 1-2 issues are being mentioned in passing — collapsing to bare IDs "since it's just a couple" is exactly the drift that causes this rule to erode over a long session
- **the same project's list was already shown in full earlier in this conversation, and this is a second (or later) recap** — e.g. after closing a second issue in the same session. "I already showed the table, I'll just recap the IDs this time" is the identical drift under a different excuse. Each display is independent and gets the full table, every time, with zero exceptions for redundancy.

If you don't have titles in hand (e.g. you only fetched IDs), fetch them before displaying — do not display IDs-only and call it done.

**Self-check before sending (mandatory).** Before sending any message that names 2+ issue IDs from this project, re-read your own draft: does every `<PROJECT>-<number>` appear on its own table row or list line with a title next to it? If any ID appears bare — in a sentence, a parenthetical, or a comma-separated run — stop and reformat into a table before sending. Do this check even when the IDs are just part of a closing summary, not the "real" whats-next display.

The **Rolling (due)** section appears only when at least one rolling issue has a `target_date` on or before today. Rolling issues never close — after completing one, bump its `target_date` to the next occurrence.

**Do not** add any commentary, recommendation, prioritization, or opinion about which issue to work on next, what stands out, or what to do. Just the list. If the user wants an opinion, they will ask for it explicitly — that's a different skill's job (see `pick-next-issue` if you have it installed).

## Step 4 — Done

No further steps.
