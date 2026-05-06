Update a rule or skill based on a mistake, repeated pattern, or better approach discovered during work.

Arguments: what went wrong or what pattern was found, desired correction, which rule/skill is affected (optional).

## When to use

- A mistake just happened that a rule could prevent
- A pattern appeared in 3+ places that should be a rule
- A better approach was found that contradicts current guidance
- An existing rule is ambiguous and caused the wrong behavior

## Steps

**1. Identify the rule to update**

- Is this a global behavior? → `~/.claude/CLAUDE.md` or `~/.claude/skills/`
- Is this project-specific? → `<project>/CLAUDE.md` or `<project>/.claude/skills/`
- Is this about a specific workflow? → the relevant skill file

**Before creating anything new**: check for an existing rule or memory entry that covers this topic. Prefer updating an existing file over creating a duplicate. Search for the relevant section in CLAUDE.md and skill files — prefer updating over adding.

**2. Two-pass diagnosis**

**Pass 1 — Verify**: Separate what Claude claimed or did from what evidence actually shows.
- What exactly did Claude do or claim? (quote the specific action or output — "agent ran a playbook without authorization" not "agent did something wrong")
- What do state files, command output, or user observations actually show?
- If they contradict: the rule is being ignored, not missing. Enforcement is the fix, not more text.

**Pass 2 — Classify the root cause**:
- **Missing rule**: scenario wasn't covered → add a new rule
- **Ambiguous rule**: guidance exists but was misread → rewrite for clarity
- **Ignored rule**: clear guidance wasn't followed → add NEVER/ALWAYS with explicit consequence, or restructure the skill to make compliance unavoidable (restatement alone won't fix this)
- **Wrong rule**: guidance was followed but was incorrect → update or remove the rule

**3. Propose the change**

- Draft the updated or new rule text — focused, short, imperative (NEVER/ALWAYS/ONLY/etc.)
- Show: current text (if updating) → proposed text
- Flag if this conflicts with any existing rule

**4. Apply**

- Edit the relevant CLAUDE.md or skill file
- Keep changes minimal — one focused addition or edit, not a rewrite
- Verify the updated file reads correctly in context

**5. Note the source**

Add a brief comment in any active issue noting what rule was updated and why. This creates a decision trail.
