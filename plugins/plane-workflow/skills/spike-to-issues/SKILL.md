---
name: spike-to-issues
description: Convert a completed spike's findings into concrete implementation issues in Plane. Use when the user wants to "turn spike findings into issues", "convert this spike", or after closing out a spike that has a findings comment. Requires a spike that is Done or has findings already posted — not for spikes still in progress.
---

Convert the findings from a completed spike issue into actionable implementation issues.

Arguments: spike issue ID (e.g. BLG-3). Must be a spike that is either Done or has a findings comment posted.

## When to use

Run this after closing out a spike, or any time a spike has documented findings and the implementation issues haven't been created yet. This is the bridge between research and build.

## Steps

1. Load the spike issue via `mcp__plane__retrieve_work_item_by_identifier`. Confirm it is a spike (title starts with "Spike:" or has a "spike" label). If not, stop and tell the user.
2. Load all comments via `mcp__plane__list_work_item_comments`. The findings comment is the source of truth — read it carefully. If no findings comment exists, tell the user the spike isn't ready to convert yet.
3. Check for existing issues in the project via `mcp__plane__list_work_items` to avoid duplicates. Note any issues already blocked by this spike.
4. Based on the findings, determine what implementation issues to create:
   - If the spike concluded "this API supports X" → create or update the feature issue that was blocked, adding concrete implementation details from the findings to its description.
   - If the spike concluded "this API does NOT support X" → create a new issue for the fallback approach (describe the fallback clearly; reference the spike and why the original plan changed).
   - If the spike concluded "blocked / impossible" → create an issue to discuss/decide an alternative, or flag to the user if there's no clear path forward.
   - If the spike produced a decision (e.g. "use fine-grained PAT, not GitHub App") → update the description of the relevant existing implementation issue with that decision. Do not create a new issue just to record a decision.
5. **STOP. Present the full proposed issue list before creating anything.** Format as a numbered list with title, priority, and one-line summary for each new issue; separately list any existing issues that will be updated. Do not proceed until the user explicitly approves (e.g. "go", "create them", "looks good"). If the user asks to modify or drop an issue, update the list and re-present before creating.
6. After confirmation:
   - Use the **create-issue** skill for any new issues.
   - For existing issues that need description updates, use `mcp__plane__update_work_item`.
   - Remove the "blocked by spike" note from any issues that are now unblocked.
7. Post a comment on the spike issue linking to the newly created/updated issues (e.g. "Findings converted to BLG-12, BLG-13. BLG-8 unblocked and updated.").
8. Output a summary: what was created, what was updated, what is now unblocked.

## Rules

- **NEVER create any issue without explicit user approval of the full proposed list (step 5).** Presenting the list and proceeding without a response is not allowed.
- Do not create implementation issues for findings that are already covered by existing issues — update those instead.
- If findings contradict the PRD (e.g. an API doesn't work as assumed), flag this explicitly. The PRD may need updating.
- Never create a new spike to follow up a spike unless the original spike surfaced a genuinely new unknown. A new unknown is fair game; "we need to research more of the same thing" is a planning failure.
- If the spike found that a feature is infeasible, do not silently drop the feature — create an issue titled "Decision: [feature] approach" so the trade-off is tracked.
