---
name: review-to-issues
description: File the user-approved findings from a project-review run (.review/<run>/findings.md) as Plane issues - deduplicated against open issues, one issue per root cause, Backlog state, never without explicit approval.
argument-hint: "[project] [findings-path] [selection]"
disable-model-invocation: true
---

Turn approved findings from a project review into Plane issues.

Arguments: Plane project identifier (e.g. PROJ); path to `findings.md` (omit to use the newest `.review/*/findings.md` in the current repo); selection (`all`, ids like `C1,C3,D2`, or omit to be asked).

## Steps

1. Read `findings.md`. If it is missing or has no findings, stop and say so - do not reconstruct findings from chat history or from the `judged/` files, which contain unverified candidates.
2. Resolve the project and its Backlog state UUID per `${CLAUDE_PLUGIN_ROOT}/skills/_shared/plane-project-resolve.md`. An empty state list means the wrong project was resolved - stop, do not create states.
3. **Dedupe against the tracker.** Load open issues via `mcp__plane__list_work_items` (see `${CLAUDE_PLUGIN_ROOT}/skills/_shared/plane-mcp-gotchas.md` before passing filters). For each finding, compare by root cause, not title wording - same file or component plus same problem is a duplicate even if phrased differently. Classify each finding: `new`, `duplicate of PROJ-123` (skip), or `extends PROJ-123` (the existing issue is real but lacks this evidence - propose a comment on it instead of a new issue).
4. **Group.** Findings that would be fixed by one change become one issue listing each as a checklist item. Never one issue per instance of a pattern.
5. **STOP. Present the full proposal before creating anything:** a numbered list - finding id(s), proposed title, priority, effort, `new` / `extends` / `duplicate (skipped)`. Ask for approval in plain text. Accept `all`, a list of numbers or ids, edits to titles or priorities, and "drop N". Re-present after any edit. Do not proceed without an explicit reply.
6. After approval, ensure a `review` label exists (`mcp__plane__list_labels`, else `mcp__plane__create_label`, color `#6366F1`). Create each approved issue with `mcp__plane__create_work_item` directly (UUIDs already resolved - do not re-invoke **create-issue** per issue):
   - `name`: the finding title, following any title convention the project documents.
   - `priority`: critical -> `urgent`, high -> `high`, medium -> `medium`, low -> `low`. Never unset.
   - `state`: Backlog. `labels`: `review`, plus any project-required labels.
   - `description_html`: real HTML (Plane drops plain text) with these sections - **Problem**, **Evidence** (the `path:line` list or evidence file names, verbatim from the finding), **Impact**, **Proposed fix**, **Acceptance criteria** (as a checklist), and a last line: `Source: project review <run dir name>, finding <id>, confidence <n>, effort <S|M|L>`.
   - Screenshots live in a gitignored directory - name the file in the description; attach it to the issue only if the user asks.
   For `extends` items, post the evidence as a comment on the existing issue instead.
7. **Record declined findings.** Append every finding the user dropped or did not select to `.review/rejected.md` - one line each: date, finding id, title, and the user's reason if they gave one. The next project-review run reads this file as do-not-report, so a declined finding is not proposed again.
8. Output a summary: created (issue id, title, priority), commented, skipped as duplicate, declined.

## Rules

- **Never create or comment on any issue without explicit approval of the presented list (step 5).**
- File only what is in `findings.md`. Do not add findings of your own, and do not raise a finding's severity while filing.
- If a finding clearly belongs to another project (infrastructure, a shared library), say so in the proposal and ask - do not file it in the wrong project.
- A review that produced three findings files three issues or fewer. There is no minimum.
