---
name: prd-to-issues
description: Parse a PRD and create Plane issues from it, one per spike and one per feature area.
disable-model-invocation: true
---

Parse a PRD and create a structured set of Plane issues from it.

Arguments: PRD file path (or omit to search the current project for `docs/prd.md`), Plane project identifier (e.g. BLG).

## Issue granularity rules

Do NOT create one issue per functional requirement — that's too granular. Instead:

- **One issue per spike** — spikes are discrete investigation tasks with clear done criteria. Prefix the title with `Spike:`.
- **One issue per feature area** — group related FRs under a single issue (e.g. all Post Scanning FRs become one "Post Scanning" issue). List the relevant FR numbers in the description.
- **One setup issue** — if the PRD implies a fresh project (new Rails app, new repo, etc.), create a single "Initial project setup" issue covering scaffolding, auth, and dev environment.
- **One deployment issue** — if the PRD mentions deployment or infrastructure, create a single issue for it (e.g. "Provision container and deploy to production"). If it clearly belongs to a different, infrastructure-specific project, note that in the final summary rather than creating it there directly — see the Rules section below.
- **Skip**: non-goals, NFRs, open questions. These are not actionable issues. Surface open questions as a comment on the last created issue instead.

## Steps

1. Read the PRD file. If no path is given, look for `docs/prd.md` in the current working directory.
2. Call `mcp__plane__list_projects` to get the project UUID for the given identifier.
3. Call `mcp__plane__list_states` for the project. Plane projects always ship with a default state set — an empty result means the wrong project UUID was resolved, or an API error, not a genuinely stateless project. Stop and report the error rather than creating a fresh state set, which would write junk states into whatever project was actually resolved. All issues must be created with a state — use Backlog.
4. Check if a "spike" label exists in the project via `mcp__plane__list_labels`. If not, create one with `mcp__plane__create_label` (color: `#F59E0B`).
5. Plan the full issue list before creating anything. Output it to the user as a numbered list (title + one-line scope summary) and wait for confirmation or edits.
6. After confirmation, create each issue by calling `mcp__plane__create_work_item` directly with the project UUID and Backlog state UUID already resolved in steps 2-3 - apply **create-issue**'s step 4 priority-inference rules per issue rather than re-invoking that skill, which would re-resolve the same UUIDs on every call. For spikes, apply the spike label from step 4. For feature-area issues, include the relevant FR numbers in the description.
7. Create issues in this order: setup first, spikes second (they're often blockers), feature areas last.
8. After all issues are created, output a summary table: issue ID, title, and any blocker relationships noted in the PRD.

## Description format for feature-area issues

Each feature-area issue description should include:
- One sentence summarising the feature.
- A checklist of the relevant FRs (e.g. `- [ ] FR-04: scan src/content/blog/*.md ...`).
- Any spike blockers called out in the PRD (e.g. "Blocked by BLG-SPIKE-02").

## Rules

- Never create issues for things the PRD explicitly marks as out of scope or non-goals.
- If the PRD has open questions, add them as a comment on the last created issue — do not create issues for unresolved questions.
- If an issue clearly belongs to another project (e.g. a deployment task), note it in the summary but do not create it in the wrong project. Ask the user if they want it created in the other project too.
- Do not create duplicate issues. Before creating, check existing issues via `mcp__plane__list_work_items` for obvious overlaps.
