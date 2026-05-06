Produce a concrete implementation plan without making any changes.

Arguments: task description, files/areas involved (if known).

## Research first

Before planning, read: relevant state files, existing configs, runbooks, CLAUDE.md. If research requires web search or community references, do it and cite sources. Plans must be grounded — no "I assume X is configured" steps.

## Plan format

For each step include:
- **What**: the specific action (edit file X, run playbook Y, add entry to Z)
- **Where**: exact file path or command
- **Why**: the decision rationale if non-obvious
- **Verify**: how to confirm this step succeeded before moving to the next

Also include:
- **Prerequisites**: what must be true/done before starting
- **Risks and unknowns**: anything that could go wrong or needs investigation
- **Rollback**: how to undo if something breaks (where applicable)

## Constraints

- Implementation tasks only — no "research X" or "confirm Y" steps in the plan (do that now, before planning).
- No placeholders or "TBD" — if you don't know something, research it or flag it as a blocker before presenting the plan.
- Do not edit files, run commands, or make any changes.

Present the plan and wait for the user to say "go" or give feedback.
