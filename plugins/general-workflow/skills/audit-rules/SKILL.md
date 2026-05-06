---
name: audit-rules
description: Audit CLAUDE.md files and skills across repos for redundancy, conflicts, and promotion candidates. Produces a report — no edits made automatically.
---

Audit CLAUDE.md files and skills across your repos. Identifies redundancy, inconsistencies, and promotion candidates. Produces a report — no edits are made automatically.

## When to use

Run when:
- Adding a new repo to your workflow
- After significant CLAUDE.md changes in any repo
- Periodically to catch drift and redundancy

Trigger: `/audit-rules`

---

## Steps

### 1. Discover repos

Find repos to audit:

```bash
find ~/Repos -maxdepth 2 -name "CLAUDE.md" | sort
```

Review the list and remove any repos the user doesn't want audited (ask if unclear).

### 2. Read global rules

Read both files in full:
- `~/.claude/CLAUDE.md` — global (applies everywhere)
- `~/Repos/CLAUDE.md` — workspace level, if it exists (applies to all ~/Repos projects)

Note the major sections in each so you can reference them by name in the report.

### 3. Catalog global skills

`ls ~/.claude/skills/` — list what's available globally. Note what each skill does (read its first 5 lines if the name isn't self-explanatory).

### 4. For each discovered repo

- Read `<path>/CLAUDE.md` in full
- Check for `<path>/.claude/skills/` — if it exists, list the skill directories and read each skill's SKILL.md first paragraph

### 5. Analyze and report

Produce a structured report with these five categories. Use judgment throughout — frequency is a weak signal. Ask: "Would this rule apply equally well in every project, or is it intentionally scoped?"

---

#### Category 1: Redundant rules

Rules in a project or workspace CLAUDE.md that are already covered at a higher level — identical or semantically equivalent.

These create divergence risk: when the global rule changes, the copy in the project won't.

**Flag as:**
```
[REDUNDANT] <project>: "<rule excerpt>"
→ Already covered in <global/workspace> CLAUDE.md under "<section name>"
→ Action: remove from project CLAUDE.md, rely on global
```

---

#### Category 2: Promotion candidates

Rules or patterns in 2+ project CLAUDE.md files that are NOT in global CLAUDE.md and appear genuinely universal.

**Use this judgment heuristic:**
- PROMOTE if: the rule would be correct and useful in *every* project, regardless of stack or type
- KEEP PROJECT-LOCAL if: the rule is specific to that stack, workflow, or intentional per-project exception

Examples of intentional per-project duplication that should NOT be promoted:
- "No worktrees" — this is a project-level decision, not a universal rule
- Issue tracker state UUIDs — project-specific identifiers
- Stack-specific commands (`bin/dev`, `npm run build`) — already in the workspace CLAUDE.md at the right level

**Flag as:**
```
[PROMOTE?] "<rule excerpt>"
→ Found in: <project list>
→ Rationale: <why this would apply everywhere>
→ Already in global? No
→ Suggested home: ~/.claude/CLAUDE.md under "<section>"
```

Or:
```
[PROJECT-SPECIFIC — OK] "<rule excerpt>"
→ Found in: <project list>
→ Intentional: <brief reason it's correctly scoped>
```

---

#### Category 3: Conflicts

Rules that contradict each other across projects, where neither appears intentionally project-specific.

**Flag as:**
```
[CONFLICT] "<topic>"
→ <project A>: "<rule>"
→ <project B>: "<rule>"
→ Needs reconciliation: propose which is correct and where it should live
```

---

#### Category 4: Skills assessment

Evaluate the split between global and project-local skills:

**Global skills that may be too project-specific:**
- A global skill that only makes sense in one project
- Flag: `[CONSIDER MOVING] <skill> → <repo>/.claude/skills/`

**Project-local skills that may deserve promotion:**
- A skill in a project's `.claude/skills/` that would be useful across repos
- Flag: `[PROMOTE SKILL?] <repo>/<skill> — useful because: <reason>`

---

#### Category 5: Missing coverage

Patterns you observe in 3+ project CLAUDE.md files that don't exist at any level. These are candidates for the global CLAUDE.md.

Also flag: things you'd expect to exist globally but don't (e.g., no rule about API key handling, no rule about `.env` files).

**Flag as:**
```
[MISSING GLOBALLY] "<topic>"
→ Seen in: <project list>
→ Current state: handled inconsistently / not handled
→ Proposed global rule: "<draft rule>"
```

---

### 6. Output

Post the report as a comment on the current active issue (if one is open), or output in chat if no issue is active. Do NOT edit any CLAUDE.md files.

Use this report header:
```
## Cross-repo rules/skills audit — <YYYY-MM-DD>

Repos audited: <list>
Global CLAUDE.md: ~/.claude/CLAUDE.md
Global skills: ~/.claude/skills/ (<N> skills)

### 1. Redundant rules (N)
...

### 2. Promotion candidates (N)
...

### 3. Conflicts (N)
...

### 4. Skills assessment
...

### 5. Missing coverage (N)
...

### Summary
One paragraph: overall health of the rule hierarchy, top 1-2 priority actions.
```

The report is advisory. The user decides what to change.
