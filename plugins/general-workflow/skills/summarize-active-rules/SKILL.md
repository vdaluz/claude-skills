Summarize which rules and skills are active in the current context.

Arguments: current file(s), task, or area of work (optional).

## Steps

1. **Identify active rule files**: Read all CLAUDE.md files in scope:
   - `~/.claude/CLAUDE.md` (always active — global rules)
   - `<project>/CLAUDE.md` (active if working in that project)
   - Workspace-level CLAUDE.md if present

2. **Identify available skills**: List `.claude/skills/` files in scope:
   - `~/.claude/skills/` (always available)
   - `<project>/.claude/skills/` (available in that project)

3. **For each active rule file**, summarize:
   - Which sections apply to the current task/context
   - Top 3–5 constraints most relevant right now
   - Any rules that might conflict or surprise

4. **For available skills**, list:
   - Skill name and trigger phrase
   - One-line description of what it does

5. **Flag gaps**: Note if any expected rules seem missing or if the current task touches an area with no explicit guidance.

Output as a structured list. Keep it scannable — this is a diagnostic tool.
